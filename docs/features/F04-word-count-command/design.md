---
troy-doc: "F04-design"
lang: "en"
version: "1.0"
updated: "2026-11-14"
status: "Approved by Troy on 2026-11-14"
mirror: "design.zh-CN.md"
---

# F04 Word count command: interface design

## 1. Feature

- ID and name: F04 Word count command
- Requirement: [docs/requirements.md](../../requirements.md#4-features)
- Hard dependencies: F03
- Soft dependencies: None

## 2. Interfaces

F04 adds two interfaces, both in the module cli, which owns the new file `src/troy_mode_trial/cli.py` (architecture section 3, ADR-0001). Section 2.1 is the command that Troy types. Section 2.2 is the function behind it, which the console script calls and which tests can call in the process.

### 2.1 `wordcount`

- Module: cli. `pyproject.toml` declares the command in its table `[project.scripts]` as `wordcount = "troy_mode_trial.cli:main"`. The installer (uv or pip) makes the program `wordcount`, `wordcount.exe` on Windows, in the environment's scripts folder.
- Purpose: Prints the number of words in one UTF-8 text file, counted as F03 counts them, so that Troy can count words in PowerShell or any other shell without writing Python.

Signature:

```text
usage: wordcount FILE
```

Parameters:

| Name | Type | Meaning | Constraints |
| --- | --- | --- | --- |
| `FILE` | One command-line argument | The path of the file to count, absolute or relative to the current working directory. | Exactly one argument. It names one existing, readable, regular file whose content is valid UTF-8. A path that holds a space is quoted as the shell asks, for example `wordcount 'my notes.txt'` in PowerShell. A path that starts with `-` follows `--`, for example `wordcount -- -notes.txt`, because argparse otherwise reads such an argument as an option. |

The command has no options (requirements section 8). It has no `-h` or `--help` either: `wordcount -h` is a wrong command line, as the Errors table describes.

- Return value: exit code 0, and standard output holds the count as a decimal number with no sign, padding, or separator, followed by one line break. The count is exactly what `count_words(FILE)` returns (F01 design 2.1 as F03 design 3.1 changed it). Standard error stays empty. Python writes the line break as `\n` on Linux and as `\r\n` on Windows.

Errors:

Every error leaves standard output empty and writes to standard error only. For a file error, the command writes exactly one line, `wordcount: <FILE>: <reason>`, followed by one line break, and exits with code 2. Troy decided code 2 on PR #39, because his scripts treat 2 as an error; the prototype shows code 1. `<FILE>` is the argument as the program received it, after the shell has removed any quotes, not an absolute path. `<reason>` is one of the fixed texts below, the same on Windows and on Linux. A file error and a wrong command line both exit with code 2, and only the text on standard error tells them apart. The prototype gives only `no such file`. The other four reason texts, and `is a folder` instead of `permission denied` for a folder on Windows, are this design's proposal, and Troy accepts or changes them.

| Error | When |
| --- | --- |
| Exit code 2, reason `no such file` | No file or folder exists at `FILE`, `FILE` is the empty string, or a folder in the path is missing or is a file. In Python: `FileNotFoundError`, or `NotADirectoryError`. |
| Exit code 2, reason `is a folder` | `FILE` names a folder. In Python: `IsADirectoryError` on Linux, and `PermissionError` on Windows for a path that names an existing folder. |
| Exit code 2, reason `permission denied` | The process may not read the file. In Python: `PermissionError` for a path that does not name a folder. |
| Exit code 2, reason `not valid UTF-8` | The file content is not valid UTF-8. In Python: `UnicodeDecodeError`. |
| Exit code 2, reason `cannot read file` | Any other `OSError` while the file is opened or read, for example a name that Windows does not allow, such as `a?b.txt`. |
| Exit code 2, usage line | The command line holds no `FILE`, more than one argument, or an argument that argparse reads as an option, such as `-h`. argparse writes the usage line `usage: wordcount FILE` and then one line `wordcount: error: <message>`, for example `wordcount: error: the following arguments are required: FILE` or `wordcount: error: unrecognized arguments: notes.txt`. The message text is argparse's own. |

Any other exception is a bug (architecture section 6). The command does not catch it: Python writes the traceback to standard error and exits with code 1. So code 1 means a bug, and never a file error or a wrong command line. A Ctrl+C is not caught either.

- Side effects: The command opens `FILE` for reading and closes it before it exits. It writes only to standard output and standard error. It writes no file, and sends and stores nothing (requirements section 7). The command exists only after the project is installed again once F04 lands, for example with `uv pip install -e . --no-deps`, and PowerShell finds it only while the environment `troy-mode-trial` is active or its scripts folder is on `PATH` (ADR-0001, Consequences).
- Performance target: None

Example:

`notes.txt` in the current folder is UTF-8 and holds the two lines `Hello world` and `  troy-mode  trial`. `latin1.txt` holds `café au lait` in Latin-1.

```text
PS> wordcount notes.txt
4
PS> wordcount missing.txt
wordcount: missing.txt: no such file
PS> $LASTEXITCODE
2
PS> wordcount latin1.txt
wordcount: latin1.txt: not valid UTF-8
PS> $LASTEXITCODE
2
PS> wordcount
usage: wordcount FILE
wordcount: error: the following arguments are required: FILE
PS> $LASTEXITCODE
2
```

### 2.2 `main`

- Module: cli, in `src/troy_mode_trial/cli.py`. The console script of section 2.1 is its only caller in the product. No module imports cli, and `src/troy_mode_trial/__init__.py` does not import it (architecture section 4). Tests import it as `from troy_mode_trial.cli import main`.
- Purpose: Runs the `wordcount` command of section 2.1 once: reads the arguments, counts the words of the file through `count_words`, which it imports from the package `troy_mode_trial`, writes the result or the error, and returns the exit code.

Signature:

```python
def main(argv: Sequence[str] | None = None) -> int:
```

`Sequence` is `collections.abc.Sequence`.

Parameters:

| Name | Type | Meaning | Constraints |
| --- | --- | --- | --- |
| `argv` | `Sequence[str] \| None` | The command-line arguments after the program name, for example `["notes.txt"]`. `None` means `sys.argv[1:]`, which is what the console script passes. | Each item is a `str`. The rules for the arguments are those of `FILE` in section 2.1. |

- Return value: `int`, the exit code. `0` after it wrote the count and one line break to standard output. `2` after it wrote one line `wordcount: <FILE>: <reason>` to standard error, with the reasons of section 2.1. The console script passes the returned code to `sys.exit`. The program name in every message is `wordcount`, whatever `sys.argv[0]` holds.

Errors:

| Error | When |
| --- | --- |
| `SystemExit` with code 2 | The arguments are wrong, as the last row of the Errors table in section 2.1 describes. argparse writes the usage line and its message to standard error and raises `SystemExit(2)`, so `main` does not return. |
| Any other exception | A bug. `main` catches only `OSError` and its subclasses and `UnicodeDecodeError` from counting, and lets every other exception reach the caller. |

- Side effects: Writes to `sys.stdout` and `sys.stderr` with their `write` methods, not with `print()` (architecture section 8), and reads the file as section 2.1 says. It changes no global state, so a test may call it several times in one process.
- Performance target: None

Example:

`notes.txt` is the file of the example in section 2.1.

```python
>>> from troy_mode_trial.cli import main
>>> main(["notes.txt"])
4
0
>>> main(["missing.txt"])  # writes to standard error
wordcount: missing.txt: no such file
2
>>> main([])
usage: wordcount FILE
wordcount: error: the following arguments are required: FILE
Traceback (most recent call last):
  ...
SystemExit: 2
```

## 3. Changes to existing interfaces

None. Requirements 4.0 added F04 as a new feature in the merged [docs] PR [#36](https://github.com/ZJUCao/troy-mode-trial/pull/36), and architecture 2.0 added the module cli in [#37](https://github.com/ZJUCao/troy-mode-trial/pull/37). `count_words` keeps its signature, behavior, and errors, and `src/troy_mode_trial/__init__.py` keeps its exports and does not import cli. No existing test case changes or retires.

## 4. Architect review

| Item | Result | Note |
| --- | --- | --- |
| Fits the module layout and the data model | Pass | Both interfaces belong to the module cli, which owns `src/troy_mode_trial/cli.py` (architecture section 3, ADR-0001). The design adds no other file under `src/troy_mode_trial/`. `main` reaches counting only through the package `troy_mode_trial`, as section 4 of the architecture asks, and nothing imports cli. The console script entry `wordcount = "troy_mode_trial.cli:main"` is the one in the tech stack, and hatchling is already the build backend. The architecture defines no data model, and the command keeps no data. |
| Follows the error handling and naming conventions | Pass | `main` catches only `OSError` and its subclasses and `UnicodeDecodeError`, and only around the counting call. For a file error it writes one line `wordcount: <FILE>: <reason>` to standard error and returns 2, as architecture 3.0 section 6 and ADR-0002 ask. It lets argparse exit with code 2 and a usage line, returns 0 on success, and lets every other exception through, so that Python exits with code 1. These are the exit codes that ADR-0002 lists: 0 for a count, 2 for a file error or a wrong command line, and 1 for a bug only. Section 2.1 also says that only standard error tells a file error from a wrong command line, as section 6 says. Standard output holds only the count and one line break, and output uses `write`, not `print()` (section 8). The design fixes the reason texts and the signature of `main`, as section 6 leaves to it. `main` and `argv` follow Python's naming. In round 1 I ran argparse with no file, two files, `-h`, and `-- -n.txt`: each gives the usage line, message, and exit code that the design states. |
| Does not duplicate an existing interface | Pass | The project has no command-line interface yet. `main` counts through the existing `count_words` and does not count words itself. |
| Depends only on features earlier in the order | Pass | F04 depends only on F03, and through it on F01. Both come before F04 in the order (F01, F03, F04, F02) and are usable on Troy's devices. F04 does not use F02. |
| Adds no hidden coupling between modules | Pass | cli relies only on what `count_words` documents: its signature, its `int` result, and its exceptions, of which `NotADirectoryError` and the other `OSError` cases are subclasses that the architecture already names. The check whether a path names a folder, for a `PermissionError` on Windows, stays in cli. `main` keeps no global state, and the package `__init__.py` does not import cli. |
| Changes an implemented interface only through the change flow | Pass | No implemented interface changes. `count_words` and the exports of `src/troy_mode_trial/__init__.py` stay as they are, and no test case changes. The new `[project.scripts]` table comes from architecture 2.0, which Troy approved in [docs] PR #37. The exit code for a file error changes only in this design's draft, not in an implemented interface, and the architecture changed first: Troy approved architecture 3.0 and ADR-0002 in [docs] PR #40. |
| The summary for Troy says what the design says, and lists every point Troy decides | Pass | The summary matches section 2: the output, the error line with exit code 2 for every file error and the message unchanged, the usage line also with exit code 2, code 1 for a bug only, `-h`, `--`, the file name as typed, the unchanged counting function, and the need to install again. Its risks match too: the scripts folder on `PATH`, the shared code 2 that only the message tells apart, and the prototype's code 1, which section 2.1 records. The one point Troy decides, the five reason texts with `is a folder` on Windows, is the one the design marks as its proposal, with a recommendation. The design has no other open choice. Each language is under 2,000 characters, about 1,740 in English and 890 in Chinese, and holds no internal IDs; the feature ID F04 is allowed. |

| Round | Issue | Resolution |
| --- | --- | --- |
| 1 | No blocking finding. Three notes, which do not block. For the Interface Designer, if the design changes for another reason: the summary's risk could add that the command is also found when the environment's scripts folder is on `PATH`, as section 2.1 says. For the Developer: build the parser inside `main` with `prog="wordcount"` and `add_help=False`, and keep `main` within 50 lines (R04), for example with a private helper that maps an exception to its reason text. On Windows, check whether the path names a folder only after a `PermissionError`. For the Test Manager: the `is a folder` and `permission denied` cases differ between Windows and Linux, so the test plan needs a case for each system or a skip with its reason. | Approved in round 1. |
| 2 | No blocking finding. Version 0.2 makes every file error exit with code 2 instead of 1, with the same message line, as Troy asked on PR #39. This matches architecture 3.0 and ADR-0002, merged in #40. I rewrote the notes of items 2, 6, and 7, which still said exit code 1. Two notes, which do not block. For the Interface Designer, if the design changes for another reason: section 2.1 or section 3 could cite ADR-0002 and architecture 3.0 (#40) next to PR #39, as section 3 cites #36 and #37. For the Test Manager: F04's test plan expects code 2 for every file error, and a test tells a file error from a wrong command line only by standard error. | Approved in round 2. |

## 5. Change log

| Version | Date | Change |
| --- | --- | --- |
| 0.1 | 2026-11-14 | First draft. |
| 0.2 | 2026-11-14 | Troy's change on PR #39: every file error exits with code 2 instead of 1, with the same message line. Said that code 1 now means only a bug, and that the text on standard error tells a file error from a wrong command line. |
| 1.0 | 2026-11-14 | Approved by Troy. |
