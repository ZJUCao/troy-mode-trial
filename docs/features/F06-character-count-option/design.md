---
troy-doc: "F06-design"
lang: "en"
version: "1.0"
updated: "2026-11-23"
status: "Approved by Troy on 2026-11-23"
mirror: "design.zh-CN.md"
---

# F06 Character count option: interface design

## 1. Feature

- ID and name: F06 Character count option
- Requirement: [docs/requirements.md](../../requirements.md#4-features)
- Hard dependencies: F04
- Soft dependencies: None

## 2. Interfaces

F06 changes the two interfaces of F04 in the module cli and adds one interface to the module counting. Section 2.1 is the command that Troy types, which gains the option `--chars`. Section 2.2 is the function behind it. Section 2.3 is the new library function `count_chars`, which counts the characters of a file and which `main` calls for `--chars`.

The counting itself is in counting, not in cli, for three reasons. Architecture section 3 says that cli reads the arguments and calls counting, and that counting counts. counting already holds the file rules that `--chars` must share with `wordcount FILE`: one byte order mark at the start is skipped (requirements Q5, Q12), and a missing file or a file that is not valid UTF-8 raises Python's own exception (Q4). And requirements Q6 settled the same question for lines: counting lines is counting, and it fits counting with no architecture change. Counting characters is counting too.

Three points in section 2.1 are proposals that Troy accepts or changes. Each one says so where it stands: the usage line shows the option, a shortened option name is a wrong command line, and the option may come after the file.

### 2.1 `wordcount`

- Module: cli. The console script `wordcount = "troy_mode_trial.cli:main"` in `pyproject.toml` stays as F04 declared it.
- Purpose: Prints the number of words in one UTF-8 text file, as in F04, or, with `--chars`, the number of characters of its decoded text, line ends included, so that Troy can count characters in PowerShell without writing Python.

Signature:

```text
usage: wordcount [--chars] FILE
```

Parameters:

| Name | Type | Meaning | Constraints |
| --- | --- | --- | --- |
| `--chars` | Option, a flag with no value | Print the number of characters of `FILE` instead of its words. Without it, the command prints the words, exactly as F04 does. | Optional. Only the full name `--chars`. There is no short form, such as `-c` (requirements Q10). A shortened name, such as `--char` or `--ch`, is a wrong command line (proposal 2 below). The option may come before or after `FILE`: `wordcount --chars notes.txt` and `wordcount notes.txt --chars` do the same (proposal 3 below). Given twice, as in `wordcount --chars --chars notes.txt`, it counts characters once, as given once. `--chars=VALUE` is a wrong command line. |
| `FILE` | One command-line argument | The path of the file to count, absolute or relative to the current working directory. | As in F04 design 2.1: exactly one argument, naming one existing, readable, regular file whose content is valid UTF-8. A path that starts with `-` follows `--`, for example `wordcount --chars -- -notes.txt`. After `--`, the text `--chars` is a file name, not the option. |

The command still has no `-h` or `--help`, and no option other than `--chars` until F05 adds `--lines` (requirements section 8).

**Proposal 1, the usage line, for Troy to accept or change.** The usage line shows the option: `usage: wordcount [--chars] FILE`, instead of F04's `usage: wordcount FILE`. The command has no help, so the usage line is the only place where the command itself names its option. The other choice keeps F04's line, so the option is not shown anywhere. With the proposal, F04's tests that check the usage line word for word change their expected line, as section 3 lists.

**Proposal 2, shortened option names, for Troy to accept or change.** Only the exact `--chars` is the option. `wordcount --char notes.txt` and `wordcount --ch notes.txt` are wrong command lines: a usage error with `wordcount: error: unrecognized arguments: --char`, and exit code 2. Without this rule, argparse would take any unique start of an option's name, such as `--c`, as the option. The proposal keeps a command line meaning only what Troy wrote, and keeps `--lines` and `--chars` from depending on which shortened names happen to be unique.

**Proposal 3, the option after the file, for Troy to accept or change.** `wordcount notes.txt --chars` counts characters, as `wordcount --chars notes.txt` does. This is how argparse reads a command line, and how many commands work. The other choice would make it a usage error, which needs extra code and gives Troy an error for a command line whose meaning is clear.

- Return value: exit code 0 on success. Standard output holds the count as a decimal number with no sign, padding, or separator, followed by one line break, and standard error stays empty, as in F04 design 2.1.
  - Without `--chars`, the count is what `count_words(FILE)` returns, as in F04.
  - With `--chars`, the count is what `count_chars(FILE)` returns (section 2.3): the number of Unicode code points of the file's text after UTF-8 decoding, with one byte order mark at the start of the file removed. Every line end counts as the file holds it: `\n` is one character, `\r` is one, and `\r\n` is two (requirements Q11). So `你` is one character, although it is three bytes, and the same file gives the same count on Windows and on Linux.

Errors:

Every error leaves standard output empty and writes to standard error only. A file error with `--chars` gives exactly the message and exit code that `wordcount FILE` gives for the same file (requirements F06 and Q8): one line `wordcount: <FILE>: <reason>`, followed by one line break, and exit code 2. `<FILE>` and the five reason texts are those of F04 design 2.1, unchanged.

| Error | When |
| --- | --- |
| Exit code 2, reason `no such file` | As in F04 design 2.1: no file or folder exists at `FILE`, `FILE` is the empty string, or a folder in the path is missing or is a file. |
| Exit code 2, reason `is a folder` | As in F04 design 2.1: `FILE` names a folder. |
| Exit code 2, reason `permission denied` | As in F04 design 2.1: the process may not read the file. |
| Exit code 2, reason `not valid UTF-8` | As in F04 design 2.1: the file content is not valid UTF-8. With `--chars`, the command checks the whole file, so a file whose invalid bytes come after valid text is still this error, and no count is printed. |
| Exit code 2, reason `cannot read file` | As in F04 design 2.1: any other `OSError` while the file is opened or read. |
| Exit code 2, usage line | The command line holds no `FILE`, more than one argument, an option other than `--chars`, a shortened option such as `--char`, `-c`, `-h`, or `--chars=VALUE`. argparse writes the usage line of proposal 1, `usage: wordcount [--chars] FILE`, and then one line `wordcount: error: <message>` in argparse's own words, for example `wordcount: error: the following arguments are required: FILE` for `wordcount --chars`, or `wordcount: error: unrecognized arguments: -c` for `wordcount -c notes.txt`. |

Any other exception is a bug, as in F04: Python writes the traceback to standard error and exits with code 1 (architecture section 6).

Two counting options in one command, such as `wordcount --lines --chars FILE`, are a usage error with exit code 2 (requirements Q13). F06 alone has no second counting option, so `--lines` is simply an unknown option until F05 adds it. To make Q13 hold without a change to `--chars`, `--chars` is the first member of a set of counting options that exclude each other: an option that a later feature adds to the set, such as F05's `--lines`, gives a usage error when it comes with `--chars`. F05's design fixes the usage line and the message for that case.

- Side effects: As in F04 design 2.1: the command opens `FILE` for reading and closes it before it exits, writes only to standard output and standard error, and writes, sends, and stores nothing. The option exists only after the project is installed again once F06 lands, for example with `uv pip install -e . --no-deps`.
- Performance target: None

Example:

`notes.txt` in the current folder is UTF-8 and holds the two lines `Hello world` and `  troy-mode  trial`, each ending with `\n`. `hello.txt` holds the one line `你好`, ending with `\r\n`: 8 bytes, but 4 characters. `latin1.txt` holds `café au lait` in Latin-1.

```text
PS> wordcount --chars notes.txt
31
PS> wordcount notes.txt --chars
31
PS> wordcount notes.txt
4
PS> wordcount --chars hello.txt
4
PS> wordcount --chars missing.txt
wordcount: missing.txt: no such file
PS> $LASTEXITCODE
2
PS> wordcount --chars latin1.txt
wordcount: latin1.txt: not valid UTF-8
PS> $LASTEXITCODE
2
PS> wordcount --char notes.txt
usage: wordcount [--chars] FILE
wordcount: error: unrecognized arguments: --char
PS> $LASTEXITCODE
2
```

### 2.2 `main`

- Module: cli, in `src/troy_mode_trial/cli.py`, as in F04 design 2.2. Tests import it as `from troy_mode_trial.cli import main`.
- Purpose: Runs the `wordcount` command of section 2.1 once: reads the arguments, counts the words of the file through `count_words`, or its characters through `count_chars` when the arguments hold `--chars`, writes the result or the error, and returns the exit code. It imports both functions from the package `troy_mode_trial`, never from `troy_mode_trial.counting` (architecture section 4).

Signature:

```python
def main(argv: Sequence[str] | None = None) -> int:
```

The signature does not change. `Sequence` is `collections.abc.Sequence`.

Parameters:

| Name | Type | Meaning | Constraints |
| --- | --- | --- | --- |
| `argv` | `Sequence[str] \| None` | The command-line arguments after the program name, for example `["--chars", "notes.txt"]` or `["notes.txt"]`. `None` means `sys.argv[1:]`, which is what the console script passes. | Each item is a `str`. The rules for the arguments are those of `--chars` and `FILE` in section 2.1. |

- Return value: `int`, the exit code, as in F04 design 2.2. `0` after it wrote the count of section 2.1 and one line break to standard output. `2` after it wrote one line `wordcount: <FILE>: <reason>` to standard error. The program name in every message is `wordcount`, whatever `sys.argv[0]` holds.

Errors:

| Error | When |
| --- | --- |
| `SystemExit` with code 2 | The arguments are wrong, as the last row of the Errors table in section 2.1 describes. argparse writes the usage line and its message to standard error and raises `SystemExit(2)`, so `main` does not return. |
| Any other exception | A bug. `main` catches only `OSError` and its subclasses and `UnicodeDecodeError` from `count_words` or `count_chars`, and lets every other exception reach the caller. |

- Side effects: As in F04 design 2.2: writes with `sys.stdout.write` and `sys.stderr.write`, not `print()` (architecture section 8), reads the file as section 2.1 says, and changes no global state, so a test may call it several times in one process.
- Performance target: None

Example:

`notes.txt` and `hello.txt` are the files of the example in section 2.1.

```python
>>> from troy_mode_trial.cli import main
>>> main(["--chars", "notes.txt"])
31
0
>>> main(["--chars", "hello.txt"])
4
0
>>> main(["notes.txt"])
4
0
>>> main(["--chars", "missing.txt"])  # writes to standard error
wordcount: missing.txt: no such file
2
>>> main(["--chars"])
usage: wordcount [--chars] FILE
wordcount: error: the following arguments are required: FILE
Traceback (most recent call last):
  ...
SystemExit: 2
```

### 2.3 `count_chars`

- Module: counting. Callers import it from the package `troy_mode_trial`, which `src/troy_mode_trial/__init__.py` defines, next to `count_words` and `count_lines`. The design adds no file under `src/troy_mode_trial/`.
- Purpose: Reads one UTF-8 text file and returns the number of characters of its decoded text, line ends included, where a character is one Unicode code point.

Signature:

```python
def count_chars(path: str | os.PathLike[str]) -> int:
```

Parameters:

| Name | Type | Meaning | Constraints |
| --- | --- | --- | --- |
| `path` | `str \| os.PathLike[str]` | The path of the file to count, absolute or relative to the current working directory. A `pathlib.Path` is an `os.PathLike[str]` and is accepted. | Names one existing, readable, regular file whose content is valid UTF-8. `bytes` paths are not accepted. |

- Return value: `int`, the number of characters, 0 or more. The function decodes the whole file as UTF-8 and removes one byte order mark (U+FEFF) at the start of the file (requirements Q12). The result is the number of code points of the text that remains, which is `len()` of that text.

  The rules for characters:

  - Line ends count as the file holds them, with no translation (requirements Q11): `\n` is one character, `\r` is one, and `\r\n` is two. Python's default text mode turns `\r\n` and `\r` into `\n`, so the function must read with line-end translation turned off.
  - Every code point counts once, whatever it is: a letter, a digit, white space, a control character, U+3000, or an emoji. A character that is several code points counts once for each, for example `é` written as `e` followed by the combining accent U+0301 is 2, and an emoji joined from several emoji with U+200D is more than 1.
  - Only one byte order mark at the very start is removed. A U+FEFF anywhere else, including a second one right after the first, counts as one character.
  - A file that is empty, or holds only the byte order mark, returns 0.

  | File bytes, as text | Result |
  | --- | --- |
  | (empty) | `0` |
  | `EF BB BF` (the byte order mark only) | `0` |
  | `Hello world\n  troy-mode  trial\n` | `31` |
  | `EF BB BF` then `Hello world\r\n  troy-mode  trial\r\n` | `33` |
  | `你好\r\n` (8 bytes) | `4` |
  | `one\rtwo\r\nthree\nfour` | `19` |
  | `EF BB BF EF BB BF` then `a` | `2` |
  | `e` then U+0301 | `2` |

Errors:

The function defines no exception of its own (requirements Q4). It lets Python's own exception reach the caller, with the same table as `count_words` and `count_lines`.

| Error | When |
| --- | --- |
| `FileNotFoundError` | No file exists at `path`, or `path` is the empty string. |
| `IsADirectoryError` or `PermissionError` | `path` names a folder. Linux raises `IsADirectoryError`. Windows raises `PermissionError`. |
| `PermissionError` | The process may not read the file. |
| `UnicodeDecodeError` | Any byte of the file is not valid UTF-8, wherever it is. |
| `TypeError` | `path` is neither a `str` nor an `os.PathLike[str]`, for example `bytes` or an `int`. |

- Side effects: The function opens the file for reading and closes it before it returns or raises. It writes, sends, and stores nothing.
- Performance target: None

Example:

`notes.txt` and `hello.txt` are the files of the example in section 2.1. `windows.txt` holds the bytes `EF BB BF` followed by `Hello world\r\n  troy-mode  trial\r\n`, as Notepad saves it.

```python
>>> from pathlib import Path
>>> from troy_mode_trial import count_chars
>>> count_chars("notes.txt")
31
>>> count_chars("hello.txt")
4
>>> count_chars(Path("windows.txt"))
33
>>> count_chars("missing.txt")
Traceback (most recent call last):
  ...
FileNotFoundError: [Errno 2] No such file or directory: 'missing.txt'
```

## 3. Changes to existing interfaces

Requirements 6.0 added F06 as a new feature, with the option `--chars` and the decisions Q10 to Q13, in the merged [docs] PR "[docs] Change the requirements: add the wordcount --chars option" (commit `fc2bb26`). F04 is accepted, so F06 changes its interfaces only as follows:

1. `wordcount` (F04 design 2.1) gains the option `--chars`. `wordcount FILE` without the option prints the same count, the same error lines, and the same exit codes as before.
2. The usage line changes from `usage: wordcount FILE` to `usage: wordcount [--chars] FILE`, if Troy accepts proposal 1 in section 2.1. The rest of every usage error stays: exit code 2, empty standard output, and a second line `wordcount: error: <message>`. F04's test plan defines a usage error by a first line of exactly `usage: wordcount FILE`, and the cases F04-T11, F04-T12, F04-T13, and F04-T21 check that line word for word. Those cases change their expected first line to `usage: wordcount [--chars] FILE`, and nothing else in them. The Test Manager makes that change in F06's test plan PR. If Troy keeps F04's line, no F04 test case changes.
3. `main` (F04 design 2.2) keeps its signature. It now accepts `--chars` in `argv` and then calls `count_chars`.
4. `src/troy_mode_trial/__init__.py` exports `count_chars` next to `count_lines` and `count_words`. This adds a name and changes no existing one. `count_words` and `count_lines` keep their signatures, behavior, and errors, and `__init__.py` still does not import cli.

F05 adds `--lines` to the same command at the same time and also changes the usage line. Whichever of F05 and F06 lands second keeps the option of the other, and its usage line shows both.

## 4. Architect review

| Item | Result | Note |
| --- | --- | --- |
| Fits the module layout and the data model | Pass | `wordcount` and `main` stay in cli, in `src/troy_mode_trial/cli.py`. `count_chars` goes in counting, in `src/troy_mode_trial/counting.py`, and is exported from `src/troy_mode_trial/__init__.py`, counting's external interface. Both files are already in counting's Owns column, and the design adds no file under `src/troy_mode_trial/`. `main` imports `count_chars` from the package, as architecture section 4 asks. The design needs no architecture change. Architecture 3.0 already holds `count_lines` in counting, so a third counting function is the same case that requirements Q6 settled. The short description "Counts the words of a text" in the module table can be widened at the next architecture change, but R07 does not depend on it. `argparse` with `allow_abbrev=False` and a mutually exclusive group is still the standard library (ADR-0001), so the design adds no dependency. The architecture defines no data model. |
| Follows the error handling and naming conventions | Pass | `count_chars` defines no exception of its own. Like `count_words` and `count_lines`, it lets Python's own exceptions through (architecture section 6, requirements Q4). `main` still catches only `OSError` and its subclasses and `UnicodeDecodeError`, around either counting call, and for `--chars` writes the same line `wordcount: <FILE>: <reason>` with exit code 2 (ADR-0002). A wrong command line exits with code 2 and a usage line, code 1 still means only a bug, and standard output holds only the count and one line break, written with `write` (section 8). `count_chars` follows the `count_<thing>(path)` naming and the path type of the two existing functions. In round 1 I ran argparse (Python 3.14.3; the project's Python 3.13 environment was not on this machine) with one `--chars` flag, `prog="wordcount"`, `add_help=False`, and `allow_abbrev=False`, both on its own and inside a mutually exclusive group. Each gives the usage line `usage: wordcount [--chars] FILE` and the outcome the design states for `--chars FILE`, `FILE --chars`, `--char`, `--ch`, `--c`, `-c`, `-h`, `--chars` with no file, `--chars=VALUE`, `--chars --chars`, `--chars -- -n.txt`, and `-- --chars`. I also checked the eight rows of the table in section 2.3 and the counts in the examples by hand. |
| Does not duplicate an existing interface | Pass | No existing interface counts characters. `main` counts through `count_chars` and does not count anything itself. `count_chars` shares only the reading rules of `count_words` and `count_lines`, which is a matter for the code, not a second interface. |
| Depends only on features earlier in the order | Pass | F06 depends only on F04, and through it on F03 and F01. All three come before F06 in the order (F01, F03, F04, F06, F02, F05) and are usable on Troy's devices. F06 uses neither F02 nor F05. `--lines` appears only as an option that is unknown until F05 adds it. |
| Adds no hidden coupling between modules | Pass | cli relies only on what `count_chars` documents: its signature, its `int` result, and the exceptions in its table, which architecture section 6 already names. The exclusive set of counting options lives in cli, and counting knows nothing about options. The package `__init__.py` adds only the name `count_chars` and still does not import cli. `main` keeps no global state. |
| Changes an implemented interface only through the change flow | Pass | F04 is accepted, and requirements 6.0 (commit `fc2bb26`, approved by Troy) added the option `--chars` to its command, so the change comes through the requirement change flow. Section 3 lists every change: the option, the new usage line if Troy accepts proposal 1, the unchanged signature of `main`, and the new export. I checked F04's test plan and `tests/test_cli.py`. F04-T11, F04-T12, F04-T13, and F04-T21 are exactly the cases that rely on the first line `usage: wordcount FILE`, either through the plan's definition of a usage error or word for word. No other F04 case changes. The v0.2 scenario for a wrong command line checks only that standard error starts with `usage:`, so it stays as it is. `count_words` and `count_lines` do not change. |
| The summary for Troy says what the design says, and lists every point Troy decides | Pass | The summary matches the design. It covers the new option and its count: one code point, `你好` with a Windows line end is 4, a Windows line end is 2, and the byte order mark is not counted. It also says that the words, the error lines, and exit code 2 stay as they are, names the new library function, and says the project must be installed again. Its three points are proposals 1, 2, and 3 of section 2.1, in the same order, each with the design's recommendation and reason. The design has no other open choice. Its two risks match section 2.3 (characters made of several code points) and section 3 (F05 also changes the usage line). Each language is under 2,000 characters, about 800 in Chinese and 1,997 in English, and holds no internal IDs. Feature IDs are allowed. |

