---
troy-doc: "F04-test-plan"
lang: "en"
version: "1.0"
updated: "2026-11-15"
status: "Approved by Troy on 2026-11-15"
mirror: "test-plan.zh-CN.md"
---

# F04 Word count command: test plan

## 1. Feature

- ID and name: F04 Word count command
- Design: [design.md](design.md)

## 2. Cases

F04 has two external interfaces, and the cases reach each one the way its caller does.

- **`main`.** F04-T01 to F04-T16 call it in the test's own process, as `from troy_mode_trial.cli import main`. They read standard output and standard error with pytest's `capsys`, and make the test's `tmp_path` the working directory with `monkeypatch.chdir`, unless a case says otherwise. Through `capsys` a line break is `\n` on both systems.
- **`wordcount`.** F04-T17 to F04-T22 start the installed program as a new process, with no shell, its working directory set to `tmp_path`, and standard output and standard error captured as bytes. The test finds the program in the scripts folder of the Python that runs the tests, `sysconfig.get_path("scripts")`, with `shutil.which("wordcount", path=...)`, which also finds `wordcount.exe` on Windows. If the program is not there, the test fails. It never skips. In these cases `<NL>` is `os.linesep` as bytes: `\n` on Linux and `\r\n` on Windows, as design 2.1 says.

Each test makes its own files in `tmp_path` and writes them in binary mode, as the exact bytes the case gives. Unless a case says otherwise, `notes.txt` holds `Hello world\n  troy-mode  trial` with no line break at the end, the design's example, which has 4 words. `latin1.txt` holds `café au lait\n` in Latin-1, so its bytes start `63 61 66 E9 20`. `sub` is an empty folder in `tmp_path`. Characters outside ASCII in a file's content or name are UTF-8. The suite runs on Windows 11 and on Linux. A case expects the same result on both, unless it names a system.

"Exactly" means the whole text: for example, standard error is exactly `wordcount: missing.txt: no such file\n` means that line and nothing else. "Usage error" means: `main` raises `SystemExit` whose `code` is `2`, or the program exits with code 2, and standard output is empty, and standard error holds exactly two lines, the first exactly `usage: wordcount FILE` and the second starting with `wordcount: error: `.

Against the mock, every case fails because the command is not implemented. This assumes that the mock `main` raises `NotImplementedError`, and that the mock PR already declares `wordcount = "troy_mode_trial.cli:main"` in `[project.scripts]`, so that CI's install makes the program. Then each `main` case gets `NotImplementedError` instead of its result, and each `wordcount` case gets exit code 1 and a traceback instead of its output (R09). If the mock PR does not declare the program, the `wordcount` cases would fail because the program is missing, which R09 does not accept, so the Test Engineer reports it before the test PR.

