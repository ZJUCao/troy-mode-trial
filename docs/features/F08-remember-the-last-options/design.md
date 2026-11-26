---
troy-doc: "F08-design"
lang: "en"
version: "1.0"
updated: "2026-11-26"
status: "Approved by Troy on 2026-11-26"
mirror: "design.zh-CN.md"
---

# F08 Remember the last options: interface design

## 1. Feature

- ID and name: F08 Remember the last options
- Requirement: [docs/requirements.md](../../requirements.md#4-features)
- Hard dependencies: F04
- Soft dependencies: None

## 2. Interfaces

F08 adds the module settings, which owns the new file `src/troy_mode_trial/settings.py` (architecture section 3, ADR-0003). Section 2 holds only the new interfaces: the settings file's format in section 2.1, and the external interface of settings in sections 2.2 to 2.6. Section 3 lists the changes to `wordcount` and `main` in the module cli, which gain the option `--again`.

settings is used only by cli. `src/troy_mode_trial/__init__.py` does not import it and exports nothing from it (architecture section 4), so the library still writes no file. Tests import the names below as `from troy_mode_trial.settings import ...`.

The saved values are the names in one tuple, `OPTION_NAMES` (section 2.2). F09 adds `sentences` to that tuple. `load_option` and `save_option` then accept it with no other change to settings, and the file format of section 2.1 does not change.

Two points in this design are proposals that Troy accepts or changes, and each says so where it stands: the new usage line (section 3.1, proposal 1), and the three texts of the settings error and warning (section 3.1, proposal 2).

### 2.1 The settings file

- Module: settings. Only settings opens this file, for reading in `load_option` and for writing in `save_option` (architecture section 8).
- Purpose: Keeps the option of the last `wordcount` run that printed a count, or that it had none, so that `wordcount --again FILE` can count with it (requirements F08, architecture section 5).

Signature:

```json
{"option": "lines"}
```

The file is UTF-8 JSON: one object with exactly one key, `"option"`. Where the file is: section 2.3.

Parameters:

| Name | Type | Meaning | Constraints |
| --- | --- | --- | --- |
| `"option"` | JSON string or `null` | The counting option of the last run that printed a count, without its leading `--`. `null` means that run had no counting option, so it counted words. | `null`, or exactly one of the names in `OPTION_NAMES` (section 2.2): `"lines"`, `"chars"`, or `"longest"`. Names are lowercase and match exactly. F09 adds `"sentences"`. |

- Return value: None. The file is data, not a call.

  `save_option` writes the content as these exact bytes, with no byte order mark and with a `\n` line end on every system:

  | Last run | Bytes of the file |
  | --- | --- |
  | `wordcount FILE` | `{"option": null}` then `\n` |
  | `wordcount --lines FILE` | `{"option": "lines"}` then `\n` |
  | `wordcount --chars FILE` | `{"option": "chars"}` then `\n` |
  | `wordcount --longest FILE` | `{"option": "longest"}` then `\n` |

  `load_option` also accepts these contents with white space between the JSON tokens, and with one byte order mark at the start, so a file that Troy saves in a text editor still reads. It rejects every form that the Errors table below lists, which is the one rule for a file that cannot be read.

Errors:

Content that is not a saved option is a settings file that cannot be read (requirements Q20, architecture section 5). `load_option` raises `ValueError` for it (section 2.5).

| Error | When |
| --- | --- |
| Cannot be read | The bytes are not valid UTF-8. |
| Cannot be read | The text is not valid JSON, for example an empty file or `{"option": "lines"` with no closing brace. |
| Cannot be read | The JSON is not an object, for example `"lines"` or `[]`. |
| Cannot be read | The object has no key, a key other than `"option"`, or a second key, for example `{}`, `{"Option": "lines"}`, or `{"option": "lines", "file": "a.txt"}`. |
| Cannot be read | The object has the key `"option"` more than once, also with the same value, for example `{"option": "lines", "option": "chars"}` or `{"option": null, "option": null}`. Python's `json` module would keep only the last value, so `load_option` checks every key that the text holds, not only the object that `json` returns. |
| Cannot be read | The value is not `null` and not a name in `OPTION_NAMES`, for example `"--lines"`, `"Lines"`, `"sentences"` before F09, `true`, `1`, or `[]`. |

- Side effects: None. What the file never holds: a file name, a path, a count, or text from a file (requirements Q18).
- Compatibility: The format outlives each version of the program (architecture section 5). A version that knows more names, such as F09's `sentences`, reads every file that F08 writes. F08's program reads a file with `"sentences"` as a file that cannot be read, so `wordcount --again` then gives the settings error of section 3.1, and the next run that prints a count writes the file again in F08's format.
- Performance target: None

Example:

```text
PS> wordcount --longest notes.txt
9
PS> Get-Content $env:APPDATA\wordcount\settings.json
{"option": "longest"}
PS> wordcount notes.txt
4
PS> Get-Content $env:APPDATA\wordcount\settings.json
{"option": null}
```

### 2.2 `OPTION_NAMES`

- Module: settings, in `src/troy_mode_trial/settings.py`.
- Purpose: The names that the settings file may hold as its `"option"` value, besides `null`. It is the one place that lists them, so F09 extends the saved values by adding one name here.

Signature:

```python
OPTION_NAMES: Final[tuple[str, ...]] = ("lines", "chars", "longest")
```

`Final` is `typing.Final`.

Parameters: None

- Return value: None. It is a constant: a tuple of lowercase option names without the leading `--`, in the order of the command's usage line. F09 appends `"sentences"`.

Errors: None

- Side effects: None
- Performance target: None

Example:

```python
>>> from troy_mode_trial.settings import OPTION_NAMES
>>> OPTION_NAMES
('lines', 'chars', 'longest')
```

### 2.3 `settings_path`

- Module: settings, in `src/troy_mode_trial/settings.py`.
- Purpose: Works out the path of the settings file from the environment of the running process (requirements Q17, architecture section 5).

Signature:

```python
def settings_path() -> pathlib.Path:
```

Parameters: None. The function reads `sys.platform` and the environment variables below at each call and caches nothing, so a test that changes them sees the change at the next call.

- Return value: `pathlib.Path`, the absolute path of the settings file. The function only builds the path. It does not check whether the file or its folder exists, and it does not resolve links or `..`.

  | System | Environment | Result |
  | --- | --- | --- |
  | Windows (`sys.platform == "win32"`) | `APPDATA` is an absolute path, for example `C:\Users\me\AppData\Roaming` | `C:\Users\me\AppData\Roaming\wordcount\settings.json` |
  | Any other | `XDG_DATA_HOME` is an absolute path, for example `/data` | `/data/wordcount/settings.json` |
  | Any other | `XDG_DATA_HOME` is unset, empty, or not an absolute path, and the home folder is `/home/me` | `/home/me/.local/share/wordcount/settings.json` |

  On Windows, the function ignores `XDG_DATA_HOME`. Elsewhere, it ignores `APPDATA`. The home folder is what `pathlib.Path.home()` returns.

Errors:

The function defines no exception of its own (architecture section 6).

| Error | When |
| --- | --- |
| `ValueError` | On Windows, `APPDATA` is unset, empty, or not an absolute path. Elsewhere, `XDG_DATA_HOME` gives no absolute path and the home folder cannot be found or is not an absolute path. `pathlib.Path.home()` raises `RuntimeError` when it cannot find the home folder, and the function raises `ValueError` instead, so callers catch only `OSError` and `ValueError`. The message says which variable is missing, but callers do not read it. |

- Side effects: None. It reads the environment only.
- Performance target: None

Example:

```python
>>> import os
>>> from troy_mode_trial.settings import settings_path
>>> os.environ["APPDATA"] = r"C:\Users\me\AppData\Roaming"  # on Windows
>>> settings_path()
WindowsPath('C:/Users/me/AppData/Roaming/wordcount/settings.json')
>>> del os.environ["APPDATA"]
>>> settings_path()
Traceback (most recent call last):
  ...
ValueError: APPDATA is not set to an absolute path
```

### 2.4 `settings_name`

- Module: settings, in `src/troy_mode_trial/settings.py`.
- Purpose: Gives the name of the settings file for an error or warning line, also when `settings_path` cannot work the path out (requirements Q20 and Q22: the line names the settings file).

Signature:

```python
def settings_name() -> str:
```

Parameters: None

- Return value: `str`. When `settings_path()` returns a path, the result is `str()` of that path, for example `C:\Users\me\AppData\Roaming\wordcount\settings.json` on Windows or `/home/me/.local/share/wordcount/settings.json` on Linux. When `settings_path()` raises `ValueError`, the result is the fixed text `%APPDATA%\wordcount\settings.json` on Windows, or `~/.local/share/wordcount/settings.json` elsewhere, so the line still tells Troy which file it means.

Errors: None. The function never raises for any environment.

- Side effects: None. It reads the environment only.
- Performance target: None

Example:

```python
>>> from troy_mode_trial.settings import settings_name
>>> settings_name()  # on Windows, with APPDATA set
'C:\\Users\\me\\AppData\\Roaming\\wordcount\\settings.json'
>>> settings_name()  # on Windows, with APPDATA unset
'%APPDATA%\\wordcount\\settings.json'
```

### 2.5 `load_option`

- Module: settings, in `src/troy_mode_trial/settings.py`.
- Purpose: Reads the saved option from the settings file, for `wordcount --again`.

Signature:

```python
def load_option(path: pathlib.Path) -> str | None:
```

Parameters:

| Name | Type | Meaning | Constraints |
| --- | --- | --- | --- |
| `path` | `pathlib.Path` | The settings file to read. cli passes what `settings_path()` returned. Tests pass a file in a temporary folder. | Any path. The function does not check that it is the path of section 2.3. |

- Return value: `str | None`. A name from `OPTION_NAMES` when the file holds that name, or `None` when the file holds `null`, which means the last run had no counting option and `--again` counts words. The function reads the whole file, decoding it as UTF-8 with one byte order mark at the start removed, and checks it against section 2.1.

Errors:

The function defines no exception of its own. It lets `OSError` and its subclasses through, and raises `ValueError` for content that is not a saved option (architecture section 6). A missing file means no saved option. It raises `FileNotFoundError`, which cli tells apart from the other errors.

| Error | When |
| --- | --- |
| `FileNotFoundError` | No file exists at `path`, or a folder in the path is missing: no run has printed a count yet. |
| Another `OSError` | The file cannot be opened or read, for example `IsADirectoryError` or `PermissionError` when `path` names a folder, `PermissionError` when the process may not read it, or `NotADirectoryError` when a folder in the path is a file. |
| `ValueError` | The content is not a saved option, as the Errors table of section 2.1 lists. Invalid UTF-8 raises `UnicodeDecodeError` and broken JSON raises `json.JSONDecodeError`. Both are subclasses of `ValueError`, and the function lets them through as they are. |

- Side effects: Opens the file for reading and closes it before it returns or raises. It writes nothing.
- Performance target: None

Example:

```python
>>> from troy_mode_trial.settings import load_option, settings_path
>>> load_option(settings_path())  # the file holds {"option": "lines"}
'lines'
>>> load_option(settings_path())  # the file holds {"option": null}
>>> load_option(settings_path())  # no file yet
Traceback (most recent call last):
  ...
FileNotFoundError: [Errno 2] No such file or directory: '...settings.json'
```

### 2.6 `save_option`

- Module: settings, in `src/troy_mode_trial/settings.py`.
- Purpose: Writes the option of a run that printed a count to the settings file, so that a failed or interrupted write never leaves a half-written file (architecture section 5).

Signature:

```python
def save_option(path: pathlib.Path, option: str | None) -> None:
```

Parameters:

| Name | Type | Meaning | Constraints |
| --- | --- | --- | --- |
| `path` | `pathlib.Path` | The settings file to write. cli passes what `settings_path()` returned. | Any path whose parent folder is, or can be created as, a folder. |
| `option` | `str \| None` | The run's counting option without its leading `--`, or `None` for a run with no counting option. | `None`, or a name in `OPTION_NAMES`. |

- Return value: None. When the function returns, the file at `path` holds the exact bytes of section 2.1 for `option`.

  The function works in this order:

  1. It checks `option`. An unknown name raises `ValueError` before it touches any folder or file.
  2. It creates the parent folder of `path`, with any missing folders above it, when it is missing. On Linux this can create `~/.local/share` too.
  3. It writes the new content to a new temporary file in that folder, with a name that starts with `settings.` and ends with `.tmp`, and closes it.
  4. It replaces `path` with the temporary file through `os.replace`.

  When step 3 or 4 fails, the function removes its temporary file before it raises. The old settings file stays whole, or there is still no file (architecture section 5). When even the removal fails, a `settings.*.tmp` file can stay in the folder. `load_option` never reads it, and it does no harm.

Errors:

The function defines no exception of its own. It lets `OSError` and its subclasses through.

| Error | When |
| --- | --- |
| `ValueError` | `option` is neither `None` nor a name in `OPTION_NAMES`. cli passes only known names, so this means a bug in cli. |
| `OSError` | The folder cannot be created, the temporary file cannot be written, or the replace fails. For example: `PermissionError` when the folder is read-only, or when another program holds the settings file open on Windows; `FileExistsError` or `NotADirectoryError` when a file stands where a folder must be; `IsADirectoryError` or `PermissionError` when `path` names a folder; or a full disk. |

- Side effects: Creates the folder of `path` when it is missing, creates and then renames or removes one temporary file in it, and replaces the settings file. It always writes, also when the file already holds the same content, so the file's time shows the last run that printed a count.
- Performance target: None

Example:

```python
>>> from troy_mode_trial.settings import load_option, save_option, settings_path
>>> save_option(settings_path(), "chars")
>>> load_option(settings_path())
'chars'
>>> save_option(settings_path(), None)
>>> settings_path().read_bytes()
b'{"option": null}\n'
>>> save_option(settings_path(), "--chars")
Traceback (most recent call last):
  ...
ValueError: not a saved option name: '--chars'
```

## 3. Changes to existing interfaces

Requirements 8.0 added F08 as a new feature, with the option `--again` and Troy's decisions Q17 to Q22, in the merged [docs] PR "[docs] Change the requirements: remember the last options and count sentences" (commit `1c21dd6`). Architecture 4.0 and ADR-0003 added the module settings in the merged [docs] PR "[docs] Change the architecture for F08" (commit `ac1a71c`). F04, F05, F06, and F07 are accepted. F08 changes their interfaces `wordcount` (F04 design 2.1, as F07 design 2.1 left it) and `main` (F04 design 2.2) as sections 3.1 and 3.2 say. Section 3.3 lists the tests that change with them.

What does not change: the counting functions `count_words`, `count_lines`, `count_chars`, and `count_longest` keep their signatures, behavior, and errors. `src/troy_mode_trial/__init__.py` keeps its exports, and imports neither cli nor settings. `wordcount FILE`, `--lines`, `--chars`, and `--longest` print the same numbers, the same file error lines, and the same exit codes as before. The console script in `pyproject.toml` stays.

### 3.1 `wordcount`

1. **New option `--again`.** `wordcount --again FILE` counts `FILE` with the option that the settings file holds (section 2.1): words for `null`, and `--lines`, `--chars`, or `--longest` for their names. After `wordcount --lines a.txt`, `wordcount --again b.txt` prints the lines of `b.txt`, and after `wordcount a.txt` it prints the words (requirements F08).

   | Name | Type | Meaning | Constraints |
   | --- | --- | --- | --- |
   | `--again` | Option, a flag with no value | Count `FILE` with the saved option of the last run that printed a count. | Optional. Only the full name `--again`, with no short form and no shortened name such as `--ag`, as for the other options. It may come before or after `FILE`. Given twice, it works as given once. `--again=VALUE` is a wrong command line. It cannot come with `--lines`, `--chars`, or `--longest`, in any order (requirements Q21). |

   The command still has no `-h` or `--help`, and no option other than `--lines`, `--chars`, `--longest`, and `--again` (requirements section 8; F09 adds `--sentences`).

2. **Proposal 1, the usage line, for Troy to accept or change.** The usage line changes from `usage: wordcount [--lines | --chars | --longest] FILE` to:

   ```text
   usage: wordcount [--lines | --chars | --longest | --again] FILE
   ```

   `--again` joins the set of options that exclude each other, because a command takes at most one of them (requirements Q21). This is the form Troy approved for F05 and F07, and it is the line argparse writes for that set, so it needs no extra code. `--again` comes last, as in the requirements. The other choice puts `--again` in its own brackets, `usage: wordcount [--lines | --chars | --longest] [--again] FILE`, which hides that `--again` cannot come with the others.

3. **New usage error.** `--again` together with a counting option is a wrong command line with exit code 2 (requirements Q21). argparse writes the usage line of proposal 1 and one line in argparse's own words that names the later option first, as for two counting options (F05 design 2.1, approved). For example, `wordcount --lines --again notes.txt` gives `wordcount: error: argument --again: not allowed with argument --lines`, and `wordcount --again notes.txt --chars` gives `wordcount: error: argument --chars: not allowed with argument --again`. Every other usage error keeps its message, and its first line becomes the line of proposal 1. A usage error reads and writes no settings file.

4. **Order of a run with `--again`.** The command reads the settings file before it opens `FILE` (architecture section 6). So a settings error comes first, and such a run prints no count: `wordcount --again missing.txt` with no saved option gives the settings error, not `no such file`. With a saved option, a file error gives exactly the line and exit code that the same command without `--again` gives.

5. **Proposal 2, the texts of the settings error and warning, for Troy to accept or change.** Each text is one line on standard error, followed by one line break, with the program name `wordcount`. `<settings file>` is what `settings_name()` returns (section 2.4): the full path, such as `C:\Users\me\AppData\Roaming\wordcount\settings.json`, or `%APPDATA%\wordcount\settings.json` when `APPDATA` is not set. The first text is the one in F08's prototype. The texts are the same on Windows and on Linux.

   | Line | When | Exit code |
   | --- | --- | --- |
   | `wordcount: no saved options to run again: <settings file>` | `--again`, and no settings file exists yet, because no run has printed a count (requirements Q20). `load_option` raised `FileNotFoundError`. | 2 |
   | `wordcount: cannot read the settings file: <settings file>` | `--again`, and the settings file cannot be read: its content is not a saved option (section 2.1), it cannot be opened, or `settings_path()` cannot work out its path (requirements Q20). | 2 |
   | `wordcount: warning: cannot write the settings file: <settings file>` | A run printed its count, and then the settings file could not be written, or `settings_path()` could not work out its path (requirements Q22). | 0 |

   Standard output is empty after either error. After the warning, standard output holds the count and one line break, as on success, and standard error holds only the warning (architecture section 8). A file error, a settings error, and a wrong command line share exit code 2, and only the text on standard error tells them apart (architecture section 6).

6. **New side effect.** Every run that prints a count now writes its option to the settings file, after the count and its line break are on standard output: `null` for `wordcount FILE`, `"lines"`, `"chars"`, or `"longest"` for those options, and for `--again` the option it used, which is the one already saved (requirements F08 and Q19). A usage error, a file error, or a settings error writes nothing, so the settings stay as they were. This replaces F04 design 2.1's promise that the command "writes no file". It still opens `FILE` for reading only, and sends nothing anywhere (requirements section 7). The command reads the environment variables `APPDATA` on Windows, and `XDG_DATA_HOME` and the home folder elsewhere, to find the file. The option exists only after the project is installed again once F08 lands, for example with `uv pip install -e . --no-deps`.

Example, on Windows, where the user's folder is `C:\Users\me` and no `wordcount` settings folder exists yet. `notes.txt` and `greeting.txt` are the files of F08's prototype: `notes.txt` holds `Hello world` and `  troy-mode  trial`, and `greeting.txt` holds `你好 世界!`.

```text
PS> wordcount --again notes.txt
wordcount: no saved options to run again: C:\Users\me\AppData\Roaming\wordcount\settings.json
PS> $LASTEXITCODE
2
PS> wordcount --lines notes.txt
2
PS> wordcount --again greeting.txt
1
PS> wordcount notes.txt
4
PS> wordcount --again greeting.txt
2
PS> wordcount --longest notes.txt
9
PS> wordcount --longest missing.txt
wordcount: missing.txt: no such file
PS> wordcount --again greeting.txt
3
PS> wordcount --lines --again notes.txt
usage: wordcount [--lines | --chars | --longest | --again] FILE
wordcount: error: argument --again: not allowed with argument --lines
PS> $LASTEXITCODE
2
PS> Set-Content $env:APPDATA\wordcount\settings.json 'not json'
PS> wordcount --again notes.txt
wordcount: cannot read the settings file: C:\Users\me\AppData\Roaming\wordcount\settings.json
PS> $LASTEXITCODE
2
```

When the settings folder is read-only, the count still prints:

```text
PS> wordcount notes.txt
4
wordcount: warning: cannot write the settings file: C:\Users\me\AppData\Roaming\wordcount\settings.json
PS> $LASTEXITCODE
0
```

### 3.2 `main`

1. **Signature.** It does not change: `def main(argv: Sequence[str] | None = None) -> int:`. `argv` may now hold `--again`, with the rules of section 3.1.
2. **Purpose.** It now also reads the saved option through `load_option` for `--again`, and saves the run's option through `save_option` after a count. It imports `settings_path`, `settings_name`, `load_option`, and `save_option` from `troy_mode_trial.settings`, and the counting functions from the package `troy_mode_trial` as before (architecture section 4).
3. **Return value.** `0` after it wrote the count and one line break to standard output, also when it then wrote the settings warning. `2` after it wrote a file error line or one of the two settings error lines of section 3.1 to standard error. It flushes standard output before it saves the option, so the count is out before the settings file is written.
4. **Errors.** `SystemExit` with code 2 for a wrong command line, now also for `--again` with a counting option, before any settings call. Around its calls to settings only, `main` catches `OSError` and `ValueError`, as architecture section 6 asks: `FileNotFoundError` from `load_option` gives the first line of the table in section 3.1, any other caught exception from `settings_path` or `load_option` gives the second, and any caught exception from `settings_path` or `save_option` gives the warning. `main` passes `save_option` only `None`, a name taken from the parsed counting option, or the name that `load_option` returned, so the warning never hides the `ValueError` that section 2.6 calls a bug in cli. Around counting, it still catches only `OSError` and `UnicodeDecodeError`. Every other exception is a bug and reaches the caller, so Python exits with code 1.
5. **Side effects.** It writes the settings file as section 3.1 item 6 says. It still keeps no state in the process, so a test may call it several times, but each call that prints a count now changes the settings file that the next call with `--again` reads. Every test that calls `main` therefore needs the settings folder of section 3.3.

Example, with `APPDATA` or `XDG_DATA_HOME` set to an empty folder, and `notes.txt` the file of section 3.1:

```python
>>> from troy_mode_trial.cli import main
>>> main(["--again", "notes.txt"])  # writes to standard error
wordcount: no saved options to run again: ...settings.json
2
>>> main(["--lines", "notes.txt"])
2
0
>>> main(["--again", "notes.txt"])
2
0
>>> main(["--again", "--chars", "notes.txt"])
usage: wordcount [--lines | --chars | --longest | --again] FILE
wordcount: error: argument --chars: not allowed with argument --again
Traceback (most recent call last):
  ...
SystemExit: 2
```

### 3.3 Tests that change with F08

These existing tests change in F08's test plan. The Test Manager owns them. F04 to F07 are accepted, so their cases must pass in every F08 PR, before and after F08's code is in (R10).

1. **Usage line of F05.** `USAGE_ALL` in `tests/test_cli_lines.py` is `usage: wordcount [--lines | --chars | --longest] FILE`, and the cases that use it compare the first line word for word. Their expected first line becomes the line of proposal 1 once `--again` works, and stays the old line before. Their second lines do not change.
2. **Usage line of F07.** `USAGE` in `tests/test_cli_longest.py` is the same line and changes the same way.
3. **Usage lines that do not change.** F06's pattern in `tests/test_cli_chars.py` accepts any bracket that holds `--chars` before ` FILE`, which the new line still is. `tests/test_cli.py` and `version-tests/test_v0_2_scenarios.py` check only that the line starts with `usage: wordcount ` or `usage:`.
4. **Settings folder for every test.** An automatic fixture in `tests/conftest.py`, and one in `version-tests/conftest.py`, sets `APPDATA` and `XDG_DATA_HOME` for every test to a new empty folder outside the test's working folder (architecture section 10, ADR-0003). Without it, every successful call of `main` writes Troy's real settings file, and the version tests in `version-tests/test_v0_2_scenarios.py`, which run the installed `wordcount` in a subprocess, do the same. The folder must be outside the folder that the tests of F04 to F07 scan when they check that a run writes no file there, such as the checks in `tests/test_cli.py`, `tests/test_cli_lines.py`, and `tests/test_cli_longest.py`, so those cases keep passing unchanged.

## 4. Architect review

| Item | Result | Note |
| --- | --- | --- |
| Fits the module layout and the data model | Pass | The module layout fits. The new interfaces live in settings, which owns `src/troy_mode_trial/settings.py` (architecture section 3, ADR-0003). cli imports settings directly, `__init__.py` neither imports nor exports it, and settings imports no module (section 4). The path rules, the key `"option"` with `null` and the three names, the write after the count, and the temporary file with `os.replace` match section 5. In round 2, section 2.1's Errors table is the one rule for a file that cannot be read, as section 5's "exactly one key" asks: a repeated `"option"` key cannot be read, also with equal values, and `load_option` checks every key in the text. The sentence above the table accepts only white space between tokens and one byte order mark. A second byte order mark is not JSON white space, so the row for text that is not valid JSON covers it. |
| Follows the error handling and naming conventions | Pass | settings defines no exception of its own. It lets `OSError` through and raises `ValueError`, and it turns `RuntimeError` from `Path.home()` into `ValueError`, so cli catches only the two types that section 6 names. `main` catches them only around its calls to settings, and still catches only `OSError` and `UnicodeDecodeError` around counting. The exit codes match section 6: 2 for the two settings errors, read before `FILE` opens, and 0 with one warning line after a failed write. Standard output holds only the count, and the warning goes to standard error (section 8). Only settings writes a file. The names follow Python's naming. In round 1 I ran argparse 3.14 with the proposed group. It gives the usage line of proposal 1 and the two `not allowed with` lines exactly as section 3.1 shows. `--again --again` parses, and `--again=1` and `--ag` exit with code 2. |
| Does not duplicate an existing interface | Pass | No settings interface exists yet. `settings_name` wraps `settings_path` for the one case that `settings_path` cannot cover, an error line when the path cannot be worked out, and does not work out the path a second way. `main` still counts through the existing counting functions. |
| Depends only on features earlier in the order | Pass | F08's only hard dependency is F04, which comes before F08 in the order (F01, F03, F04, F07, F06, F02, F05, F08, F09) and is accepted. The design names F09 only as a later change to `OPTION_NAMES`, and does not use it. |
| Adds no hidden coupling between modules | Pass | cli relies only on what settings documents. It tells "no saved option" from "cannot read" by `FileNotFoundError`, which `load_option` documents as its signal. The list of saved names stays inside settings in `OPTION_NAMES`. The test fixture of section 3.3 sets environment variables that `settings_path` documents, and the design says it must stay outside the folders that the accepted tests scan. |
| Changes an implemented interface only through the change flow | Pass | The changes to `wordcount` and `main` come after requirements 8.0 (Q17 to Q22) and architecture 4.0 with ADR-0003, which Troy approved and which are merged (`1c21dd6`, `ac1a71c`). ADR-0003's Consequences already list the end of F04's "writes no file" and the new usage line. `main`'s signature does not change. Section 3.3 sends the changed tests of F05 and F07 and the new fixtures to F08's test plan, which the Test Manager owns. |
| The summary for Troy says what the design says, and lists every point Troy decides | Pass | In round 2 the summary matches the design: `--again` and what it repeats, the file, its folder on Windows and Linux with `$XDG_DATA_HOME` now named (note b of round 1), and what it never holds, hand edits that may add spaces while anything else invalid makes the file unreadable (section 2.1), the error with no count and exit code 2, no counting option with `--again`, and no change without `--again`. Its two decision points are the design's two proposals, each with a recommendation. Its risks are the design's: the warning and the older option after a failed write, and the shared exit code 2. The design has no other open choice. The English summary is about 1,300 characters, within 2,000, and holds no internal ID. It no longer says that `--again` works only after the project is installed again (section 3.1 item 6). That is not a decision, so it does not block. See note d. |

| Round | Issue | Resolution |
| --- | --- | --- |
| 1 | Finding 1, which blocks, on item 1, in section 2.1, the paragraph after the bytes table and the Errors table. The sentence that accepts "any content that Python's `json` module reads as such an object" contradicts the Errors table and architecture section 5 for a repeated key, such as `{"option": "lines", "option": "chars"}`. State the rule in one place. I recommend that such a file cannot be read, because architecture section 5 says that the object has exactly one key, and the Errors table already lists "a second key". Add the example to the Errors table, and change the sentence to say that `load_option` accepts white space between tokens and one byte order mark, and rejects every other form that the table lists. Make the same change in the mirror. Notes, which do not block. a. For the Developer: `save_option` raises `ValueError` for an unknown name, which section 2.6 calls a bug in cli, but section 3.2 item 4 turns it into the warning. Architecture section 6 allows that, but keep the name that cli passes to `save_option` coming only from the parsed options, so that the warning never hides a bug. Keep `main` within 50 lines (R04) with helpers for reading and saving. b. For the Interface Designer, if the summary changes for finding 1: the Linux folder could say "or `$XDG_DATA_HOME/wordcount` when it is set". c. For the Test Manager: the cases of F05 and F07 that compare the usage line must pass in every F08 PR (R10). Plan how they change at the same time as `--again` lands without making them accept either line, and give the test of `load_option` with a repeated key the result that the revised section 2.1 states. | Changes requested in round 1. |
| 2 | Round 1's finding 1 and note a, checked against design 0.2. No new finding blocks. Note, which does not block. d. For the Interface Designer: the summary for Troy could say again, in one line, that `--again` works only after the project is installed again, as section 3.1 item 6 says. Note c of round 1 for the Test Manager stands: the test of `load_option` with a repeated key expects a file that cannot be read, also with equal values. | Finding 1 is resolved: section 2.1's Errors table is the one rule, with both repeated-key examples, and the sentence above it accepts only white space between tokens and one byte order mark. Note a is resolved in section 3.2 item 4. Approved in round 2. |

## 5. Change log

| Version | Date | Change |
| --- | --- | --- |
| 0.1 | 2026-11-26 | First draft. |
| 0.2 | 2026-11-26 | Architect review round 1, finding 1: section 2.1 states in one place that a file that holds the key `"option"` more than once cannot be read, adds that example to the Errors table, and says that `load_option` accepts only white space between tokens and one byte order mark beyond the exact bytes. Section 3.2 says which names `main` passes to `save_option` (note a). |
| 1.0 | 2026-11-26 | Approved by Troy. |