| Round | Issue | Resolution |
| --- | --- | --- |
| 1 | No blocking finding. The design needs no architecture change, as the Interface Designer asked me to confirm (item 1). Four notes, which do not block. For the Interface Designer: the English summary is about 1,997 of its 2,000 characters, so any text added in a later round must be paid for by shortening the summary elsewhere. Section 3 could also cite the requirements PR by its number, #63, next to its title and commit. For the Interface Designer and the main session: section 2.1 says that F05's design fixes the message for `--lines` with `--chars`. That holds only if F05 lands second. F05 changes the same `wordcount` and `main`, so the batch plan should start F05 only after this design merges (F06 1/6). For the Developer: build the counting options as a mutually exclusive group in the parser with `allow_abbrev=False`. Read with `encoding="utf-8-sig"` and `newline=""` and return `len()` of the text, sharing the path check with the existing functions. Update the usage line in the doc comment of `main`, and keep `main` within 50 lines (R04), for example with a helper that picks the counting function. For the Test Manager: change only the expected first line of F04-T11, F04-T12, F04-T13, and F04-T21. Write each file in binary mode so that `\r\n` reaches `count_chars` as two characters. | Approved in round 1. |

## 5. Change log

| Version | Date | Change |
| --- | --- | --- |
| 0.1 | 2026-11-23 | First draft. |
| 1.0 | 2026-11-23 | Approved by Troy. |
