---
troy-doc: "F09-design"
lang: "en"
version: "0.1"
updated: "2026-11-26"
status: "Draft. In Architect review."
mirror: "design.zh-CN.md"
---

# F09 Count sentences option: interface design

## 1. Feature

- ID and name: F09 Count sentences option
- Requirement: [docs/requirements.md](../../requirements.md#4-features)
- Hard dependencies: F04
- Soft dependencies: None

## 2. Interfaces

F09 adds one interface, the library function `count_sentences` in the module counting (section 2.1), which counts the sentences of a file and which `main` calls for `--sentences`. Section 3 lists the changes to existing interfaces: `wordcount` and `main` in the module cli, which gain the option `--sentences`, the interfaces of F08's module settings, which gain the saved value `sentences`, and the exports of the package.

The sentence rule is in counting, not in cli, for the reasons F06 design section 2 gives for `count_chars` and F07 design section 2 gives for `count_longest`. counting already holds the rules that `--sentences` must share with `wordcount FILE`: one byte order mark at the start is skipped (requirements Q5), a missing file or a file that is not valid UTF-8 raises Python's own exception (Q4), and a word holds at least one letter or digit (F03), which a sentence must hold too (Q24). Requirements Q6 settled that counting lines fits counting with no architecture change. Counting sentences fits it the same way, and the design adds no file under `src/troy_mode_trial/`.

F09 comes after F08 in the order, and F08's design is approved and merged (F08 design 1.0). F09 builds on it: `--sentences` joins the set of options that exclude each other, beside `--lines`, `--chars`, `--longest`, and `--again`, and `--again` after `--sentences` counts sentences (requirements section 5, Troy's choice on 2026-11-26). F08's code is not on `main` yet, so section 3 records these as changes to F08's designed interfaces, which F09's code makes after F08's code is in.

One point in this design is a proposal that Troy accepts or changes, and it says so where it stands: the new usage line (section 3.1, proposal 1).

### 2.1 `count_sentences`

- Module: counting. Callers import it from the package `troy_mode_trial`, which `src/troy_mode_trial/__init__.py` defines, next to `count_chars`, `count_lines`, `count_longest`, and `count_words` (section 3.4).
- Purpose: Reads one UTF-8 text file and returns the number of its sentences, where a sentence is a run of text that ends in `.`, `!`, or `?` and holds at least one letter or digit (requirements F09).

Signature:

```python
def count_sentences(path: str | os.PathLike[str]) -> int:
```

The name starts with `count_`, like the other four functions behind the command.

Parameters:

| Name | Type | Meaning | Constraints |
| --- | --- | --- | --- |
| `path` | `str \| os.PathLike[str]` | The path of the file to read, absolute or relative to the current working directory. A `pathlib.Path` is an `os.PathLike[str]` and is accepted. | Names one existing, readable, regular file whose content is valid UTF-8. `bytes` paths are not accepted. |

