---
troy-doc: "ADR-0003"
lang: "en"
version: "1.0"
updated: "2026-11-26"
status: "Approved by Troy on 2026-11-26"
mirror: "ADR-0003-settings-module.zh-CN.md"
---

# ADR-0003: The `wordcount` command keeps its last option through a new module, settings

## 1. Status

Accepted. Troy accepted it on 2026-11-26 by approving `docs/architecture.md`.

## 2. Context

Requirements 8.0 add F08. `wordcount --again FILE` counts FILE with the option of the last run that printed a count. Every such run writes its option, or that it had none, to one settings file: `%APPDATA%\wordcount\settings.json` on Windows, and `$XDG_DATA_HOME/wordcount/settings.json`, or `~/.local/share/wordcount/settings.json`, on Linux. The file holds only the option (Q18). A failed run leaves it as it was (Q19). `--again` with no saved option or an unreadable file is an error that names the file, exit code 2 (Q20). A file that cannot be written gives the count, a warning that names the file on standard error, and exit code 0 (Q22). Requirements section 7 now lets the command write this one file, and the library still reads files only. F09 comes after F08 and makes `--again` remember `--sentences` too.

Architecture 3.0 does not cover this:

- Its data model is empty, and the program keeps no file. The settings file is the first stored format, and it outlives every version of the program that writes it.
- Its section 6 lets cli catch only `OSError` and `UnicodeDecodeError` from counting, and treats every other exception as a bug. A settings file with broken content raises `ValueError` from `json`, and a failed write must not change the exit code.
- Its section 8 says that standard error holds errors and usage lines. A warning with exit code 0 is new.
- It has no test setup. Every successful call of `main` in the existing tests of F04 to F07 would write the real settings file in Troy's data folder. Several of those tests also check that their working folder does not change.
- Requirements 7 allow the standard library only.

## 3. Decision

1. **A new module, settings**, owns `src/troy_mode_trial/settings.py`. It finds the settings file, reads the saved option, and writes it. Its external interface is `src/troy_mode_trial/settings.py`. It may depend on no module. cli may depend on counting and settings. counting never imports settings, and `src/troy_mode_trial/__init__.py` does not import it or export from it, so R07 keeps the library from writing any file. F08's design names the functions.
2. **Where the file is.** On Windows (`sys.platform == "win32"`), `<APPDATA>\wordcount\settings.json`. Elsewhere, `<XDG_DATA_HOME>/wordcount/settings.json` when `XDG_DATA_HOME` is set to an absolute path, otherwise `~/.local/share/wordcount/settings.json`. The path is worked out from the environment at each run, never cached. An unset `APPDATA` on Windows is a settings error as in point 5, not a bug.
3. **Data model.** The file is UTF-8 JSON: one object with exactly one key, whose value is `null` for a run with no option, or the name of one counting option. F08's design fixes the key and the values (`lines`, `chars`, `longest`); F09's design adds `sentences`. Any other content, such as broken JSON, another key, or an unknown value, is a file that cannot be read (Q20). The file never holds a file name, a path, a count, or text from a file (Q18).
4. **When and how it is written.** cli writes the option only after the count and its line break are on standard output, so a failed run never writes (Q19). settings creates the `wordcount` folder when it is missing, writes the new content to a temporary file in the same folder, and then replaces the old file with `os.replace`. A failed or interrupted write leaves the old file whole, or no file, and never a half-written one. The standard library's `json`, `os`, `pathlib`, and `tempfile` are enough, so no dependency is added.
5. **Error handling.** settings defines no exception of its own. It lets `OSError` and its subclasses through and raises `ValueError` for content that is not a saved option (`json.JSONDecodeError` is a `ValueError`). cli catches `OSError` and `ValueError` only around its calls to settings, never around counting. On a read for `--again`, it writes one error line that names the settings file and returns exit code 2. A missing file means no saved option. On a write, it writes one warning line that names the settings file to standard error and returns exit code 0. F08's design fixes the texts.
6. **Output.** Standard output still holds only the count and one line break. Standard error may hold one warning on a run that exits with code 0.
7. **Test setup.** No test reads or writes Troy's real data folder. An automatic fixture in `tests/conftest.py`, and one in `version-tests/conftest.py`, sets `APPDATA` and `XDG_DATA_HOME` for every test to a new empty folder outside the test's working folder. The subprocess runs of the installed program inherit them. The Test Manager adds the fixtures in F08's test plan.

The architecture changes to match after Troy approves it. The module table adds settings. The dependency rules add `cli --> settings`. Sections 5 to 8 and 10 take points 3 to 7. The decision records add this ADR.

## 4. Options considered

| Option | Pros | Cons |
| --- | --- | --- |
| A new module settings, which only cli uses (chosen) | R07 keeps counting a read-only library. The stored format and its errors have one place, which F09 extends. cli stays the command line only. | The architecture changes, and the module table gains a row. |
| Put the settings code in `src/troy_mode_trial/cli.py` | No new module. | cli's file mixes the command line with file paths, JSON, and safe writes, and grows again with F09. Nothing checks where the file writing sits. |
| Put the settings code in counting | No new module. | The library would hold code that writes a file, against requirements 7. |
| The third-party package `platformdirs` for the folder | Handles more systems. | A new dependency, against requirements 7. Its Windows default is not `%APPDATA%\wordcount`. |
| Write the file in place, with no temporary file | Slightly less code. | A failed write can leave a half-written file, and the next `--again` then fails. |

## 5. Consequences

- The program keeps a file on Troy's computer for the first time. Its format is hard to change later: a new version must still read the file an older one wrote, or treat it as unreadable.
- Every run that prints a count writes one small file, so `wordcount` does a little more work per run.
- `main`'s promise in F04's design that the command writes no file changes. F08's design records this, and the new usage line, as changes to existing interfaces.
- The accepted tests of F05 and F07 that compare the exact usage line, and the tests of F04 to F07 that call `main`, depend on F08's test plan: the first need the new usage line, and all need the fixture of point 7.
- F09's design changes F08's interfaces: it adds `sentences` to the saved values.

## 6. Related

- Features: F08, F09, F04
- Rules: R07, R16