| ID | Level | Interface | What it tests | Setup and input | Expected result |
| --- | --- | --- | --- | --- | --- |
| F04-T01 | functional | `main` | The design's example: the count and one line break on standard output, and code 0. | `main(["notes.txt"])`. | Returns `0`, and the type of the result is exactly `int`. Standard output is exactly `4\n`. Standard error is empty. |
| F04-T02 | functional | `main` | The command counts words as F03 counts them. | Three files: `dashes.txt` holds `Wait -- what ... don't x--y 3.14 _`, `only-symbols.txt` holds `-- ... !!!`, and `empty.txt` is empty. Call `main` once for each name. | Each call returns `0` and leaves standard error empty. Standard output is exactly `5\n`, `0\n`, and `0\n`. |
| F04-T03 | unit | `main` | The count is a plain decimal number, with no sign, padding, or separator. | `many.txt` holds `a ` 12,345 times. `main(["many.txt"])`. | Returns `0`. Standard output is exactly `12345\n`. |
| F04-T04 | unit | `main` | `FILE` may be any path form the design allows. | `notes.txt` in `tmp_path`, and copies of it as `sub/notes.txt`, `my notes.txt`, `日本語.txt`, and `-notes.txt`. Five calls, with `tmp_path` as the working directory except the first: `main([<absolute path of notes.txt>])` from the working directory `sub`; `main(["sub/notes.txt"])`; `main(["my notes.txt"])`; `main(["日本語.txt"])`; and `main(["--", "-notes.txt"])`. | Each call returns `0`, writes exactly `4\n` to standard output, and leaves standard error empty. |
| F04-T05 | functional | `main` | The design's example of a missing file. | An empty working directory. `main(["missing.txt"])`. | Returns `2`. Standard output is empty. Standard error is exactly `wordcount: missing.txt: no such file\n`. |
| F04-T06 | unit | `main` | Every case of "no such file" gets that reason, and the message holds the argument as typed, not a resolved or absolute path. | `notes.txt` and the folder `sub` exist. Five calls: `main([""])`, `main(["missing-folder/notes.txt"])`, `main(["notes.txt/inner.txt"])` (a file used as a folder), `main(["sub/../missing.txt"])`, and `main(["缺失.txt"])`. | Each returns `2` and leaves standard output empty. Standard error is exactly `wordcount: : no such file\n`, `wordcount: missing-folder/notes.txt: no such file\n`, `wordcount: notes.txt/inner.txt: no such file\n`, `wordcount: sub/../missing.txt: no such file\n`, and `wordcount: 缺失.txt: no such file\n`. |
| F04-T07 | functional | `main` | A file that is not valid UTF-8 gets the reason `not valid UTF-8`. | `latin1.txt`, and `broken.txt` with the bytes `6F 6B 20 FF FE`. Call `main` once for each name. | Each returns `2` and leaves standard output empty. Standard error is exactly `wordcount: latin1.txt: not valid UTF-8\n` and `wordcount: broken.txt: not valid UTF-8\n`. |
| F04-T08 | functional | `main` | A folder gets the reason `is a folder` on both systems, though Python raises a different error on each. | `main(["sub"])` and `main(["."])`. Runs on Windows and on Linux. | Each returns `2` and leaves standard output empty. Standard error is exactly `wordcount: sub: is a folder\n` and `wordcount: .: is a folder\n`. |
| F04-T09 | functional | `main` | A file the process may not read gets the reason `permission denied`. | Linux only: `secret.txt` holds `one two`, with its mode set to `0o000`. `main(["secret.txt"])`. The test skips on Windows, where a test cannot remove its own read right portably, and when the process runs as root, which can read the file anyway. It restores the mode afterward. | Returns `2`. Standard output is empty. Standard error is exactly `wordcount: secret.txt: permission denied\n`. |
| F04-T10 | unit | `main` | Any other error while the file is opened gets the reason `cannot read file`. | A name of 300 `a` followed by `.txt`, longer than either system allows for one name. On Windows only, also `a?b.txt`, a name that Windows does not allow. Call `main` once for each name. | Each returns `2` and leaves standard output empty. Standard error is exactly `wordcount: <name>: cannot read file\n`, where `<name>` is the argument as given. |
| F04-T11 | functional | `main` | The design's example of a missing argument. | `main([])`. | A usage error. The second line of standard error is exactly `wordcount: error: the following arguments are required: FILE`. |
| F04-T12 | unit | `main` | Every other wrong command line is a usage error, not a count, a file error, or a help text. | `notes.txt` exists, `missing.txt` and `other.txt` do not. Six calls: `main(["notes.txt", "notes.txt"])`, `main(["missing.txt", "other.txt"])`, `main(["-h"])`, `main(["--help"])`, `main(["-x", "notes.txt"])`, and `main(["--"])`. | Each is a usage error. For the first call, the second line of standard error is exactly `wordcount: error: unrecognized arguments: notes.txt`. No call writes a help text or a line `wordcount: <FILE>: <reason>`. |
| F04-T13 | unit | `main` | The program name in every message is `wordcount`, whatever `sys.argv[0]` holds. | `monkeypatch.setattr(sys, "argv", ["other-name.py"])`. Call `main([])`, then `main(["missing.txt"])`. | The first is a usage error whose first line is exactly `usage: wordcount FILE`. The second returns `2` and writes exactly `wordcount: missing.txt: no such file\n` to standard error. |
| F04-T14 | unit | `main` | With no argument, `main` reads `sys.argv[1:]`, as the console script does. | `monkeypatch.setattr(sys, "argv", ["wordcount", "notes.txt"])`. Call `main()`, and also `main(None)`. | Each returns `0` and writes exactly `4\n` to standard output. |
| F04-T15 | unit | `main` | `argv` may be any sequence of `str`, not only a list. | `main(("notes.txt",))`, a tuple. | Returns `0` and writes exactly `4\n` to standard output. |
| F04-T16 | unit | `main` | `main` keeps no state between calls, and writes no file. | `notes.txt` and `latin1.txt` exist. Record the names and bytes of every file in `tmp_path`, the working directory, and `sys.argv`. In one process, call `main` with `["notes.txt"]`, `["missing.txt"]`, `["latin1.txt"]`, and `["notes.txt"]`, and read the output after each call. | The calls return `0`, `2`, `2`, and `0`. Each call's output is only its own: `4\n`; `wordcount: missing.txt: no such file\n`; `wordcount: latin1.txt: not valid UTF-8\n`; and `4\n`. Afterward, `tmp_path` holds the same files with the same bytes, and the working directory and `sys.argv` are unchanged. |
| F04-T17 | integration | `wordcount` | The installed program counts a file, as in the F04 prototype. | Run `wordcount notes.txt`. | Exit code 0. Standard output is exactly `4<NL>`. Standard error is empty. |
| F04-T18 | integration | `wordcount` | The installed program reports a missing file with code 2. | An empty working directory. Run `wordcount missing.txt`. | Exit code 2. Standard output is empty. Standard error is exactly `wordcount: missing.txt: no such file<NL>`. |
| F04-T19 | integration | `wordcount` | The installed program reports a file that is not valid UTF-8 with code 2. | Run `wordcount latin1.txt`. | Exit code 2. Standard output is empty. Standard error is exactly `wordcount: latin1.txt: not valid UTF-8<NL>`. |
| F04-T20 | integration | `wordcount` | The installed program reports a folder with code 2, on both systems. | Run `wordcount sub`. | Exit code 2. Standard output is empty. Standard error is exactly `wordcount: sub: is a folder<NL>`. |
| F04-T21 | integration | `wordcount` | A wrong command line exits with code 2 and a usage line, which tells it apart from a file error. | Three runs: `wordcount` with no argument, `wordcount notes.txt notes.txt`, and `wordcount -h`. | Each is a usage error, with exit code 2. Standard error holds no line that starts with `wordcount: notes.txt: `. |
| F04-T22 | integration | `wordcount` | The arguments reach the program as Troy types them. | Copies of `notes.txt` as `my notes.txt`, `日本語.txt`, and `-notes.txt`. Four runs: `wordcount <absolute path of notes.txt>` from the working directory `sub`; `wordcount "my notes.txt"`, one argument that holds a space; `wordcount 日本語.txt`; and `wordcount -- -notes.txt`. | Each exits with code 0, writes exactly `4<NL>` to standard output, and leaves standard error empty. |