- Return value: `int`, 0 or more. The function decodes the whole file as UTF-8 and removes one byte order mark (U+FEFF) at the start of the file (requirements Q5). Inside counting, it uses the same file reading and the same letter-or-digit test as `count_words`, not a second copy of them.

  The rules for sentences:

  - A mark is one of the three characters `.` (U+002E), `!` (U+0021), and `?` (U+003F). No other character is a mark: not the Chinese marks `。`, `！`, and `？`, not the full-width `．`, and not the ellipsis character `…` (requirements Q26).
  - A run of marks is one or more marks with nothing between them, such as `.`, `...`, `!!`, or `?!`. Each run of marks ends one piece of text: the text from the end of the previous run, or from the start of the file, up to and including this run (requirements Q23).
  - A piece is a sentence when it holds at least one character for which `str.isalnum()` is true, the test that F03 uses for a word (requirements Q24). A piece of marks, white space, and other characters only, such as the second piece of `Hi. .`, is no sentence.
  - The text after the last run of marks is no sentence, whatever it holds (requirements Q25).
  - A mark ends a piece wherever it stands, also inside a number, an abbreviation, or a web address, so `3.14.` is two pieces (requirements F09, section 8).
  - Line ends and other white space do not end a sentence. A sentence may run over several lines, and a line with no mark is part of the next sentence, or of the text after the last mark. So a file saved on Windows and the same file saved on Linux give the same number.
  - Only one byte order mark at the very start is removed. A U+FEFF anywhere else is an ordinary character, and it is neither a letter nor a digit.

  The result is never more than the number of runs of marks. When `count_words(path)` is 0, `count_sentences(path)` is 0 too, because a letter or digit is never white space and is therefore always part of a word.

  | File bytes, as text | Result | Why |
  | --- | --- | --- |
  | (empty) | `0` | No mark. |
  | `EF BB BF` (the byte order mark only) | `0` | No mark. |
  | `-- ...\n` | `0` | The one piece holds no letter or digit. |
  | `It rains. Does it stop? Yes!!\nWait...\n` | `4` | `!!` and `...` each end one sentence. |
  | `Done. Not yet\r\n` | `1` | `Not yet` ends in no mark. |
  | `Pi is 3.14.\n` | `2` | `Pi is 3.` and `14.`. |
  | `Wait?!` | `1` | One run of marks. |
  | `Hi . . . there.` | `2` | The two pieces ` .` hold no letter or digit. |
  | `1. 2. 3.` | `3` | A digit is enough. |
  | `_.` | `0` | `_` is neither a letter nor a digit. |
  | `Line one\nline two.` | `1` | A line end does not end a sentence. |
  | `"Stop!" he said.` | `2` | The closing `"` starts the second piece. |
  | `你好。世界。` | `0` | `。` is not a mark. |
  | `你好。He left.` | `1` | One piece, ended by `.`. |
  | `EF BB BF` then `Hi.` | `1` | The byte order mark is removed. |

Errors:

The function defines no exception of its own (requirements Q4). It lets Python's own exception reach the caller, with the same table as `count_words`, `count_lines`, `count_chars`, and `count_longest`.

| Error | When |
| --- | --- |
| `FileNotFoundError` | No file exists at `path`, or `path` is the empty string. |
| `IsADirectoryError` or `PermissionError` | `path` names a folder. Linux raises `IsADirectoryError`. Windows raises `PermissionError`. |
| `PermissionError` | The process may not read the file. |
| `UnicodeDecodeError` | Any byte of the file is not valid UTF-8, wherever it is. |
| `TypeError` | `path` is neither a `str` nor an `os.PathLike[str]`, for example `bytes` or an `int`. |

- Side effects: The function opens the file for reading and closes it before it returns or raises. It writes, sends, and stores nothing. It does not touch the settings file.
- Performance target: None

Example:

`story.txt`, `draft.txt`, `pi.txt`, and `dashes.txt` are the files of F09's prototype: `story.txt` holds the lines `It rains. Does it stop? Yes!!` and `Wait...`, `draft.txt` holds `Done. Not yet`, `pi.txt` holds `Pi is 3.14.`, and `dashes.txt` holds `-- ...`.

```python
>>> from pathlib import Path
>>> from troy_mode_trial import count_sentences
>>> count_sentences("story.txt")
4
>>> count_sentences(Path("draft.txt"))
1
>>> count_sentences("pi.txt")
2
>>> count_sentences("dashes.txt")
0
>>> count_sentences("missing.txt")
Traceback (most recent call last):
  ...
FileNotFoundError: [Errno 2] No such file or directory: 'missing.txt'
```

## 3. Changes to existing interfaces

Requirements 8.0 added F09 as a new feature, with the option `--sentences` and Troy's decisions Q23 to Q26, in the merged [docs] PR "[docs] Change the requirements: remember the last options and count sentences" (commit `1c21dd6`). Requirements section 5 records Troy's choice that F09 comes after F08 and that `--again` remembers `--sentences`. Architecture 4.0 and ADR-0003, merged in the [docs] PR "[docs] Change the architecture for F08" (commit `ac1a71c`), say in section 5 and in ADR-0003's Consequences that F09's design adds `sentences` to the saved values. F04 to F07 are accepted. F08's design 1.0 is approved and merged, and its code lands before F09's. F09 changes these interfaces as sections 3.1 to 3.4 say, and section 3.5 lists the tests that change with them.

