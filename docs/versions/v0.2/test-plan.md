---
troy-doc: "v0.2-test-plan"
lang: "en"
version: "0.1"
updated: "2026-11-08"
status: "Draft."
mirror: "test-plan.zh-CN.md"
---

# v0.2 version test plan

## 1. Version

- Version: v0.2
- Features: F02
- Requirements: [docs/requirements.md](../../requirements.md#6-version-plan)

## 2. End-to-end scenarios

Each scenario follows the user flow in requirements section 3, the F02 prototype, and the decisions Q2 to Q5. The scenarios call the function by the prototype's name, `count_lines`. If F02's design fixes another name, or does not accept a `pathlib.Path`, the Test Manager updates this plan before the v0.2 tests PR.

Troy's scripts call `count_lines` with a path relative to the current working directory, so the scenarios do too, except where a scenario says otherwise. Each test makes its own files in a temporary folder and writes them in binary mode, as the exact bytes the scenario gives, so that Windows never turns `\n` into `\r\n`. Characters outside ASCII are encoded as UTF-8 unless the scenario gives other bytes. The requirements promise only the type of an exception, not its message (Q4), so a scenario that expects an exception checks the type only.

Q2 names only `\n`, `\r\n`, and `\r` as line breaks. So no scenario uses the other characters that Python's `str.splitlines()` treats as line breaks, such as U+2028 or form feed. F02's design and test plan settle those characters.

| ID | Scenario | Run by | Steps | Expected result |
| --- | --- | --- | --- | --- |
| v0.2-S01 | Count the lines of a file whose last line has no line break, as in the F02 prototype. | Claude | 1. Write `notes.txt` with `Hello world\n  troy-mode  trial`, with no line break at the end. 2. Make the folder of `notes.txt` the working directory. 3. Run `from troy_mode_trial import count_lines`. 4. Call `count_lines("notes.txt")`. | Returns `2`, and the type of the result is exactly `int`. |
| v0.2-S02 | Count the lines of a file with Windows line breaks, as in the F02 prototype. | Claude | 1. Write `windows.txt` with `Hello world\r\n  troy-mode  trial`, with no line break at the end. 2. Make its folder the working directory. 3. Call `count_lines("windows.txt")`. | Returns `2`. Each `\r\n` ends one line, not two. |
| v0.2-S03 | Count the lines of an empty file, as in the F02 prototype. | Claude | 1. Write an empty `empty.txt`. 2. Make its folder the working directory. 3. Call `count_lines("empty.txt")`. | Returns `0`. |
| v0.2-S04 | Count a file that does not exist, as in the F02 prototype. | Claude | 1. Make an empty folder the working directory. 2. Call `count_lines("missing.txt")`. | Raises `FileNotFoundError`. |
| v0.2-S05 | Count a file that is not valid UTF-8. | Claude | 1. Write `latin1.txt` with `café au lait\n` in Latin-1, so that its bytes start `63 61 66 E9 20`. 2. Make its folder the working directory. 3. Call `count_lines("latin1.txt")`. | Raises `UnicodeDecodeError`. |
| v0.2-S06 | Count a file that holds only one line break. | Claude | 1. Write `one-break.txt` with `\n` and nothing else. 2. Make its folder the working directory. 3. Call `count_lines("one-break.txt")`. | Returns `1`. |
| v0.2-S07 | Count a file with empty lines and a line break at the end. | Claude | 1. Write `blank-lines.txt` with `first\n\nthird\n`. 2. Make its folder the working directory. 3. Call `count_lines("blank-lines.txt")`. | Returns `3`. The empty second line counts, and the final `\n` does not start a fourth line. |
| v0.2-S08 | Count a file that mixes all three line breaks. | Claude | 1. Write `mixed-breaks.txt` with `one\rtwo\r\nthree\nfour`, with no line break at the end. 2. Make its folder the working directory. 3. Call `count_lines("mixed-breaks.txt")`. | Returns `4`. |
| v0.2-S09 | A script of Troy's counts the lines and the words of files made on Windows and on Linux, in its own Python process on Troy's PC, and gets the same counts for the same text whatever the line breaks. | Claude | 1. Write three files. `windows.txt` holds the bytes `EF BB BF` followed by `Hello world\r\n  troy-mode  trial\r\n`, as Notepad saves it. `linux.txt` holds `Hello world\n  troy-mode  trial\n`. `mixed.txt` holds `Wait -- what ... don't x--y 3.14 _\r\n日本語　テキスト 😀\n`, where the gap between `日本語` and `テキスト` is U+3000. 2. Record the bytes of each file. 3. Start a new Python 3.13 process from a folder other than the files' folder. 4. In that process, import `troy_mode_trial`. 5. For each file in the order of step 1, call `troy_mode_trial.count_lines` and then `troy_mode_trial.count_words` on the absolute path of the file as a `pathlib.Path`, and print the two counts on one line, separated by one space. Run all steps on Windows 11 on Troy's PC. | The process exits with code 0 and prints the lines `2 4`, `2 4`, and `2 7`. Each file keeps the bytes recorded in step 2. |

No scenario runs on Linux, although requirements section 7 promises the same counts on Windows 11 and on Linux. Claude's scenarios run only in the release test on Troy's PC, which runs Windows 11, and no Linux device of Troy's is on record. v0.2-S02, v0.2-S08, and v0.2-S09 count files with Linux line breaks on Windows instead. The feature tests of F02 run on Linux in CI.

## 3. Performance and stress cases

None. Requirements section 7.1 sets no performance target, so v0.2 has no performance or stress case (R14).

## 4. Devices

| Device | Operating system | Run by |
| --- | --- | --- |
| Troy's PC | Windows 11, with Python 3.13 in the conda environment `troy-mode-trial` | Claude |

Claude's scenarios run only in the release test on Troy's PC, never in CI, so the GitHub Actions runner is not a device for them. v0.2 is a library with no user interface, and every scenario runs through `count_lines` or `count_words` from a script. So no scenario needs a device that only Troy has.

## 5. Acceptance record

None. Troy has not yet accepted v0.2.

## 6. Change log

| Version | Date | Change |
| --- | --- | --- |
| 0.1 | 2026-11-08 | First draft. |
