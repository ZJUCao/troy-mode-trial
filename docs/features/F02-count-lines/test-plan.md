---
troy-doc: "F02-test-plan"
lang: "en"
version: "1.0"
updated: "2026-11-17"
status: "Approved by Troy on 2026-11-17"
mirror: "test-plan.zh-CN.md"
---

# F02 Count lines: test plan

## 1. Feature

- ID and name: F02 Count lines: count the lines in one UTF-8 text file. A last line without a line break still counts.
- Design: [design.md](design.md)

## 2. Cases

Every case reaches the function the way a caller does: `from troy_mode_trial import count_lines`. Each test makes its own files in pytest's `tmp_path` and writes them in binary mode, as the exact bytes the case gives, so that Windows never turns `\n` into `\r\n`. In the inputs, `\xXX` and `\uXXXX` name one Unicode character, which the test encodes as UTF-8, and `EF BB BF` names the bytes of a byte order mark. The suite runs on Windows 11 and on Linux, and every case expects the same result on both, except where a case says otherwise.

| ID | Level | Interface | What it tests | Setup and input | Expected result |
| --- | --- | --- | --- | --- | --- |
| F02-T01 | functional | `count_lines` | The design's example: two lines, the second without a line break at the end. | `notes.txt` holds `Hello world\n  troy-mode  trial`. Call `count_lines` with its path as a `str`. | Returns `2`, and the type of the result is exactly `int`. |
| F02-T02 | unit | `count_lines` | `\r\n` ends one line, not two, so Windows line breaks give the same count as in F02-T01. | Two files: `windows.txt` holds `Hello world\r\n  troy-mode  trial`, and a second file holds `Hello world\r\n  troy-mode  trial\r\n`. Call with each path as a `pathlib.Path`. | Returns `2` for each. |
| F02-T03 | unit | `count_lines` | An empty file, and a file that holds only the byte order mark, have no lines (Q3, Q5). | Two files: an empty file, and a file of the bytes `EF BB BF` alone. | Returns `0` for each. |
| F02-T04 | unit | `count_lines` | A file that holds only one line break has one line (Q3), for each of the three line breaks. | Three files: `\n`, `\r\n`, and `\r`. | Returns `1` for each. |
| F02-T05 | unit | `count_lines` | A last line without a line break counts, and a line break at the end does not start another line. | Four files: `a`, `a\n`, `a\nb`, and `a\nb\n`. | Returns `1`, `1`, `2`, and `2`. |
| F02-T06 | unit | `count_lines` | An empty line between two line breaks counts as a line. | Three files: `first\n\nthird\n`, `\n\n\n`, and `\r\n\r\n`. | Returns `3`, `3`, and `2`. |
| F02-T07 | unit | `count_lines` | All three line breaks in one file each end one line (Q2). | `one\rtwo\r\nthree\nfour` | Returns `4`. |
| F02-T08 | unit | `count_lines` | Only a `\r` directly followed by `\n` joins into one line break. Any other order of `\r` and `\n` gives one line per break. | Five files: `\r\r\n`, `\n\r`, `\r\r`, `\r\n\n`, and `a\r\rb`. | Returns `2`, `2`, `2`, `2`, and `3`. |
| F02-T09 | unit | `count_lines` | The other characters that `str.splitlines()` treats as line breaks are ordinary characters for F02. | The design's file `a b\fc\x85d`. Then one file for each of `\v`, `\f`, `\x1c`, `\x1d`, `\x1e`, `\x85`, ` `, and ` `, holding `a`, that character, and `b`. Last, a file `a b\nc `. | Returns `1` for the design's file and for each of the eight files, and `2` for the last file. |
| F02-T10 | unit | `count_lines` | The same text gives the same count whichever line break it uses. | Three files of the same text, `alpha\nbeta\n\ngamma`, `alpha\r\nbeta\r\n\r\ngamma`, and `alpha\rbeta\r\rgamma`. | Returns `4` for each. |
| F02-T11 | unit | `count_lines` | One byte order mark at the start of the file is ignored (Q5), and a U+FEFF anywhere else is ordinary text. | Five files: `EF BB BF` followed by `one\ntwo`; `EF BB BF` followed by `\n`; `EF BB BF` followed by `x`; `EF BB BF EF BB BF`, two marks; and `a\n﻿`. | Returns `2`, `1`, `1`, `1`, and `2`. |
| F02-T12 | unit | `count_lines` | The count stays right in a large file, where a `\r\n` may be split across any internal read boundary. | A file of 100,000 copies of `abcde\r\n` (7 bytes each, so for any read size that is a power of 2 up to 64 KiB, some boundary falls between a `\r` and its `\n`), then 100,000 copies of `x\r`, then 100,000 copies of `y\n`, then one last line of 100,000 `z` characters with no line break. The file holds 1,200,000 bytes, more than 1 MiB. | Returns `300001`. |
| F02-T13 | functional | `count_lines` | Each accepted form of `path` gives the same count. | A file holding `a\nb\nc`. Call with its absolute path as a `str`, as a `pathlib.Path`, and as an object of a test class that implements `__fspath__` and returns a `str`. | Returns `3` for each. |
| F02-T14 | functional | `count_lines` | A relative path is resolved against the current working directory. | A file `lines.txt` holding `alpha\nbeta` in `tmp_path`. Make `tmp_path` the working directory with `monkeypatch.chdir`, then call with `"lines.txt"` and with `pathlib.Path("lines.txt")`. | Returns `2` for each. |
| F02-T15 | functional | `count_lines` | A missing file, or the empty string as `path`, raises Python's own exception (Q4). | A path in `tmp_path` where nothing exists, as a `str` and as a `pathlib.Path`. Then the empty string `""`. | Raises `FileNotFoundError` for each. |
| F02-T16 | functional | `count_lines` | A path that names a folder raises Python's own exception. | `tmp_path` itself, as a `str` and as a `pathlib.Path`. | Raises `IsADirectoryError` or `PermissionError` for each. On Linux, it raises `IsADirectoryError`. |
| F02-T17 | functional | `count_lines` | A file the process may not read raises `PermissionError`. | Linux only: a file holding `one\ntwo`, with its mode set to `0o000`. The test skips on Windows, where a test cannot remove its own read right portably, and when the process runs as root, which can read the file anyway. It restores the mode afterward. | Raises `PermissionError`. |
| F02-T18 | functional | `count_lines` | Content that is not valid UTF-8 raises Python's own exception (Q4). | Three files: `café au lait\n` in Latin-1 (bytes starting `63 61 66 E9 20`); `ok\nfine\n` followed by the cut-off sequence `E6 97`; and `hello\n` encoded as UTF-16 with its byte order mark. | Raises `UnicodeDecodeError` for each. |
| F02-T19 | functional | `count_lines` | A `path` of any other type raises `TypeError`. | Call with `b"lines.txt"` (`bytes`), with the integer file descriptor of an open file that holds `one\ntwo`, with `None`, with `3.5`, and with an object whose `__fspath__` returns `bytes`. The test closes the descriptor afterward. | Raises `TypeError` for each. |
| F02-T20 | functional | `count_lines` | The function closes the file before it returns and before it raises. | Record warnings with `warnings.catch_warnings(record=True)` and `simplefilter("always", ResourceWarning)`. Call `count_lines` once on a file holding `one\ntwo`, and once on a file that raises `UnicodeDecodeError`. Then run `gc.collect()` and rename each file to a new name in `tmp_path`. | No `ResourceWarning` is recorded, and both renames succeed. The rename catches an open file on Windows, which cannot rename one. |
| F02-T21 | functional | `count_lines` | The function writes and stores nothing. | A file holding `one\ntwo\r\n`. Record its bytes, its modification time in nanoseconds, and the list of entries in `tmp_path`. Call `count_lines` twice. | Both calls return `2`. The file's bytes and modification time are unchanged, and `tmp_path` holds the same entries as before. |
| F02-T22 | integration | `count_lines`, `count_words` | The package exports `count_lines` next to `count_words`, and both count the same file as their designs say. | `from troy_mode_trial import count_lines, count_words`. A file holding `EF BB BF` followed by `Hello world\r\n  troy-mode  trial\r\n`. Call `count_lines`, then `count_words`, on its path. | `count_lines` returns `2` and `count_words` returns `4`. `"count_lines"` and `"count_words"` are both in `troy_mode_trial.__all__`. |

## 3. Performance cases

None. The design sets no performance target for `count_lines`, and requirements 7.1 sets none for the project (R14).

## 4. Not tested

| What | Why |
| --- | --- |
| The text of an exception's message, such as `[Errno 2] No such file or directory: 'missing.txt'` in the design's example. | Python writes the message, and the design promises only the exception type (Q4). F02-T15 to F02-T19 check the type. |
| `PermissionError` for an unreadable file on Windows. | Removing a file's read right on Windows needs access control lists, which a portable test cannot set and reset reliably. F02-T17 checks the same behavior on Linux. |
| Which of `IsADirectoryError` and `PermissionError` Windows raises for a folder. | The design allows either on Windows. F02-T16 accepts either there and asks for `IsADirectoryError` on Linux. |
| Performance. | No performance target exists (R14). |

## 5. Alignment with the Interface Designer

None. The design answered every question this plan raised.

## 6. Change log

| Version | Date | Change |
| --- | --- | --- |
| 0.1 | 2026-11-16 | First draft. |
| 1.0 | 2026-11-17 | Approved by Troy. |