What does not change: the counting functions `count_words`, `count_lines`, `count_chars`, and `count_longest` keep their signatures, behavior, and errors. `wordcount FILE`, `--lines`, `--chars`, `--longest`, and `--again` with a saved option other than `sentences` print the same numbers, the same file error lines, the same settings error and warning lines, and the same exit codes as before. The settings file's place, its key, the exact bytes for the other values, and F08's rules for a file that cannot be read stay. `settings_path`, `settings_name`, and the signatures of `load_option` and `save_option` stay. `src/troy_mode_trial/__init__.py` still imports neither cli nor settings. The console script in `pyproject.toml` stays. Short forms of the option are out of scope.

### 3.1 `wordcount`

This changes F04 design 2.1, as F07 design 2.1 and F08 design 3.1 left it.

1. **New option `--sentences`.** `wordcount --sentences FILE` prints the number of sentences of `FILE` instead of its words: exactly what `count_sentences(FILE)` returns (section 2.1), as one decimal number and one line break on standard output, with exit code 0, as for the other options.

   | Name | Type | Meaning | Constraints |
   | --- | --- | --- | --- |
   | `--sentences` | Option, a flag with no value | Print the number of sentences of `FILE` instead of its number of words. | Optional. Only the full name `--sentences`. There is no short form, and a shortened name, such as `--sent` or `--s`, is a wrong command line, as for the other options. It may come before or after `FILE`. Given twice, it works as given once. `--sentences=VALUE` is a wrong command line. It cannot come with `--lines`, `--chars`, `--longest`, or `--again`, in any order (requirements F09, Q13, and Q21). After `--`, the text `--sentences` is a file name, not the option. |

   The command still has no `-h` or `--help`, and no option other than `--lines`, `--chars`, `--longest`, `--sentences`, and `--again` (requirements section 8).

2. **Proposal 1, the usage line, for Troy to accept or change.** The usage line changes from F08's `usage: wordcount [--lines | --chars | --longest | --again] FILE` to:

   ```text
   usage: wordcount [--lines | --chars | --longest | --sentences | --again] FILE
   ```

   `--sentences` joins the set of options that exclude each other, because a command takes at most one of them. This is the form Troy approved for F05, F07, and F08, and it is the line argparse writes for that set, so it needs no extra code. `--sentences` stands after the other counting options and before `--again`, as in the requirements, so the counting options stay together and `--again`, which repeats one of them, stays last. The other choice adds `--sentences` at the end, `usage: wordcount [--lines | --chars | --longest | --again | --sentences] FILE`, which puts `--again` between two counting options.

   The line is 77 characters long. argparse takes the width from the environment variable `COLUMNS` when it is set, otherwise from the terminal of standard output, and otherwise uses 80 columns. It writes the line on one line when that width is at least 79 columns. In a narrower window it breaks the line over two lines, as it already does for F08's 63-character line in a window narrower than 65 columns. The usage error's exit code and second line do not change with the width.

3. **New usage errors.** `--sentences` together with `--lines`, `--chars`, `--longest`, or `--again` is a wrong command line with exit code 2 (requirements F09, Q13, and Q21). argparse writes the usage line of proposal 1 and then one line in argparse's own words that names the later option first, as for two counting options (F05 design 2.1, approved). For example, `wordcount --lines --sentences notes.txt` gives `wordcount: error: argument --sentences: not allowed with argument --lines`, `wordcount --sentences notes.txt --again` gives `wordcount: error: argument --again: not allowed with argument --sentences`, and `wordcount --again --sentences notes.txt` gives `wordcount: error: argument --sentences: not allowed with argument --again`. This error comes before the check for a missing `FILE`. Every other usage error keeps its message, and its first line becomes the line of proposal 1. A usage error reads and writes no settings file, as in F08.

4. **File errors.** A file error with `--sentences` gives exactly the message and exit code that `wordcount FILE` gives for the same file (requirements F09): one line `wordcount: <FILE>: <reason>` on standard error, exit code 2, and empty standard output, with `<FILE>` and the five reason texts of F04 design 2.1 unchanged. The command decodes the whole file, so a file whose invalid bytes come after valid text is still `not valid UTF-8`, and no number is printed.

