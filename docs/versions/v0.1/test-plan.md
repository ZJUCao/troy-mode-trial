---
troy-doc: "v0.1-test-plan"
lang: "en"
version: "0.2"
updated: "2026-11-08"
status: "Draft."
mirror: "test-plan.zh-CN.md"
---

# v0.1 version test plan

## 1. Version

- Version: v0.1
- Features: F01, F03
- Requirements: [docs/requirements.md](../../requirements.md#6-version-plan)

## 2. End-to-end scenarios

Each scenario follows the user flow in requirements section 3 and the prototypes of F01 and F03. Troy's scripts call `count_words` with a path relative to the current working directory, so the scenarios do too, except where a scenario says otherwise. Each test makes its own files in a temporary folder and writes them in binary mode, as the exact bytes the scenario gives, so that Windows never turns `\n` into `\r\n`. Characters outside ASCII are encoded as UTF-8 unless the scenario gives other bytes. The design promises only the type of an exception, not its message (Q4), so a scenario that expects an exception checks the type only.

| ID | Scenario | Run by | Steps | Expected result |
| --- | --- | --- | --- | --- |
| v0.1-S01 | Count the words of a file, as in the F01 prototype. | Claude | 1. Write `notes.txt` with `Hello world\n  troy-mode  trial`, with no line break at the end. 2. Make the folder of `notes.txt` the working directory. 3. Run `from troy_mode_trial import count_words`. 4. Call `count_words("notes.txt")`. | Returns `4`, and the type of the result is exactly `int`. |
| v0.1-S02 | Count the words of an empty file, as in the F01 prototype. | Claude | 1. Write an empty `empty.txt`. 2. Make its folder the working directory. 3. Call `count_words("empty.txt")`. | Returns `0`. |
| v0.1-S03 | Count a file that does not exist, as in the F01 prototype. | Claude | 1. Make an empty folder the working directory. 2. Call `count_words("missing.txt")`. | Raises `FileNotFoundError`. |
| v0.1-S04 | Count a file that is not valid UTF-8, as in the F01 prototype. | Claude | 1. Write `latin1.txt` with `café au lait` in Latin-1, so that its bytes start `63 61 66 E9 20`. 2. Make its folder the working directory. 3. Call `count_words("latin1.txt")`. | Raises `UnicodeDecodeError`. |
| v0.1-S05 | Count a file whose runs do not all hold a letter or digit, as in the F03 prototype. | Claude | 1. Write `dashes.txt` with `Wait -- what ... don't x--y 3.14 _`. 2. Make its folder the working directory. 3. Call `count_words("dashes.txt")`. | Returns `5`. The runs `--`, `...`, and `_` do not count. |
| v0.1-S06 | Count a file that holds only runs without a letter or digit, as in the F03 prototype. | Claude | 1. Write `only-symbols.txt` with `-- ... !!!` and nothing else. 2. Make its folder the working directory. 3. Call `count_words("only-symbols.txt")`. | Returns `0`. |
| v0.1-S07 | A script of Troy's counts files made on Windows and on Linux, in its own Python process on Troy's PC, and gets the same count for the same words whatever the line endings. | Claude | 1. Write three files. `windows.txt` holds the bytes `EF BB BF` followed by `Hello world\r\n  troy-mode  trial\r\n`, as Notepad saves it. `linux.txt` holds `Hello world\n  troy-mode  trial\n`. `mixed.txt` holds `Wait -- what ... don't x--y 3.14 _\r\n日本語　テキスト 😀\n`, where the gap between `日本語` and `テキスト` is U+3000. 2. Record the bytes of each file. 3. Start a new Python 3.13 process from a folder other than the files' folder. 4. In that process, import `troy_mode_trial`, call `troy_mode_trial.count_words` once on the absolute path of each file as a `pathlib.Path`, and print the three counts. Run all steps on Windows 11 on Troy's PC. | The process exits with code 0 and prints `4`, `4`, and `7`. Each file keeps the bytes recorded in step 2. |

## 3. Performance and stress cases

None. Requirements section 7.1 sets no performance target, so v0.1 has no performance or stress case (R14).

## 4. Devices

| Device | Operating system | Run by |
| --- | --- | --- |
| Troy's PC | Windows 11, with Python 3.13 in the conda environment `troy-mode-trial` | Claude |

Claude's scenarios run only in the release test on Troy's PC, never in CI, so the GitHub Actions runner is not a device for them. v0.1 is a library with no user interface, and every scenario runs through `count_words` from a script. So no scenario needs a device that only Troy has.

## 5. Acceptance record

None. Troy has not yet accepted v0.1.

## 6. Change log

| Version | Date | Change |
| --- | --- | --- |
| 0.1 | 2026-11-08 | First draft. |
| 0.2 | 2026-11-08 | v0.1-S07 runs on Windows 11 on Troy's PC only, and section 4 no longer lists the GitHub Actions runner, because version tests never run in CI. |
