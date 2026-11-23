---
troy-doc: "F05-design"
lang: "en"
version: "1.0"
updated: "2026-11-23"
status: "Approved by Troy on 2026-11-23"
mirror: "design.zh-CN.md"
---

# F05 Line count option: interface design

## 1. Feature

- ID and name: F05 Line count option
- Requirement: [docs/requirements.md](../../requirements.md#4-features)
- Hard dependencies: F02, F04
- Soft dependencies: None

## 2. Interfaces

F05 changes the two interfaces of F04 in the module cli, as F06 also does. Section 2.1 is the command that Troy types, which gains the option `--lines`. Section 2.2 is the function behind it. F05 adds no library function: `main` counts lines through F02's `count_lines`, which the package `troy_mode_trial` already exports (F02 design 2.1).

This design builds on F06's design 1.0, which Troy approved with every recommendation. Three of its rules hold for the whole command line, so they hold for `--lines` as they do for `--chars`: the usage line names the options, a shortened option name is a wrong command line, and an option may come after the file. F06's design makes `--chars` the first member of a set of counting options that exclude each other, and leaves to this design the usage line and the message when `--lines` and `--chars` come together (requirements Q13). `--lines` is the second member of that set.

Two points in section 2.1 are proposals that Troy accepts or changes, and each one says so where it stands: the usage line that shows both options, and the message for both options in one command.

### 2.1 `wordcount`

- Module: cli. The console script `wordcount = "troy_mode_trial.cli:main"` in `pyproject.toml` stays as F04 declared it.
- Purpose: Prints the number of words in one UTF-8 text file, as in F04, or, with `--lines`, the number of lines in it, counted as F02 counts them, or, with `--chars`, the number of its characters, as in F06. Troy can then count lines in PowerShell without writing Python.

Signature:

```text
usage: wordcount [--lines | --chars] FILE
```

Parameters:

| Name | Type | Meaning | Constraints |
| --- | --- | --- | --- |
| `--lines` | Option, a flag with no value | Print the number of lines of `FILE` instead of its words. Without a counting option, the command prints the words, exactly as F04 does. | Optional. Only the full name `--lines`. There is no short form, such as `-l` (requirements Q7). A shortened name, such as `--line` or `--li`, is a wrong command line, as for `--chars` (F06 design 2.1, proposal 2, approved). The option may come before or after `FILE`: `wordcount --lines notes.txt` and `wordcount notes.txt --lines` do the same (F06 design 2.1, proposal 3, approved). Given twice, as in `wordcount --lines --lines notes.txt`, it counts lines once, as given once. `--lines=VALUE` is a wrong command line. It cannot come with `--chars`, in either order (requirements Q13, proposal 2 below). |
| `--chars` | Option, a flag with no value | Print the number of characters of `FILE`, exactly as F06 design 2.1 says. | As in F06 design 2.1. It cannot come with `--lines`, in either order. |
| `FILE` | One command-line argument | The path of the file to count, absolute or relative to the current working directory. | As in F04 design 2.1: exactly one argument, naming one existing, readable, regular file whose content is valid UTF-8. A path that starts with `-` follows `--`, for example `wordcount --lines -- -notes.txt`. After `--`, the text `--lines` is a file name, not the option. |

The command still has no `-h` or `--help`, and no option other than `--lines` and `--chars` (requirements section 8).

**Proposal 1, the usage line, for Troy to accept or change.** The usage line shows both options as alternatives: `usage: wordcount [--lines | --chars] FILE`. The brackets say that a counting option is optional, and the `|` says that a command takes at most one of them. This is the line argparse writes for a set of options that exclude each other, so it needs no extra code. The other choice is `usage: wordcount [--lines] [--chars] FILE`, which reads as if both options could come together, although that is a usage error. `--lines` comes first because the requirements name it first.

**Proposal 2, both options in one command, for Troy to accept or change.** `wordcount --lines --chars notes.txt` is a usage error with exit code 2, as Troy decided (requirements Q13). Standard error holds the usage line of proposal 1 and then one line in argparse's own words, which names the second option first:

```text
usage: wordcount [--lines | --chars] FILE
wordcount: error: argument --chars: not allowed with argument --lines
```

`wordcount --chars --lines notes.txt` gives `wordcount: error: argument --lines: not allowed with argument --chars`. Both options give this error wherever they stand, for example `wordcount --lines notes.txt --chars`, and it comes before the check for a missing `FILE`. The other choice is a message of the project's own, such as `wordcount: error: give only one of --lines and --chars`. It reads more plainly, but it needs extra code, and every other usage error of the command uses argparse's own words.

- Return value: exit code 0 on success. Standard output holds the count as a decimal number with no sign, padding, or separator, followed by one line break, and standard error stays empty, as in F04 design 2.1.
  - Without a counting option, the count is what `count_words(FILE)` returns, as in F04.
  - With `--lines`, the count is what `count_lines(FILE)` returns (F02 design 2.1): `\n`, `\r\n`, and `\r` each end one line, a last line without a line break still counts, one byte order mark at the start is ignored, and an empty file has 0 lines (requirements Q2, Q3, Q5). So a file saved on Windows and the same file saved on Linux give the same count.
  - With `--chars`, the count is what `count_chars(FILE)` returns, as in F06 design 2.1.

Errors:

Every error leaves standard output empty and writes to standard error only. A file error with `--lines` gives exactly the message and exit code that `wordcount FILE` gives for the same file (requirements Q8): one line `wordcount: <FILE>: <reason>`, followed by one line break, and exit code 2. `<FILE>` and the five reason texts are those of F04 design 2.1, unchanged.

| Error | When |
| --- | --- |
| Exit code 2, reason `no such file` | As in F04 design 2.1: no file or folder exists at `FILE`, `FILE` is the empty string, or a folder in the path is missing or is a file. |
| Exit code 2, reason `is a folder` | As in F04 design 2.1: `FILE` names a folder. |
| Exit code 2, reason `permission denied` | As in F04 design 2.1: the process may not read the file. |
| Exit code 2, reason `not valid UTF-8` | As in F04 design 2.1: the file content is not valid UTF-8. With `--lines`, the command decodes the whole file, so a file whose invalid bytes come after valid text is still this error, and no count is printed. |
| Exit code 2, reason `cannot read file` | As in F04 design 2.1: any other `OSError` while the file is opened or read. |
| Exit code 2, usage line, both options | The command line holds both `--lines` and `--chars`, in any order and at any place. Standard error holds the usage line and message of proposal 2. |
| Exit code 2, usage line, other cases | The command line holds no `FILE`, more than one argument, an option other than `--lines` and `--chars`, a shortened option such as `--line`, `-l`, `-h`, or `--lines=VALUE`. argparse writes the usage line of proposal 1 and then one line `wordcount: error: <message>` in argparse's own words, for example `wordcount: error: the following arguments are required: FILE` for `wordcount --lines`, or `wordcount: error: unrecognized arguments: -l` for `wordcount -l notes.txt`. |

Any other exception is a bug, as in F04: Python writes the traceback to standard error and exits with code 1 (architecture section 6).

**Landing order.** F06's code is built at the same time and is not merged yet. Whichever of F05 and F06 lands second keeps the option of the other. This design describes the command once both have landed. If F05's code lands first, then until F06's code lands the set of counting options holds only `--lines`, `--chars` is an unknown option, and argparse writes the usage line `usage: wordcount [--lines] FILE`. F06's code then adds `--chars` to the set, and the usage line becomes the line of proposal 1. If F06's code lands first, F05's code adds `--lines` to F06's set, before `--chars`.

- Side effects: As in F04 design 2.1: the command opens `FILE` for reading and closes it before it exits, writes only to standard output and standard error, and writes, sends, and stores nothing. The option exists only after the project is installed again once F05 lands, for example with `uv pip install -e . --no-deps`.
- Performance target: None

Example:

`notes.txt` in the current folder is UTF-8 and holds the two lines `Hello world` and `  troy-mode  trial`, each ending with `\n`. `windows.txt` holds the same two lines, each ending with `\r\n`. `latin1.txt` holds `café au lait` in Latin-1.

```text
PS> wordcount --lines notes.txt
2
PS> wordcount notes.txt --lines
2
PS> wordcount --lines windows.txt
2
PS> wordcount notes.txt
4
PS> wordcount --lines missing.txt
wordcount: missing.txt: no such file
PS> $LASTEXITCODE
2
PS> wordcount --lines latin1.txt
wordcount: latin1.txt: not valid UTF-8
PS> $LASTEXITCODE
2
PS> wordcount --lines --chars notes.txt
usage: wordcount [--lines | --chars] FILE
wordcount: error: argument --chars: not allowed with argument --lines
PS> $LASTEXITCODE
2
PS> wordcount -l notes.txt
usage: wordcount [--lines | --chars] FILE
wordcount: error: unrecognized arguments: -l
PS> $LASTEXITCODE
2
```

### 2.2 `main`

- Module: cli, in `src/troy_mode_trial/cli.py`, as in F04 design 2.2. Tests import it as `from troy_mode_trial.cli import main`.
- Purpose: Runs the `wordcount` command of section 2.1 once: reads the arguments, counts the file through `count_words`, through `count_lines` when the arguments hold `--lines`, or through `count_chars` when they hold `--chars`, writes the result or the error, and returns the exit code. It imports the three functions from the package `troy_mode_trial`, never from `troy_mode_trial.counting` (architecture section 4).

Signature:

```python
def main(argv: Sequence[str] | None = None) -> int:
```

The signature does not change. `Sequence` is `collections.abc.Sequence`.

Parameters:

| Name | Type | Meaning | Constraints |
| --- | --- | --- | --- |
| `argv` | `Sequence[str] \| None` | The command-line arguments after the program name, for example `["--lines", "notes.txt"]` or `["notes.txt"]`. `None` means `sys.argv[1:]`, which is what the console script passes. | Each item is a `str`. The rules for the arguments are those of `--lines`, `--chars`, and `FILE` in section 2.1. |

- Return value: `int`, the exit code, as in F04 design 2.2. `0` after it wrote the count of section 2.1 and one line break to standard output. `2` after it wrote one line `wordcount: <FILE>: <reason>` to standard error. The program name in every message is `wordcount`, whatever `sys.argv[0]` holds.

Errors:

| Error | When |
| --- | --- |
| `SystemExit` with code 2 | The arguments are wrong, as the two usage rows of the Errors table in section 2.1 describe, including `--lines` with `--chars`. argparse writes the usage line and its message to standard error and raises `SystemExit(2)`, so `main` does not return. |
| Any other exception | A bug. `main` catches only `OSError` and its subclasses and `UnicodeDecodeError` from `count_words`, `count_lines`, or `count_chars`, and lets every other exception reach the caller. |

- Side effects: As in F04 design 2.2: writes with `sys.stdout.write` and `sys.stderr.write`, not `print()` (architecture section 8), reads the file as section 2.1 says, and changes no global state, so a test may call it several times in one process.
- Performance target: None

Example:

`notes.txt` is the file of the example in section 2.1.

```python
>>> from troy_mode_trial.cli import main
>>> main(["--lines", "notes.txt"])
2
0
>>> main(["notes.txt"])
4
0
>>> main(["--lines", "missing.txt"])  # writes to standard error
wordcount: missing.txt: no such file
2
>>> main(["--chars", "--lines", "notes.txt"])
usage: wordcount [--lines | --chars] FILE
wordcount: error: argument --lines: not allowed with argument --chars
Traceback (most recent call last):
  ...
SystemExit: 2
```

## 3. Changes to existing interfaces

Requirements 5.0 added F05 as a new feature, with the option `--lines` and the decisions Q7 to Q9, in the merged [docs] PR "[docs] Change the requirements: add the wordcount --lines option" (commit `eb369e0`). Requirements 6.0 added decision Q13, two counting options in one command are a usage error, in the merged [docs] PR "[docs] Change the requirements: add the wordcount --chars option" (#63, commit `fc2bb26`). F04 is accepted, so F05 changes its interfaces only as follows:

1. `wordcount` (F04 design 2.1) gains the option `--lines`. `wordcount FILE` without an option prints the same count, the same error lines, and the same exit codes as before, and `wordcount --chars FILE` behaves as F06's design says.
2. The usage line becomes `usage: wordcount [--lines | --chars] FILE`, if Troy accepts proposal 1 in section 2.1. It replaces F04's `usage: wordcount FILE` and F06's `usage: wordcount [--chars] FILE`. The rest of every usage error stays: exit code 2, empty standard output, and a second line `wordcount: error: <message>`. Once both F05 and F06 have landed, these expected usage lines change to `usage: wordcount [--lines | --chars] FILE`, and nothing else in them:
   - F04's test plan: the definition of a usage error, whose first line is exactly `usage: wordcount FILE`, and so the cases that rely on it, F04-T11, F04-T12, F04-T13, and F04-T21. F04-T13 also checks the line word for word. In `tests/test_cli.py` these are the helper `_assert_usage` and the checks in `test_f04_t13_program_name` and `test_f04_t21_program_usage`. F06's test plan PR changes the same line to `usage: wordcount [--chars] FILE` first (F06 design section 3). Whichever line those cases expect at that time changes to the new one.
   - F06's test plan, which is not merged yet: every case that expects the first line `usage: wordcount [--chars] FILE`, such as the design's examples for `--char` and for `--chars` with no file.
   - F06's design shows `usage: wordcount [--chars] FILE` in sections 2.1 and 2.2, as the line of the command while `--chars` was its only option. Its section 3 already says that the feature that lands second shows both options, so this design does not change F06's design.
   - The v0.2 and v0.3 version test plans check only that standard error starts with `usage:`, so they do not change.
3. A usage error for `--lines` with `--chars` replaces the earlier `unrecognized arguments: --lines` that F06 alone would give. Its message is that of proposal 2 in section 2.1. A case in F06's test plan that expects `unrecognized arguments: --lines` changes its expected second line to that message once both features have landed.
4. `main` (F04 design 2.2) keeps its signature. It now accepts `--lines` in `argv` and then calls `count_lines`.
5. `src/troy_mode_trial/__init__.py` does not change. It already exports `count_lines` (F02 design 2.1). `count_words`, `count_lines`, and `count_chars` keep their signatures, behavior, and errors.

## 4. Architect review

| Item | Result | Note |
| --- | --- | --- |
| Fits the module layout and the data model | Pass | `wordcount` and `main` stay in cli, in `src/troy_mode_trial/cli.py`. F05 adds no library function and no file under `src/troy_mode_trial/`: `main` calls F02's `count_lines`, which `src/troy_mode_trial/__init__.py`, counting's external interface, already exports. `main` imports the three counting functions from the package, as architecture section 4 asks. The set of counting options that exclude each other is an argparse mutually exclusive group, which is still the standard library (ADR-0001), so the design adds no dependency and needs no architecture change. The architecture defines no data model. |
| Follows the error handling and naming conventions | Pass | `main` still catches only `OSError` and its subclasses and `UnicodeDecodeError`, now around `count_lines` too, and for `--lines` writes the same line `wordcount: <FILE>: <reason>` with exit code 2 (architecture section 6, ADR-0002, requirements Q8). A wrong command line, including `--lines` with `--chars`, exits with code 2 and a usage line (requirements Q13), code 1 still means only a bug, and standard output holds only the count and one line break, written with `write` (section 8). The option name follows `--chars`. In round 1 I ran argparse (Python 3.14.3; the project's Python 3.13 environment was not on this machine) with `prog="wordcount"`, `add_help=False`, `allow_abbrev=False`, a mutually exclusive group of `--lines` then `--chars`, and `FILE`. It gives the usage line `usage: wordcount [--lines \| --chars] FILE` and the messages `argument --chars: not allowed with argument --lines` for `--lines --chars notes.txt`, for `--lines notes.txt --chars`, and for `--lines --chars` with no file, and `argument --lines: not allowed with argument --chars` for `--chars --lines notes.txt`, all with exit code 2, as proposals 1 and 2 state. It also gives the outcome the design states for `--lines FILE`, `FILE --lines`, `--lines --lines`, `--lines -- -n.txt`, `-- --lines`, `-l`, `--line`, `--li`, `-h`, `--lines=x`, `--lines` with no file, and two files. With `--lines` as the group's only member, the usage line is `usage: wordcount [--lines] FILE` and `--chars` is an unrecognized argument, as the landing-order paragraph says. The line counts in the examples are right by F02's rules. |
| Does not duplicate an existing interface | Pass | F05 adds no counting function. `main` counts lines only through `count_lines` and counts nothing itself, so the line rules stay in one place. |
| Depends only on features earlier in the order | Pass | F05 depends on F02 and F04, and builds on F06's approved design. All three come before F05 in the order (F01, F03, F04, F06, F02, F05). F02 and F04 are usable on Troy's devices. F06's code is not merged, and the landing-order paragraph covers both orders, so F05 does not wait for F06's code. |
| Adds no hidden coupling between modules | Pass | cli relies only on what `count_lines` documents: its signature, its `int` result, and the exceptions in F02's table, which architecture section 6 already names. The exclusive set of options lives in cli, and counting knows nothing about options. `src/troy_mode_trial/__init__.py` does not change and still does not import cli. `main` keeps no global state. |
| Changes an implemented interface only through the change flow | Pass | F04 and F02 are accepted. Requirements 5.0 (commit `eb369e0`) added `--lines` to F04's command, and requirements 6.0 (#63, commit `fc2bb26`) added Q13, both approved by Troy, so the change comes through the requirement change flow. Section 3 lists every change: the option, the new usage line if Troy accepts proposal 1, the message for both options, the unchanged signature of `main`, and the unchanged `__init__.py` and counting functions. I checked F04's test plan and `tests/test_cli.py`. The helper `_assert_usage` and the checks in `test_f04_t13_program_name` and `test_f04_t21_program_usage` are the only places that hold `usage: wordcount FILE`. The v0.2 and v0.3 version test plans check only that standard error starts with `usage:`. F06's design is not implemented and does not change. |
| The summary for Troy says what the design says, and lists every point Troy decides | Pass | The summary matches the design: the line count and its rules for Windows and Linux line ends, a last line without a line break, and an empty file; the words and `--chars` unchanged; the same error line and exit code 2 for file errors; full name only, before or after the file; both options a usage error; install again. Its two points are proposals 1 and 2 of section 2.1, in the same order, each with the design's recommendation and reason, and its two risks match the landing-order paragraph with section 3, and proposal 2. The design has no other open choice. I ran troy-check's R22 functions on the summary in the brief: no problem found, about 960 characters in Chinese and 1,930 in English, and no internal IDs. |

| Round | Issue | Resolution |
| --- | --- | --- |
| 1 | No blocking finding. The Interface Designer asked me to confirm the usage line and the message by running argparse: both are confirmed, as the second row of the checklist says. Notes, which do not block. For the Interface Designer: the summary leaves out that one byte order mark at the start is ignored, which section 2.1 says. It is the same rule as for words, so the summary needs no change, and the English part has only about 70 characters left. For the Developer: add `--lines` to the mutually exclusive group before `--chars`, with `allow_abbrev=False` on the parser, so that the usage line reads as proposal 1 whichever feature lands second. Update the usage line in the doc comments of `_build_parser` and `main`, and keep `main` within 50 lines (R04), for example with a helper that picks the counting function. For the Test Manager: F04-T12 also relies on the usage-error definition, so it changes through `_assert_usage` with F04-T11, F04-T13, and F04-T21. Whichever of F05 and F06 lands its test PR second updates the expected usage line to the line of proposal 1. | Approved in round 1. |

## 5. Change log

| Version | Date | Change |
| --- | --- | --- |
| 0.1 | 2026-11-23 | First draft. |
| 1.0 | 2026-11-23 | Approved by Troy. |