5. **Settings.** A run with `--sentences` that prints a count saves `"sentences"` in the settings file, after the count and its line break are on standard output, as F08 design 3.1 item 6 says for the other options. After it, `wordcount --again FILE` counts the sentences of `FILE`, and saves `"sentences"` again. A run with `--sentences` that fails, with a usage error or a file error, writes nothing, so the settings stay as they were (requirements Q19). When the settings file cannot be written, the count still prints with F08's warning and exit code 0 (requirements Q22). The settings error and warning texts of F08 design 3.1 proposal 2 do not change.

6. **Installing.** The option exists in the installed `wordcount` once F09's code is installed, for example with `uv pip install -e . --no-deps`, as for the earlier options.

Example, on Windows, where the user's folder is `C:\Users\me`, with the files of section 2.1 and `notes.txt`, which holds `Hello world` and `  troy-mode  trial`:

```text
PS> wordcount --sentences story.txt
4
PS> wordcount story.txt
7
PS> wordcount --sentences draft.txt
1
PS> wordcount --sentences pi.txt
2
PS> wordcount --sentences dashes.txt
0
PS> wordcount --again story.txt
4
PS> Get-Content $env:APPDATA\wordcount\settings.json
{"option": "sentences"}
PS> wordcount --again draft.txt
1
PS> wordcount --sentences missing.txt
wordcount: missing.txt: no such file
PS> $LASTEXITCODE
2
PS> wordcount --lines --sentences notes.txt
usage: wordcount [--lines | --chars | --longest | --sentences | --again] FILE
wordcount: error: argument --sentences: not allowed with argument --lines
PS> $LASTEXITCODE
2
PS> wordcount --sent notes.txt
usage: wordcount [--lines | --chars | --longest | --sentences | --again] FILE
wordcount: error: unrecognized arguments: --sent
PS> $LASTEXITCODE
2
```

`wordcount --again story.txt` prints `4`, the sentences of `story.txt`, because the run before it, `wordcount --sentences dashes.txt`, printed a count and saved `sentences`.

### 3.2 `main`

This changes F04 design 2.2, as F07 design 2.2 and F08 design 3.2 left it.

1. **Signature.** It does not change: `def main(argv: Sequence[str] | None = None) -> int:`. `argv` may now hold `--sentences`, with the rules of section 3.1.
2. **Purpose.** It now also gets the number through `count_sentences` for `--sentences`, and for `--again` when the saved option is `"sentences"`. It imports `count_sentences` from the package `troy_mode_trial`, next to the other four counting functions, never from `troy_mode_trial.counting` (architecture section 4). It imports from `troy_mode_trial.settings` the same four names as in F08.
3. **Return value.** As in F08 design 3.2: `0` after it wrote the count and one line break to standard output, also when it then wrote the settings warning, and `2` after it wrote a file error line or one of the two settings error lines to standard error.
4. **Errors.** `SystemExit` with code 2 for a wrong command line, now also for `--sentences` with another option of the set, before any settings call or any counting. Around counting, it still catches only `OSError` and `UnicodeDecodeError`, now also from `count_sentences`. Around settings, it still catches only `OSError` and `ValueError`. It passes `save_option` `"sentences"` only when the parsed arguments hold `--sentences`, or when `load_option` returned `"sentences"`, so the warning never hides the `ValueError` that F08 design 2.6 calls a bug in cli. Every other exception is a bug and reaches the caller, so Python exits with code 1.
5. **Side effects.** As in F08 design 3.2, with `"sentences"` as one more value that it saves.

Example, with `APPDATA` or `XDG_DATA_HOME` set to an empty folder, and `story.txt` the file of section 2.1:

```python
>>> from troy_mode_trial.cli import main
>>> main(["--sentences", "story.txt"])
4
0
>>> main(["--again", "story.txt"])
4
0
>>> main(["--sentences", "--chars", "story.txt"])
usage: wordcount [--lines | --chars | --longest | --sentences | --again] FILE
wordcount: error: argument --chars: not allowed with argument --sentences
Traceback (most recent call last):
  ...
SystemExit: 2
```

