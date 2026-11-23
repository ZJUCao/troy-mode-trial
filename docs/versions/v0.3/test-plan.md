---
troy-doc: "v0.3-test-plan"
lang: "en"
version: "0.1"
updated: "2026-11-23"
status: "Draft."
mirror: "test-plan.zh-CN.md"
---

# v0.3 version test plan

## 1. Version

- Version: v0.3
- Features: F05, F06
- Requirements: [docs/requirements.md](../../requirements.md#6-version-plan)

## 2. End-to-end scenarios

Every test makes its own files in a temporary folder. It writes each file in binary mode, as the exact bytes the scenario gives, so that Windows never turns `\n` into `\r\n`. Characters outside ASCII are encoded as UTF-8 unless the scenario gives other bytes.

The scenarios follow the `wordcount --lines FILE` and `wordcount --chars FILE` flows in requirements section 3, the F05 and F06 prototypes, the decisions Q7, Q8, and Q10 to Q13, and the error handling in architecture section 6. The designs of F05 and F06 are not written yet. So the scenarios rely only on what the requirements, the prototypes, and the approved F04 design already fix:

- A file error prints one line `wordcount: <FILE>: <reason>` to standard error and exits with code 2 (ADR-0002). Q8 and F06's requirement say that each option gives the same message and exit code as `wordcount FILE`. So for a file that is not valid UTF-8, a scenario compares the option's output with the output of `wordcount FILE` for the same file, instead of fixing a reason text.
- A wrong command line exits with code 2, leaves standard output empty, and writes a usage line to standard error. The designs may change the usage line to show the new options, so a scenario checks only that standard error starts with `usage:`.

The scenarios run the installed command, as Troy does. The release test runs in the conda environment `troy-mode-trial` with the project installed, so `wordcount.exe` is in the environment's scripts folder and on `PATH`. If no `wordcount` is on `PATH`, the test fails. It never skips.

- v0.3-S01 to v0.3-S14 start the `wordcount` that is on `PATH`, the program that PowerShell starts for `wordcount`, as a new process with the scenario's arguments. Each test captures standard output, standard error, and the exit code.
- v0.3-S15 runs the commands in Windows PowerShell, `powershell.exe -NoProfile -NonInteractive -Command`, to check that PowerShell finds the command with each option and that `$LASTEXITCODE` holds its exit code.

When a scenario compares output, it reads `\r\n` as `\n`. "One line break" means one `\n` or one `\r\n` at the end. Unless a scenario says otherwise, the working directory is the files' folder.

### 2.1 Count lines in PowerShell (F05)

v0.3-S01 to v0.3-S06 run `wordcount --lines`. The command counts lines as F02 counts them: `\n`, `\r\n`, and `\r` each end one line, a last line without a line break still counts, and an empty file has 0 lines (Q2, Q3).

### 2.2 Count characters in PowerShell (F06)

v0.3-S07 to v0.3-S12 run `wordcount --chars`. A character is one Unicode code point of the decoded text, line ends included. `\r\n` is two characters, and the command translates no line end (Q11). One byte order mark at the start of the file is not counted (Q12).

### 2.3 Wrong command lines and PowerShell (F05 and F06)

v0.3-S13 and v0.3-S14 check the command lines that requirements section 8 and the decisions Q7, Q10, and Q13 rule out. v0.3-S15 and v0.3-S16 run both options in PowerShell, as Troy does.

| ID | Scenario | Run by | Steps | Expected result |
| --- | --- | --- | --- | --- |
| v0.3-S01 | Count the lines of a file with the option, and its words without it, as in the F05 prototype. | Claude | 1. Write `notes.txt` with `Hello world\n  troy-mode  trial\n`. 2. Run `wordcount --lines notes.txt`. 3. Run `wordcount notes.txt`. | Step 2 prints exactly `2` and one line break. Step 3 prints exactly `4` and one line break. Both runs leave standard error empty and exit with code 0. |
| v0.3-S02 | Count the lines of a file that does not exist, as in the F05 prototype. | Claude | 1. Make an empty folder the working directory. 2. Run `wordcount --lines missing.txt`. | Standard output is empty. Standard error is exactly `wordcount: missing.txt: no such file` and one line break. The exit code is 2. |
| v0.3-S03 | Count the lines of a file that is not valid UTF-8. | Claude | 1. Write `latin1.txt` with `café au lait\n` in Latin-1, so that its bytes start `63 61 66 E9 20`. 2. Run `wordcount --lines latin1.txt`. 3. Run `wordcount latin1.txt`. | Step 2 leaves standard output empty, writes one line that starts with `wordcount: latin1.txt: ` and one line break to standard error, and exits with code 2. Its standard error and exit code equal those of step 3. |
| v0.3-S04 | Count the lines of an empty file and of a file that holds only one line break. | Claude | 1. Write an empty `empty.txt`. 2. Write `one-break.txt` with `\n` and nothing else. 3. Run `wordcount --lines empty.txt`. 4. Run `wordcount --lines one-break.txt`. | Step 3 prints `0` and one line break. Step 4 prints `1` and one line break. Both runs leave standard error empty and exit with code 0. |
| v0.3-S05 | Count the lines of files with empty lines and with all three line breaks. | Claude | 1. Write `blank-lines.txt` with `first\n\nthird\n`. 2. Write `mixed-breaks.txt` with `one\rtwo\r\nthree\nfour`, with no line break at the end. 3. Run `wordcount --lines blank-lines.txt`. 4. Run `wordcount --lines mixed-breaks.txt`. | Step 3 prints `3` and one line break. Step 4 prints `4` and one line break. Both runs leave standard error empty and exit with code 0. |
| v0.3-S06 | The option gets the same line counts for files made on Windows and on Linux, given by absolute path from another folder. | Claude | 1. Write three files. `windows.txt` holds the bytes `EF BB BF` followed by `Hello world\r\n  troy-mode  trial\r\n`, as Notepad saves it. `linux.txt` holds `Hello world\n  troy-mode  trial\n`. `mixed.txt` holds `Wait -- what ... don't x--y 3.14 _\r\n日本語　テキスト 😀\n`, where the gap between `日本語` and `テキスト` is U+3000. 2. Record the bytes of each file. 3. Make a folder other than the files' folder the working directory. 4. For each file in the order of step 1, run `wordcount --lines` with the absolute path of the file. | The three runs print `2`, `2`, and `2`, each followed by one line break. Each run leaves standard error empty and exits with code 0. Each file keeps the bytes recorded in step 2. |
| v0.3-S07 | Count the characters of a file with the option, and its words without it, as in the F06 prototype. | Claude | 1. Write `notes.txt` with `Hello world\n  troy-mode  trial\n`. 2. Run `wordcount --chars notes.txt`. 3. Run `wordcount notes.txt`. | Step 2 prints exactly `31` and one line break. Step 3 prints exactly `4` and one line break. Both runs leave standard error empty and exit with code 0. |
| v0.3-S08 | Count characters, not bytes, as in the F06 prototype. | Claude | 1. Write `hello.txt` with `你好\r\n`, 8 bytes. 2. Run `wordcount --chars hello.txt`. | Standard output is exactly `4` and one line break. Standard error is empty. The exit code is 0. |
| v0.3-S09 | Count the characters of a file that does not exist, as in the F06 prototype. | Claude | 1. Make an empty folder the working directory. 2. Run `wordcount --chars missing.txt`. | Standard output is empty. Standard error is exactly `wordcount: missing.txt: no such file` and one line break. The exit code is 2. |
| v0.3-S10 | Count the characters of a file that is not valid UTF-8. | Claude | 1. Write `latin1.txt` as in v0.3-S03. 2. Run `wordcount --chars latin1.txt`. 3. Run `wordcount latin1.txt`. | Step 2 leaves standard output empty, writes one line that starts with `wordcount: latin1.txt: ` and one line break to standard error, and exits with code 2. Its standard error and exit code equal those of step 3. |
| v0.3-S11 | Count the characters of an empty file and of a file that holds only a byte order mark. | Claude | 1. Write an empty `empty.txt`. 2. Write `bom-only.txt` with the bytes `EF BB BF` and nothing else. 3. Run `wordcount --chars empty.txt`. 4. Run `wordcount --chars bom-only.txt`. | Steps 3 and 4 each print `0` and one line break. Both runs leave standard error empty and exit with code 0. |
| v0.3-S12 | The option counts each line end as the file holds it, skips the byte order mark, and gets the same count for the same file on Troy's PC, given by absolute path from another folder. | Claude | 1. Write `windows.txt`, `linux.txt`, and `mixed.txt` with the bytes of v0.3-S06, step 1. 2. Write `breaks.txt` with `one\rtwo\r\nthree\nfour`, with no line break at the end. 3. Record the bytes of each file. 4. Make a folder other than the files' folder the working directory. 5. For each file in the order of steps 1 and 2, run `wordcount --chars` with the absolute path of the file. | The four runs print `33`, `31`, `47`, and `19`, each followed by one line break. Each run leaves standard error empty and exits with code 0. Each file keeps the bytes recorded in step 3. |
| v0.3-S13 | Both options in one command get a usage line, not a count. | Claude | 1. Write `notes.txt` as in v0.3-S01. 2. Run `wordcount --lines --chars notes.txt`. 3. Run `wordcount --chars --lines notes.txt`. | For each run, standard output is empty, standard error starts with `usage:`, and the exit code is 2. |
| v0.3-S14 | Other wrong command lines with the options get a usage line, not a count. | Claude | 1. Write `notes.txt` as in v0.3-S01. 2. Run `wordcount --lines` with no file. 3. Run `wordcount --chars` with no file. 4. Run `wordcount --lines notes.txt notes.txt`. 5. Run `wordcount --chars notes.txt notes.txt`. 6. Run `wordcount -l notes.txt`. 7. Run `wordcount -c notes.txt`. | For each run, standard output is empty, standard error starts with `usage:`, and the exit code is 2. |
| v0.3-S15 | Troy counts lines and characters in a PowerShell session, in a folder whose name holds a space, as in the F05 and F06 prototypes. | Claude | 1. Make a folder named `my notes` and write `notes.txt` in it as in v0.3-S01. 2. Make `my notes` the working directory. 3. Run one Windows PowerShell process, `powershell.exe -NoProfile -NonInteractive -Command`, with these commands in order: `wordcount --lines notes.txt`, `Write-Output "exit $LASTEXITCODE"`, `wordcount --chars notes.txt`, `Write-Output "exit $LASTEXITCODE"`, `wordcount --lines missing.txt`, `Write-Output "exit $LASTEXITCODE"`, `wordcount --chars '<absolute path of notes.txt>'`, `Write-Output "exit $LASTEXITCODE"`, `wordcount --chars missing.txt`, and `Write-Output "exit $LASTEXITCODE"`. | Standard output holds exactly the lines `2`, `exit 0`, `31`, `exit 0`, `exit 2`, `31`, `exit 0`, and `exit 2`, in that order. Standard error holds `missing.txt` twice. |
| v0.3-S16 | Troy counts the lines and the characters of a file with Chinese text in Windows Terminal. | Troy | 1. Open Windows Terminal with PowerShell in the conda environment `troy-mode-trial`. 2. Make a folder the working directory. 3. Run `Set-Content -Path chinese.txt -Encoding UTF8 -Value '你好 世界','第二 行'`. 4. Run `wordcount --lines chinese.txt`. 5. Run `wordcount --chars chinese.txt`. 6. Run `wordcount chinese.txt`. | Windows Terminal shows `2`, `13`, and `4`, each on its own line, and no error. |

No scenario runs on Linux, although requirements section 7 promises the same counts on Windows 11 and on Linux. Claude's scenarios run only in the release test on Troy's PC, which runs Windows 11, and no Linux device of Troy's is on record. v0.3-S05, v0.3-S06, and v0.3-S12 count files with Linux line breaks on Windows instead. The feature tests of F05 and F06 run on Linux in CI.

v0.3-S15 uses Windows PowerShell 5.1, `powershell.exe`, because every Windows 11 has it. No scenario runs PowerShell 7, `pwsh`. Both start the same `wordcount.exe`, so v0.3-S01 to v0.3-S14 hold for either.

In v0.3-S16, `Set-Content` writes `你好 世界\r\n第二 行\r\n`, 13 characters. Windows PowerShell 5.1 also writes a byte order mark first, and PowerShell 7 does not. The mark is not counted (Q12), so Troy sees `13` in either shell.

No scenario checks an option after the file, such as `wordcount notes.txt --lines`, or a shortened option, such as `--line`. The requirements give only the form `wordcount --lines FILE` and do not say whether the other forms are wrong command lines. The designs of F05 and F06 decide, and their feature tests check what they decide.

## 3. Performance and stress cases

None. Requirements section 7.1 sets no performance target, so v0.3 has no performance or stress case (R14).

## 4. Devices

| Device | Operating system | Run by |
| --- | --- | --- |
| Troy's PC | Windows 11, with Python 3.13 in the conda environment `troy-mode-trial`, and Windows PowerShell 5.1 | Claude |
| Troy's PC, in Windows Terminal | Windows 11 | Troy |

Claude's scenarios run only in the release test on Troy's PC, never in CI, so the GitHub Actions runner is not a device for them. Every scenario of Claude's runs the `wordcount` command, which a script can start and read on Troy's PC. v0.3-S16 is Troy's: it checks what Windows Terminal itself shows, which no script can read.

## 5. Acceptance record

None. Troy has not yet accepted v0.3.

## 6. Change log

| Version | Date | Change |
| --- | --- | --- |
| 0.1 | 2026-11-23 | First draft, for F05 and F06. |