## 3. Performance cases

None. Design 2.1 and 2.2 set no performance target, and requirements 7.1 sets none for the project (R14).

## 4. Not tested

| What | Why |
| --- | --- |
| A bug: an exception other than a file error reaches the caller, Python writes a traceback, and the program exits with code 1. A Ctrl+C is not caught either. | No input through `main` or `wordcount` makes counting raise any other exception. Provoking one would need replacing the counting function inside cli, which tests an internal detail, not an external interface. Against the mock, such a test would also pass, which R09 forbids. |
| `PermissionError` for an unreadable file on Windows. | Removing a file's read right on Windows needs access control lists, which a portable test cannot set and reset reliably. F04-T09 checks the same reason on Linux, and F04-T08 checks the Windows `PermissionError` for a folder. |
| That the file is closed before the command exits. | `main` reads the file only through `count_words`, whose closing F01's cases check. F04-T16 checks that the command writes no file. |
| That output uses `write` and not `print()`. | Both give the same text, so a caller cannot tell them apart. ruff's T20 rule enforces it (architecture section 8). |
| Items of `argv` that are not `str`, and a path that holds the character U+0000. | Design 2.2 allows only `str` items, so other types are outside the contract. No shell can pass U+0000 in an argument, so `wordcount` never receives one. |
| The bytes of a file name outside ASCII on standard error when `wordcount` writes to a pipe on Windows. | Python then encodes standard error in the system's code page, so the bytes depend on the machine. F04-T06 checks the text of such a message through `main`, and F04-T22 checks that such a name reaches the program and is counted. |
| PowerShell finding `wordcount`, `$LASTEXITCODE`, quotes as PowerShell removes them, and the need to install the project again once F04 lands. | CI runs on Linux, without PowerShell. The v0.2 version test plan runs the command in Windows PowerShell on Troy's PC. F04-T22 checks that a quoted argument reaches the program as one argument. |
| Performance. | No performance target exists (R14). |

## 5. Alignment with the Interface Designer

None. The design answered every question this plan raised. The Architect's notes in design section 4 asked for a case for each system or a skip with its reason where Windows and Linux differ: F04-T08 and F04-T20 run on both systems, F04-T09 runs on Linux only with its reason, and F04-T10 adds a Windows-only name. They also asked that a test tell a file error from a wrong command line only by standard error: F04-T12 and F04-T21 do.

## 6. Change log

| Version | Date | Change |
| --- | --- | --- |
| 0.1 | 2026-11-15 | First draft. |
| 1.0 | 2026-11-15 | Approved by Troy. |