### 3.3 F08's settings interfaces

This changes F08 design sections 2.1, 2.2, 2.5, and 2.6, as F08 design section 2 foresaw: F09 adds one name to `OPTION_NAMES`, and `load_option` and `save_option` accept it with no other change to settings.

1. **`OPTION_NAMES`** (F08 design 2.2) gains `"sentences"` at its end, in the order of the usage line's counting options:

   ```python
   OPTION_NAMES: Final[tuple[str, ...]] = ("lines", "chars", "longest", "sentences")
   ```

2. **The settings file** (F08 design 2.1). The value of `"option"` may now be `"sentences"`, for a run with `--sentences`. `save_option` writes it as these exact bytes, with no byte order mark and with a `\n` line end on every system:

   | Last run | Bytes of the file |
   | --- | --- |
   | `wordcount --sentences FILE` | `{"option": "sentences"}` then `\n` |

   The key, the bytes for the other values, and every other row of F08's Errors table stay. Only the example `"sentences"` before F09 in the last row no longer applies. `"Sentences"`, `"sentence"`, and `"--sentences"` still cannot be read, because names are lowercase and match exactly.

3. **`load_option`** (F08 design 2.5) keeps its signature and errors. It now returns `'sentences'` for a file that holds `"sentences"`, where F08's code raises `ValueError`.

4. **`save_option`** (F08 design 2.6) keeps its signature, its order of steps, and its errors. It now accepts `"sentences"` as `option`, where F08's code raises `ValueError` before it touches any folder or file.

5. **Compatibility** (architecture section 5). F09's program reads every file that F08's program writes, because F09 only adds a name. F08's program, or any older `wordcount` with `--again`, reads a file that holds `"sentences"` as a file that cannot be read, as F08 design 2.1 and ADR-0003's Consequences say. Its `wordcount --again` then gives F08's settings error `wordcount: cannot read the settings file: <settings file>` with exit code 2, and its next run that prints a count writes the file again in F08's format. A program without F08 does not read the file at all.

Example, with the settings file in a temporary folder:

```python
>>> from troy_mode_trial.settings import OPTION_NAMES, load_option, save_option, settings_path
>>> OPTION_NAMES
('lines', 'chars', 'longest', 'sentences')
>>> save_option(settings_path(), "sentences")
>>> settings_path().read_bytes()
b'{"option": "sentences"}\n'
>>> load_option(settings_path())
'sentences'
```

### 3.4 Package exports

`src/troy_mode_trial/__init__.py` exports `count_sentences` next to `count_chars`, `count_lines`, `count_longest`, and `count_words`, and adds it to `__all__`. This adds a name and changes no existing one. `__init__.py` still imports neither cli nor settings, and exports nothing from them (architecture section 4).

### 3.5 Tests that change with F09

These existing tests change in F09's test plan. The Test Manager owns them. F04 to F07 are accepted, and F08 may be accepted by then, so the cases of accepted features must pass in every F09 PR, before and after F09's code is in (R10). Their expected usage line becomes the line of proposal 1 once `--sentences` works, and stays F08's line before, as F08's test plan does for F08's change.

