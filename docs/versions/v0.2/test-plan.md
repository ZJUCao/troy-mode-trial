---
troy-doc: "v0.2-test-plan"
lang: "en"
version: "1.0"
updated: "2026-11-17"
status: "Accepted by Troy on 2026-11-17"
mirror: "test-plan.zh-CN.md"
---

# v0.2 version test plan

## 1. Version

- Version: v0.2
- Features: F02, F04
- Requirements: [docs/requirements.md](../../requirements.md#6-version-plan)

## 2. End-to-end scenarios

Every test makes its own files in a temporary folder. It writes each file in binary mode, as the exact bytes the scenario gives, so that Windows never turns `\n` into `\r\n`. Characters outside ASCII are encoded as UTF-8 unless the scenario gives other bytes.

### 2.1 Count lines in a script (F02)

v0.2-S01 to v0.2-S09 follow the user flow in requirements section 3, the F02 prototype, the decisions Q2 to Q5, and F02's design. They call `count_lines`, the name that F02's design fixes. Troy's scripts call it with a path relative to the current working directory, so the scenarios do too, except where a scenario says otherwise. The requirements promise only the type of an exception, not its message (Q4), so a scenario that expects an exception checks the type only.

Q2 names only `\n`, `\r\n`, and `\r` as line breaks. So no scenario uses the other characters that Python's `str.splitlines()` treats as line breaks, such as U+2028 or form feed. F02's design makes them ordinary characters, and F02's feature tests check them.

### 2.2 Count words in PowerShell (F04)

v0.2-S10 to v0.2-S17 follow the `wordcount FILE` flow in requirements section 3, the F04 prototype, and the error handling in architecture section 6. F04's design keeps the prototype's error text `no such file`, and a file error exits with code 2 (ADR-0002), not the prototype's 1.

The scenarios run the installed command, as Troy does. The release test runs in the conda environment `troy-mode-trial` with the project installed, so `wordcount.exe` is in the environment's scripts folder and on `PATH`. If no `wordcount` is on `PATH`, the test fails. It never skips.

- v0.2-S10 to v0.2-S16 start the `wordcount` that is on `PATH`, the program that PowerShell starts for `wordcount`, as a new process with the scenario's arguments. Each test captures standard output, standard error, and the exit code.
- v0.2-S17 runs the commands in Windows PowerShell, `powershell.exe -NoProfile -NonInteractive -Command`, to check that PowerShell finds the command and that `$LASTEXITCODE` holds its exit code.

When a scenario compares output, it reads `\r\n` as `\n`. "One line break" means one `\n` or one `\r\n` at the end. Unless a scenario says otherwise, the working directory is the files' folder.

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
| v0.2-S10 | Count the words of a file with the command, as in the F04 prototype. | Claude | 1. Write `notes.txt` with `Hello world\n  troy-mode  trial`, with no line break at the end. 2. Run `wordcount notes.txt`. | Standard output is exactly `4` and one line break. Standard error is empty. The exit code is 0. |
| v0.2-S11 | Count a file that does not exist with the command, as in the F04 prototype. | Claude | 1. Make an empty folder the working directory. 2. Run `wordcount missing.txt`. | Standard output is empty. Standard error is exactly `wordcount: missing.txt: no such file` and one line break. The exit code is 2. |
| v0.2-S12 | Count a file that is not valid UTF-8 with the command. | Claude | 1. Write `latin1.txt` with `café au lait\n` in Latin-1, so that its bytes start `63 61 66 E9 20`. 2. Run `wordcount latin1.txt`. | Standard output is empty. Standard error is one line that starts with `wordcount: latin1.txt: `, and one line break. The exit code is 2. |
| v0.2-S13 | The command counts words as F03 counts them, as in the F03 prototype. | Claude | 1. Write `dashes.txt` with `Wait -- what ... don't x--y 3.14 _`. 2. Write `only-symbols.txt` with `-- ... !!!` and nothing else. 3. Run `wordcount dashes.txt`. 4. Run `wordcount only-symbols.txt`. | Step 3 prints `5` and one line break. Step 4 prints `0` and one line break. Both runs leave standard error empty and exit with code 0. |
| v0.2-S14 | Count the words of an empty file with the command. | Claude | 1. Write an empty `empty.txt`. 2. Run `wordcount empty.txt`. | Standard output is exactly `0` and one line break. Standard error is empty. The exit code is 0. |
| v0.2-S15 | The command gets the same counts for files made on Windows and on Linux, given by absolute path from another folder. | Claude | 1. Write `windows.txt`, `linux.txt`, and `mixed.txt` with the bytes of v0.2-S09, step 1. 2. Record the bytes of each file. 3. Make a folder other than the files' folder the working directory. 4. For each file in the order of step 1, run `wordcount` with the absolute path of the file as its one argument. | The three runs print `4`, `4`, and `7`, each followed by one line break. Each run leaves standard error empty and exits with code 0. Each file keeps the bytes recorded in step 2. |
| v0.2-S16 | A wrong command line gets a usage line, not a count. | Claude | 1. Write `notes.txt` as in v0.2-S10. 2. Run `wordcount` with no argument. 3. Run `wordcount notes.txt notes.txt`. | For each run, standard output is empty, standard error starts with `usage:`, and the exit code is 2. |
| v0.2-S17 | Troy counts words in a PowerShell session, in a folder whose name holds a space, as in the F04 prototype. | Claude | 1. Make a folder named `my notes` and write `notes.txt` in it as in v0.2-S10. 2. Make `my notes` the working directory. 3. Run one Windows PowerShell process, `powershell.exe -NoProfile -NonInteractive -Command`, with these commands in order: `wordcount notes.txt`, `Write-Output "exit $LASTEXITCODE"`, `wordcount missing.txt`, `Write-Output "exit $LASTEXITCODE"`, `wordcount '<absolute path of notes.txt>'`, and `Write-Output "exit $LASTEXITCODE"`. | Standard output holds exactly the lines `4`, `exit 0`, `exit 2`, `4`, and `exit 0`, in that order. Standard error holds `missing.txt`. |
| v0.2-S18 | Troy counts the words of a file with Chinese text in Windows Terminal. | Troy | 1. Open Windows Terminal with PowerShell in the conda environment `troy-mode-trial`. 2. Make a folder the working directory and write `chinese.txt` in it, UTF-8, with `你好 世界` and a line break, then `第二 行`. 3. Run `wordcount chinese.txt`. | Windows Terminal shows `4` on its own line, and no error. |

No scenario runs on Linux, although requirements section 7 promises the same counts on Windows 11 and on Linux. Claude's scenarios run only in the release test on Troy's PC, which runs Windows 11, and no Linux device of Troy's is on record. v0.2-S02, v0.2-S08, v0.2-S09, and v0.2-S15 count files with Linux line breaks on Windows instead. The feature tests of F02 and F04 run on Linux in CI.

v0.2-S17 uses Windows PowerShell 5.1, `powershell.exe`, because every Windows 11 has it. No scenario runs PowerShell 7, `pwsh`. Both start the same `wordcount.exe`, so v0.2-S10 to v0.2-S16 hold for either.

## 3. Performance and stress cases

None. Requirements section 7.1 sets no performance target, so v0.2 has no performance or stress case (R14).

## 4. Devices

| Device | Operating system | Run by |
| --- | --- | --- |
| Troy's PC | Windows 11, with Python 3.13 in the conda environment `troy-mode-trial`, and Windows PowerShell 5.1 | Claude |
| Troy's PC, in Windows Terminal | Windows 11 | Troy |

Claude's scenarios run only in the release test on Troy's PC, never in CI, so the GitHub Actions runner is not a device for them. Every scenario runs through `count_lines` or `count_words` from a script, or through the `wordcount` command, which a script can start and read on Troy's PC. v0.2-S18 is Troy's: it checks what Windows Terminal itself shows, which no script can read.

## 5. Acceptance record

| Date | Result | Troy's notes |
| --- | --- | --- |
| 2026-11-17 | Accepted as v0.2.0 | Troy ticked every box of the device-test checklist #62 (v0.2-S18 and "I accept v0.2.0") on commit 8505ca9. No notes. No bugs deferred. |

None. Troy has not yet accepted v0.2.

## 6. Change log

| Version | Date | Change |
| --- | --- | --- |
| 0.1 | 2026-11-08 | First draft. |
| 0.2 | 2026-11-14 | v0.2 adds F04, the `wordcount` command. New scenarios v0.2-S10 to v0.2-S17 run the command directly and in Windows PowerShell. Section 2.1 follows F02's approved design, which fixes the name `count_lines` and accepts a `pathlib.Path`. Section 4 adds Windows PowerShell 5.1. The scenarios of F02 do not change. |
| 0.3 | 2026-11-17 | v0.2-S11, v0.2-S12, and v0.2-S17 expect exit code 2 for a file error, as F04's design and ADR-0002 decided. New scenario v0.2-S18, which Troy runs in Windows Terminal, and a device row for it. |
| 1.0 | 2026-11-17 | Accepted by Troy as v0.2.0. |
