---
troy-doc: "F07-design"
lang: "en"
version: "1.1"
updated: "2026-11-25"
status: "Approved by Troy on 2026-11-25"
mirror: "design.zh-CN.md"
---

# F07 Longest word option: interface design

## 1. Feature

- ID and name: F07 Longest word option
- Requirement: [docs/requirements.md](../../requirements.md#4-features)
- Hard dependencies: F04
- Soft dependencies: None

## 2. Interfaces

F07 changes the two interfaces of F04 in the module cli and adds one interface to the module counting, as F06 did. Section 2.1 is the command that Troy types, which gains the option `--longest`. Section 2.2 is the function behind it. Section 2.3 is the new library function `count_longest`, which finds the length of the longest word of a file and which `main` calls for `--longest`.

The search for the longest word is in counting, not in cli, for the reasons F06 design section 2 gives for `count_chars`. Architecture section 3 says that cli reads the arguments and calls counting. counting already holds the rules that `--longest` must share with `wordcount FILE`: what a word is (F03), that one byte order mark at the start is skipped (requirements Q5), and that a missing file or a file that is not valid UTF-8 raises Python's own exception (Q4). Keeping the word rule in one module means that `wordcount FILE` and `wordcount --longest FILE` cannot disagree on what a word is (Q15). Requirements Q6 settled that counting lines fits counting with no architecture change. Measuring words fits it the same way.

F05's and F06's code is on `main`, so the command already has `--lines` and `--chars` in a set of counting options that exclude each other. `--longest` is the third member of that set, which is how requirements Q16 holds. F07 uses nothing else of F05 or F06. Three rules that Troy approved for F06 and F05 hold for the whole command line, so they hold for `--longest` too: a shortened option name is a wrong command line, an option may come after the file, and two counting options in one command give a usage error in argparse's own words.

One point in section 2.1 is a proposal that Troy accepts or changes, and it says so where it stands: the usage line that shows the new option.

### 2.1 `wordcount`

- Module: cli. The console script `wordcount = "troy_mode_trial.cli:main"` in `pyproject.toml` stays as F04 declared it.
- Purpose: Prints the number of words in one UTF-8 text file, as in F04, or, with `--longest`, the length in characters of its longest word, so that Troy can find the longest word's length in PowerShell without writing Python. `--lines` and `--chars` work as F05 and F06 say.

Signature:

```text
usage: wordcount [--lines | --chars | --longest] FILE
```

Parameters:

| Name | Type | Meaning | Constraints |
| --- | --- | --- | --- |
| `--longest` | Option, a flag with no value | Print the length, in characters, of the longest word of `FILE` instead of its number of words. Without a counting option, the command prints the words, exactly as F04 does. | Optional. Only the full name `--longest`. There is no short form, such as `-L` (requirements Q14). A shortened name, such as `--long` or `--lo`, is a wrong command line, as for `--chars` and `--lines`. The option may come before or after `FILE`: `wordcount --longest notes.txt` and `wordcount notes.txt --longest` do the same. Given twice, as in `wordcount --longest --longest notes.txt`, it works as given once. `--longest=VALUE` is a wrong command line. It cannot come with `--lines` or `--chars`, in any order (requirements Q16). |
| `--lines` | Option, a flag with no value | Print the number of lines of `FILE`, exactly as F05 design 2.1 says. | As in F05 design 2.1. It cannot come with `--chars` or `--longest`. |
| `--chars` | Option, a flag with no value | Print the number of characters of `FILE`, exactly as F06 design 2.1 says. | As in F06 design 2.1. It cannot come with `--lines` or `--longest`. |
| `FILE` | One command-line argument | The path of the file to read, absolute or relative to the current working directory. | As in F04 design 2.1: exactly one argument, naming one existing, readable, regular file whose content is valid UTF-8. A path that starts with `-` follows `--`, for example `wordcount --longest -- -notes.txt`. After `--`, the text `--longest` is a file name, not the option. |

The command still has no `-h` or `--help`, and no option other than `--lines`, `--chars`, and `--longest` (requirements section 8). It never prints the longest word itself (requirements section 8).

**Proposal 1, the usage line, for Troy to accept or change.** The usage line shows the three options as alternatives: `usage: wordcount [--lines | --chars | --longest] FILE`, instead of F05's `usage: wordcount [--lines | --chars] FILE`. This follows the form Troy approved for F05: the brackets say that a counting option is optional, and each `|` says that a command takes at most one of them. It is the line argparse writes for the set of options, so it needs no extra code. `--longest` comes last, as in the requirements. The other choice keeps F05's line, so the command names `--longest` nowhere, because it has no help.

- Return value: exit code 0 on success. Standard output holds one decimal number with no sign, padding, or separator, followed by one line break, and standard error stays empty, as in F04 design 2.1.
  - Without a counting option, the number is what `count_words(FILE)` returns, as in F04.
  - With `--longest`, the number is what `count_longest(FILE)` returns (section 2.3): the length of the longest word, in Unicode code points, with words as F03 counts them, or 0 for a file with no word. The word is the whole run of characters that are not white space, punctuation included, so `don't,` is 6 (requirements Q15). `世界!` is 3, although it is 7 bytes. A web address or a run such as `x--y` is one word, so such a run is often the longest. Line ends are white space, so a file saved on Windows and the same file saved on Linux give the same number.
  - With `--lines` or `--chars`, the number is what F05's or F06's design says.

Errors:

Every error leaves standard output empty and writes to standard error only. A file error with `--longest` gives exactly the message and exit code that `wordcount FILE` gives for the same file (requirements F07): one line `wordcount: <FILE>: <reason>`, followed by one line break, and exit code 2. `<FILE>` and the five reason texts are those of F04 design 2.1, unchanged.

| Error | When |
| --- | --- |
| Exit code 2, reason `no such file` | As in F04 design 2.1: no file or folder exists at `FILE`, `FILE` is the empty string, or a folder in the path is missing or is a file. |
| Exit code 2, reason `is a folder` | As in F04 design 2.1: `FILE` names a folder. |
| Exit code 2, reason `permission denied` | As in F04 design 2.1: the process may not read the file. |
| Exit code 2, reason `not valid UTF-8` | As in F04 design 2.1: the file content is not valid UTF-8. With `--longest`, the command decodes the whole file, so a file whose invalid bytes come after valid text is still this error, and no number is printed. |
| Exit code 2, reason `cannot read file` | As in F04 design 2.1: any other `OSError` while the file is opened or read. |
| Exit code 2, usage line, two counting options | The command line holds `--longest` together with `--lines` or `--chars`, in any order and at any place. Standard error holds the usage line of proposal 1 and then one line in argparse's own words, which names the later option first, as for `--lines` with `--chars` (F05 design 2.1, proposal 2, approved). For example, `wordcount --lines --longest notes.txt` gives `wordcount: error: argument --longest: not allowed with argument --lines`, and `wordcount --longest notes.txt --chars` gives `wordcount: error: argument --chars: not allowed with argument --longest`. This error comes before the check for a missing `FILE`. `--lines` with `--chars` keeps the message of F05's design. |
| Exit code 2, usage line, other cases | The command line holds no `FILE`, more than one argument, an option other than the three, a shortened option such as `--long`, `-L`, `-h`, or `--longest=VALUE`. argparse writes the usage line of proposal 1 and then one line `wordcount: error: <message>` in argparse's own words, for example `wordcount: error: the following arguments are required: FILE` for `wordcount --longest`, or `wordcount: error: unrecognized arguments: -L` for `wordcount -L notes.txt`. |

Any other exception is a bug, as in F04: Python writes the traceback to standard error and exits with code 1 (architecture section 6).

- Side effects: As in F04 design 2.1: the command opens `FILE` for reading and closes it before it exits, writes only to standard output and standard error, and writes, sends, and stores nothing. The option exists only after the project is installed again once F07 lands, for example with `uv pip install -e . --no-deps`.
- Performance target: None

Example:

`notes.txt` in the current folder is UTF-8 and holds the two lines `Hello world` and `  troy-mode  trial`, each ending with `\n`. `greeting.txt` holds the one line `你好 世界!`, ending with `\r\n`. `dashes.txt` holds the one line `-- ...`. `latin1.txt` holds `café au lait` in Latin-1.

```text
PS> wordcount --longest notes.txt
9
PS> wordcount notes.txt --longest
9
PS> wordcount notes.txt
4
PS> wordcount --longest greeting.txt
3
PS> wordcount --longest dashes.txt
0
PS> wordcount --longest missing.txt
wordcount: missing.txt: no such file
PS> $LASTEXITCODE
2
PS> wordcount --longest latin1.txt
wordcount: latin1.txt: not valid UTF-8
PS> $LASTEXITCODE
2
PS> wordcount --lines --longest notes.txt
usage: wordcount [--lines | --chars | --longest] FILE
wordcount: error: argument --longest: not allowed with argument --lines
PS> $LASTEXITCODE
2
PS> wordcount --long notes.txt
usage: wordcount [--lines | --chars | --longest] FILE
wordcount: error: unrecognized arguments: --long
PS> $LASTEXITCODE
2
```

### 2.2 `main`

- Module: cli, in `src/troy_mode_trial/cli.py`, as in F04 design 2.2. Tests import it as `from troy_mode_trial.cli import main`.
- Purpose: Runs the `wordcount` command of section 2.1 once: reads the arguments, gets the number through `count_words`, through `count_lines` for `--lines`, through `count_chars` for `--chars`, or through `count_longest` for `--longest`, writes the result or the error, and returns the exit code. It imports the four functions from the package `troy_mode_trial`, never from `troy_mode_trial.counting` (architecture section 4).

Signature:

```python
def main(argv: Sequence[str] | None = None) -> int:
```

The signature does not change. `Sequence` is `collections.abc.Sequence`.

Parameters:

| Name | Type | Meaning | Constraints |
| --- | --- | --- | --- |
| `argv` | `Sequence[str] \| None` | The command-line arguments after the program name, for example `["--longest", "notes.txt"]` or `["notes.txt"]`. `None` means `sys.argv[1:]`, which is what the console script passes. | Each item is a `str`. The rules for the arguments are those of `--lines`, `--chars`, `--longest`, and `FILE` in section 2.1. |

- Return value: `int`, the exit code, as in F04 design 2.2. `0` after it wrote the number of section 2.1 and one line break to standard output. `2` after it wrote one line `wordcount: <FILE>: <reason>` to standard error. The program name in every message is `wordcount`, whatever `sys.argv[0]` holds.

Errors:

| Error | When |
| --- | --- |
| `SystemExit` with code 2 | The arguments are wrong, as the two usage rows of the Errors table in section 2.1 describe, including `--longest` with `--lines` or `--chars`. argparse writes the usage line and its message to standard error and raises `SystemExit(2)`, so `main` does not return. |
| Any other exception | A bug. `main` catches only `OSError` and its subclasses and `UnicodeDecodeError` from `count_words`, `count_lines`, `count_chars`, or `count_longest`, and lets every other exception reach the caller. |

- Side effects: As in F04 design 2.2: writes with `sys.stdout.write` and `sys.stderr.write`, not `print()` (architecture section 8), reads the file as section 2.1 says, and changes no global state, so a test may call it several times in one process.
- Performance target: None

Example:

`notes.txt` and `greeting.txt` are the files of the example in section 2.1.

```python
>>> from troy_mode_trial.cli import main
>>> main(["--longest", "notes.txt"])
9
0
>>> main(["--longest", "greeting.txt"])
3
0
>>> main(["--longest", "missing.txt"])  # writes to standard error
wordcount: missing.txt: no such file
2
>>> main(["--longest", "--chars", "notes.txt"])
usage: wordcount [--lines | --chars | --longest] FILE
wordcount: error: argument --chars: not allowed with argument --longest
Traceback (most recent call last):
  ...
SystemExit: 2
```

### 2.3 `count_longest`

- Module: counting. Callers import it from the package `troy_mode_trial`, which `src/troy_mode_trial/__init__.py` defines, next to `count_chars`, `count_lines`, and `count_words`. The design adds no file under `src/troy_mode_trial/`.
- Purpose: Reads one UTF-8 text file and returns the length, in Unicode code points, of its longest word, with words as `count_words` finds them, or 0 when the file has no word.

Signature:

```python
def count_longest(path: str | os.PathLike[str]) -> int:
```

The name starts with `count_`, like `count_words`, `count_lines`, and `count_chars`, so that the four functions behind the command read as one family. Troy chose this name. It returns a length, not a number of things, as the Purpose and the Return value say.

Parameters:

| Name | Type | Meaning | Constraints |
| --- | --- | --- | --- |
| `path` | `str \| os.PathLike[str]` | The path of the file to read, absolute or relative to the current working directory. A `pathlib.Path` is an `os.PathLike[str]` and is accepted. | Names one existing, readable, regular file whose content is valid UTF-8. `bytes` paths are not accepted. |

- Return value: `int`, 0 or more. The function decodes the whole file as UTF-8 and removes one byte order mark (U+FEFF) at the start of the file (requirements Q5). It splits the text into words exactly as `count_words` does (F03 design), and returns the greatest `len()` of a word, or 0 when there is no word. So `count_words(path)` is 0 exactly when `count_longest(path)` is 0. Inside counting, the function uses the same word rule and the same file reading as `count_words`, not a second copy of them, so the two cannot disagree on what a word is.

  The rules for words and their length:

  - A word is a run of one or more characters for which `str.isspace()` is false, with at least one character for which `str.isalnum()` is true. The whole run is the word, punctuation included (requirements Q15). A run with no letter or digit, such as `--` or `...`, is not a word, and its length never counts, however long it is.
  - Every character for which `str.isspace()` is true separates words, including the line ends `\n`, `\r`, and `\r\n`, a tab, and U+3000. No white space is ever part of a word, so line-end translation does not change the result.
  - The length counts code points, as `--chars` does. `你` is 1, although it is three bytes. A character that is several code points counts once for each: `é` written as `e` followed by the combining accent U+0301 is 2.
  - Only one byte order mark at the very start is removed. A U+FEFF anywhere else is not white space, so it is part of the run it is in and adds 1 to that run's length, as it does for `count_words`.
  - When several words share the greatest length, the result is that length. Which word it is does not matter, since the function returns only the length.

  | File bytes, as text | Result |
  | --- | --- |
  | (empty) | `0` |
  | `EF BB BF` (the byte order mark only) | `0` |
  | `-- ...\n` | `0` |
  | `Hello world\n  troy-mode  trial\n` | `9` |
  | `don't, he said.` | `6` |
  | `你好 世界!\r\n` | `3` |
  | `----a ......` | `5` |
  | `a\tbb\rccc\r\ndd` | `3` |
  | `x` then U+3000 then `yy` | `2` |
  | `EF BB BF` then `abc` | `3` |
  | `EF BB BF EF BB BF` then `abc` | `4` |
  | `e` then U+0301 | `2` |

Errors:

The function defines no exception of its own (requirements Q4). It lets Python's own exception reach the caller, with the same table as `count_words`, `count_lines`, and `count_chars`.

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

`notes.txt`, `greeting.txt`, and `dashes.txt` are the files of the example in section 2.1.

```python
>>> from pathlib import Path
>>> from troy_mode_trial import count_longest
>>> count_longest("notes.txt")
9
>>> count_longest(Path("greeting.txt"))
3
>>> count_longest("dashes.txt")
0
>>> count_longest("missing.txt")
Traceback (most recent call last):
  ...
FileNotFoundError: [Errno 2] No such file or directory: 'missing.txt'
```

## 3. Changes to existing interfaces

Requirements 7.0 added F07 as a new feature, with the option `--longest` and the decisions Q14 to Q16, in the merged [docs] PR "[docs] Change the requirements: add the wordcount --longest option" (commit `3cc6e1b`). F04 is accepted, and F05 and F06, which added `--lines` and `--chars` to the same command, are accepted too. F07 changes their interfaces only as follows:

1. `wordcount` (F04 design 2.1) gains the option `--longest`. `wordcount FILE`, `wordcount --lines FILE`, and `wordcount --chars FILE` print the same numbers, the same error lines, and the same exit codes as before.
2. The usage line changes from `usage: wordcount [--lines | --chars] FILE` to `usage: wordcount [--lines | --chars | --longest] FILE`, if Troy accepts proposal 1 in section 2.1. The rest of every usage error stays: exit code 2, empty standard output, and a second line `wordcount: error: <message>`, with the same message as before for every command line without `--longest`. The expected usage lines change as follows, and nothing else in the cases:
   - F05's test plan: the cases that check the first line `usage: wordcount [--lines | --chars] FILE` word for word, F05-T13, F05-T14, F05-T15, and F05-T23. In `tests/test_cli_lines.py` they take that line from the constant `USAGE_BOTH`. Their expected first line becomes the line of proposal 1. F05 is accepted, so these cases must pass in every F07 PR, both before and after F07's code is in (R10). Replacing `USAGE_BOTH` outright in F07's test PR would make them fail until the code lands, so their check must accept the old line before F07's code and the new line after it. Their second lines, including `argument --chars: not allowed with argument --lines`, do not change.
   - F06's test plan: F06-T28 and F06-T34 check that the usage line holds `--chars` inside one pair of brackets before ` FILE`, which the new line still does, so they do not change.
   - F04's test plan 1.1 checks only that a usage line starts with `usage: wordcount `, and the v0.3 version test plan checks only that standard error starts with `usage:`, so they do not change.
   - F05's and F06's designs show the usage line of their time in their examples. This design does not change them, as F05's design did not change F06's.
3. A command line with `--longest` used to be a usage error with `unrecognized arguments: --longest`. It now gets the number of section 2.1, or, with `--lines` or `--chars`, the usage error of section 2.1.
4. `main` (F04 design 2.2) keeps its signature. It now accepts `--longest` in `argv` and then calls `count_longest`.
5. `src/troy_mode_trial/__init__.py` exports `count_longest` next to `count_chars`, `count_lines`, and `count_words`. This adds a name and changes no existing one. The three counting functions keep their signatures, behavior, and errors, and `__init__.py` still does not import cli.

## 4. Architect review

| Item | Result | Note |
| --- | --- | --- |
| Fits the module layout and the data model | Pass | `wordcount` and `main` stay in cli, in `src/troy_mode_trial/cli.py`. `count_longest` goes in counting and is exported from `src/troy_mode_trial/__init__.py`, counting's external interface. Both files are already in counting's Owns column, and the design adds no file under `src/troy_mode_trial/`. `main` imports the four functions from the package, as architecture section 4 asks. Measuring words is the same case that requirements Q6 settled for lines, so the design needs no architecture change. The third member of the argparse mutually exclusive group is still the standard library (ADR-0001), so the design adds no dependency. The architecture defines no data model. |
| Follows the error handling and naming conventions | Pass | `count_longest` defines no exception of its own and has the same error table as the three counting functions (architecture section 6, requirements Q4). `main` still catches only `OSError` and its subclasses and `UnicodeDecodeError`, and for `--longest` writes the same line `wordcount: <FILE>: <reason>` with exit code 2 (ADR-0002). A wrong command line exits with code 2 and a usage line (requirements Q16), code 1 still means only a bug, and standard output holds only the number and one line break, written with `write` (section 8). The architecture has no rule for function names. `count_longest` starts with `count_`, like `count_words`, `count_lines`, and `count_chars`, as Troy decided on PR #79, so the four functions behind the command read as one family. Section 2.3 says plainly that it returns a length, not a number of things, so the name does not mislead a caller about the result. The name clashes with no name in the package or in cli, and sections 2 and 3 use it everywhere, in both languages. As the Interface Designer asked, I ran argparse (Python 3.14.3; the project's Python 3.13 environment was not on this machine) with `prog="wordcount"`, `add_help=False`, `allow_abbrev=False`, a mutually exclusive group of `--lines`, `--chars`, then `--longest`, and `FILE`. It gives the usage line `usage: wordcount [--lines \| --chars \| --longest] FILE` and exactly the two messages of the Errors table in section 2.1, `argument --longest: not allowed with argument --chars` for `--chars --longest`, and `argument --lines: not allowed with argument --longest` for `--longest --lines` with no file, so the two-option error comes before the missing `FILE`. `--lines --chars` keeps `argument --chars: not allowed with argument --lines`. It also gives the outcome the design states for `--longest FILE`, `FILE --longest`, `--longest --longest`, `--longest -- -n.txt`, `-- --longest`, `-L`, `--long`, `--lo`, `-h`, `--longest=x`, `--longest` with no file, and two files. I also checked the twelve rows of the table in section 2.3 and the numbers in the examples by hand against F03's word rule. |
| Does not duplicate an existing interface | Pass | No existing interface measures words. `main` gets the length only through `count_longest` and measures nothing itself. `count_longest` shares the word rule and the reading rules with `count_words`, which section 2.3 now states, and which is a matter for the code inside counting, not a second interface. |
| Depends only on features earlier in the order | Pass | F07 depends only on F04, and through it on F03 and F01. All three come before F07 in the order (F01, F03, F04, F07, F06, F02, F05) and are usable on Troy's devices. F05 and F06 come after F07 in the order, but they are accepted and their code is on `main`, so F07 only adds a third member to the group they built and waits for no feature. It calls none of their functions. |
| Adds no hidden coupling between modules | Pass | cli relies only on what `count_longest` documents: its signature, its `int` result, and the exceptions in its table, which architecture section 6 already names. The exclusive set of options lives in cli, and counting knows nothing about options. The rule that `wordcount` and `wordcount --longest` agree on what a word is stays inside counting. `src/troy_mode_trial/__init__.py` adds only the name `count_longest` and still does not import cli. `main` keeps no global state. |
| Changes an implemented interface only through the change flow | Pass | F04, F05, and F06 are accepted. Requirements 7.0 (commit `3cc6e1b`, approved by Troy) added `--longest` to F04's command, with Q14 to Q16, so the change comes through the requirement change flow. The usage line that F05 fixed changes only if Troy accepts proposal 1. Section 3 lists every change: the option, the usage line, the old `unrecognized arguments: --longest` error, the unchanged signature of `main`, and the new export. I checked `tests/test_cli_lines.py`, `tests/test_cli_chars.py`, `tests/test_cli.py`, and the test plans. F05-T13, F05-T14, F05-T15, and F05-T23 are exactly the cases that use `USAGE_BOTH`. F06's pattern `^usage: wordcount \[[^\]]*--chars[^\]]*\] FILE$` matches the new line. F04's plan 1.1 and the v0.3 version test plan check only the start of the line. The rename to `count_longest` changes no implemented interface: F07's code is not on `main`, no source or test file uses either name, and the rename follows Troy's decision on PR #79. |
| The summary for Troy says what the design says, and lists every point Troy decides | Pass | The summary matches the design: the length in characters, punctuation included, `don't,` is 6 and `世界!` is 3, 0 for a file with no word, the same result for Windows and Linux line ends, the full name only, before or after the file, a usage error with `--lines` or `--chars`, the same file errors and exit code 2, the other commands unchanged, the new library function, and installing again. Its one point is proposal 1 of section 2.1, with the design's recommendation and reason. The design has no other open choice. Its two risks match section 2.3 (characters of several code points) and section 2.1 (long runs with no space). I measured about 790 characters in Chinese and 1,690 in English, both under 2,000. Neither holds an internal ID that troy-check's R22 pattern finds. Feature IDs are allowed. For version 1.1, the summary of PR #82 matches the change: the new name `count_longest` and why, the function staying in counting with no new module, its behavior, result, and errors unchanged, the command unchanged, and the two clarifications of sections 2.3 and 3, which change no behavior. It lists nothing for Troy to decide, which is right, because the name and the module are Troy's decisions on PR #79 and the design has no other open choice. Its one risk, a name that starts with "count" for a function that returns a length, is what section 2.3 says. |

| Round | Issue | Resolution |
| --- | --- | --- |
| 1 | No blocking finding. The usage line and the two-option messages are confirmed by running argparse, as the second row of the checklist says. Notes, which do not block. For the Interface Designer: the summary says that `wordcount FILE`, `--lines`, and `--chars` print what they print today. Their numbers and file errors do, but their usage error's first line changes if Troy accepts the decision point, which the summary also states, so it needs no change. For the Developer: add `--longest` to the existing mutually exclusive group after `--chars`. Find the words in `longest_word_length` with the same `_checked_path`, empty-path check, `encoding="utf-8-sig"` read, `str.split()`, and `_has_letter_or_digit` as `count_words`, so the two cannot disagree. Update the usage line in the doc comments of `_build_parser` and `main`, and keep `main` within 50 lines (R04), for example by widening `_count_function`. For the Test Manager: F05-T13, F05-T14, F05-T15, and F05-T23 test an accepted feature, so they must pass in every F07 PR (R10), before and after F07's code. As F05 did for F06 with its landing check, make their expected first line depend on whether the branch has `--longest`, or check it against a pattern, rather than replacing `USAGE_BOTH` outright. For the Product Manager: the F07 prototype says `世界!` is 3 characters "not 9 bytes". It is 7 bytes, as design section 2.1 says. | Approved in round 1. |
| 1 (PR #82, version 1.1) | No blocking finding. The rename of `longest_word_length` to `count_longest` is complete in sections 2 and 3 of both languages, and this section now uses the new name. The function stays in counting, as Troy decided on PR #79, with its signature, result, and errors unchanged. The two clarifications in sections 2.3 and 3 match the round 1 notes for the Developer and the Test Manager, which now apply to `count_longest`. Note, which does not block: section 2.1 still calls the usage line "Proposal 1, for Troy to accept or change", and section 3 item 2 still says "if Troy accepts proposal 1", although Troy approved the design in version 1.0. The Interface Designer may reword them in a later revision. | Approved in round 1. |

## 5. Change log

| Version | Date | Change |
| --- | --- | --- |
| 0.1 | 2026-11-25 | First draft. |
| 1.0 | 2026-11-25 | Approved by Troy. |
| 1.1 | 2026-11-25 | Renamed the library function `longest_word_length` to `count_longest`, consistent with `count_words`, `count_lines`, and `count_chars`, after Troy overturned the round 3 ruling on PR #81. It stays in the module counting, and what it does, returns, and raises is unchanged. Removed the reason given for the old name. Section 2.3 now says the function shares the word rule and file reading of `count_words`, and section 3 says that F05's usage-line cases must pass before and after F07's code. |