1. **Usage line of F05.** `USAGE_ALL` in `tests/test_cli_lines.py`, as F08's test plan leaves it, and the cases that compare the first line word for word. Their second lines do not change.
2. **Usage line of F07.** `USAGE` in `tests/test_cli_longest.py`, as F08's test plan leaves it, changes the same way.
3. **Usage line of F08.** The cases of F08's test plan that compare the usage line word for word change the same way. Their second lines, such as `argument --again: not allowed with argument --lines`, do not change.
4. **F08's cases about `sentences`.** Any case of F08's test plan that expects `"sentences"` to be unknown changes: a settings file that holds `"sentences"` now reads as `'sentences'`, `save_option(path, "sentences")` now writes the bytes of section 3.3, and `OPTION_NAMES` is the tuple of section 3.3. Cases with other unknown names, such as `"Lines"` or `"--lines"`, do not change.
5. **Usage lines that do not change.** F06's pattern in `tests/test_cli_chars.py` accepts any bracket that holds `--chars` before ` FILE`, which the new line still is when it is on one line. `tests/test_cli.py` and the version tests check only that the line starts with `usage: wordcount ` or `usage:`.
6. **Settings folder.** F09 adds no fixture. Its tests that call `main` or run the installed `wordcount` use F08's automatic fixtures in `tests/conftest.py` and `version-tests/conftest.py`, which set `APPDATA` and `XDG_DATA_HOME` to a new empty folder for every test (architecture section 10, ADR-0003), so no F09 test reads or writes the real settings file.
7. **Width of the usage line.** A case that compares the usage line word for word expects the one-line form of proposal 1, which argparse writes when the width of section 3.1 item 2 is at least 79 columns: `COLUMNS` unset or at least 79, and standard output not a narrower terminal.

## 4. Architect review

| Item | Result | Note |
| --- | --- | --- |
| Fits the module layout and the data model | Pass | `count_sentences` lives in counting and is exported through `src/troy_mode_trial/__init__.py`, which still imports neither cli nor settings (architecture sections 3 and 4). The design adds no file under `src/troy_mode_trial/`. The new saved value `sentences` is the one that architecture section 5 and ADR-0003 already foresee, and the settings file's place, key, and other bytes stay. Section 3.3 item 5 says how an older version treats a file that F09 writes, as architecture section 5 asks. |
| Follows the error handling and naming conventions | Pass | `count_sentences` defines no exception and lets Python's own exceptions through, with the same table as the other four counting functions (architecture section 6). cli still catches only `OSError` and `UnicodeDecodeError` around counting and only `OSError` and `ValueError` around settings, and passes `save_option` only known names. The name follows the `count_` prefix. Standard output still holds only the count. |
| Does not duplicate an existing interface | Pass | No existing interface counts sentences. Section 2.1 requires the same file reading and the same letter-or-digit test as `count_words` inside counting, not a second copy. The saved names stay in the one tuple `OPTION_NAMES`. |
| Depends only on features earlier in the order | Pass | The hard dependency F04 is accepted. F09 also builds on F08's designed interfaces, and F08 comes before F09 in the order (F01, F03, F04, F07, F06, F02, F05, F08, F09), with its design merged, as requirements section 5 records Troy's choice. Section 2 says F09's code lands after F08's code. |
| Adds no hidden coupling between modules | Pass | cli maps the option to its counting function and to its saved name. settings learns only one more name in `OPTION_NAMES` and nothing about counting. counting does not touch the settings file (section 2.1, Side effects). |
| Changes an implemented interface only through the change flow | Pass | The changes to the accepted `wordcount` and `main`, the usage line, and the accepted tests come from requirements 8.0, which Troy approved through the change flow. Section 3 lists what changes and what stays, and section 3.5 hands the changed tests of accepted features to F09's test plan, so they pass before and after F09's code, as for F08. F08's settings interfaces are designed but not implemented yet. |
| The summary for Troy says what the design says, and lists every point Troy decides | Pass | The summary gives the sentence rule with the design's own examples, `--again` with `--sentences`, the file errors, and the usage errors. It lists the one proposal, the usage line, with its two options and a recommendation, and both risks: an older `wordcount` cannot read a settings file that holds `sentences`, and the 77-character line breaks below 79 columns. Checked by running argparse on Python 3.14.3 with the design's parser: the line is 77 characters and stays on one line at `COLUMNS=79` and breaks before `FILE` at 78; the three "not allowed with" messages are word for word as in section 3.1 item 3; `--sent` gives `unrecognized arguments: --sent` and exit code 2. Every row of the table in section 2.1 also gives the stated result by the stated rules. |

| Round | Issue | Resolution |
| --- | --- | --- |
| 1 | None. All seven items pass. Risky: the settings file that Troy keeps may now hold `sentences`, which an older `wordcount` cannot read. | Approved. |

## 5. Change log

| Version | Date | Change |
| --- | --- | --- |
| 0.1 | 2026-11-26 | First draft. |
