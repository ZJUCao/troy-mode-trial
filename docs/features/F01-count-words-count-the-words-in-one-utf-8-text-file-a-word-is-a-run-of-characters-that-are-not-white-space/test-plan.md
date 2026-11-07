---
troy-doc: "F01-test-plan"
lang: "en"
version: "1.0"
updated: "2026-11-07"
status: "Approved by Troy on 2026-11-07"
mirror: "test-plan.zh-CN.md"
---

# F01 Count words: test plan

## 1. Feature

- ID and name: F01 Count words: count the words in one UTF-8 text file. A word is a run of characters that are not white space.
- Design: [design.md](design.md)

## 2. Cases

Every case reaches the function the way a caller does: `from troy_mode_trial import count_words`. Each test makes its own files in pytest's `tmp_path` and writes them in binary mode, as the exact bytes the case gives, so that Windows never turns `\n` into `\r\n`. In the inputs, `\uXXXX` names one Unicode character, which the test encodes as UTF-8. The suite runs on Windows 11 and on Linux, and every case expects the same result on both, except where a case says otherwise.

| ID | Level | Interface | What it tests | Setup and input | Expected result |
| --- | --- | --- | --- | --- | --- |
| F01-T01 | functional | `count_words` | The design's example: words on two lines, with leading, trailing, and repeated spaces, and no line break at the end. | `notes.txt` holds `Hello world\n  troy-mode  trial`. Call `count_words` with its path as a `str`. | Returns `4`, and the type of the result is exactly `int`. |
| F01-T02 | unit | `count_words` | An empty file has no words (Q3). | An empty file. | Returns `0`. |
| F01-T03 | unit | `count_words` | A file of white space only has no words (Q3). | Three files: `   `, `\n`, and `\t \r\n \v\f\r`. | Returns `0` for each. |
| F01-T04 | unit | `count_words` | One run of characters with no white space is one word, even when it holds punctuation and digits. | Three files: `a`, `troy-mode`, and `x=1,y=2;`. | Returns `1` for each. |
| F01-T05 | unit | `count_words` | Each ASCII white space character separates words, and a run of several counts as one gap. | `\tone  two\t\tthree\vfour\ffive \n six  ` | Returns `6`. |
| F01-T06 | unit | `count_words` | Unicode white space separates words (Q1). | `甲　乙 丙 丁 戊\u0085己` | Returns `6`. |
| F01-T07 | unit | `count_words` | A character for which `str.isspace()` is false does not separate words, even when it looks blank. | `a​b c⁠d` (zero width space and word joiner) | Returns `2`. |
| F01-T08 | unit | `count_words` | `\n`, `\r\n`, and `\r` are white space and give the same count. | Three files with the same words: `one two\nthree\nfour`, `one two\r\nthree\r\nfour`, and `one two\rthree\rfour`. A fourth file ends `four\r\n`. | Returns `4` for each of the four files. |
| F01-T09 | unit | `count_words` | Words with characters outside ASCII, which take two to four bytes in UTF-8, each count once. | `café naïve 日本語 😀 Ελληνικά` | Returns `5`. |
| F01-T10 | unit | `count_words` | One byte order mark at the start of the file is ignored (Q5). | Four files: the bytes `EF BB BF` followed by `one two`; `EF BB BF` alone; `EF BB BF` followed by ` word`; `EF BB BF` followed by `\n`. | Returns `2`, `0`, `1`, and `0`. |
| F01-T11 | unit | `count_words` | A U+FEFF anywhere other than the first character is not white space and is part of a word. | Three files: `a ﻿ b`, `a﻿b`, and `﻿﻿` (two marks at the start). | Returns `3`, `1`, and `1`. |
| F01-T12 | unit | `count_words` | The count stays right in a large file, where a word or a run of white space may cross any internal read boundary. | A file of 200,000 copies of `word ` with a single line break in place of every 1,000th space, followed by one word of 100,000 `x` characters, then `　end`. The file is larger than 1 MiB. | Returns `200002`. |
| F01-T13 | functional | `count_words` | Each accepted form of `path` gives the same count. | A file holding `one two three`. Call with its absolute path as a `str`, as a `pathlib.Path`, and as an object of a test class that implements `__fspath__` and returns a `str`. | Returns `3` for each. |
| F01-T14 | functional | `count_words` | A relative path is resolved against the current working directory. | A file `words.txt` holding `alpha beta` in `tmp_path`. Make `tmp_path` the working directory with `monkeypatch.chdir`, then call with `"words.txt"` and with `pathlib.Path("words.txt")`. | Returns `2` for each. |
| F01-T15 | functional | `count_words` | A missing file raises Python's own exception (Q4). | A path in `tmp_path` where nothing exists, as a `str` and as a `pathlib.Path`. | Raises `FileNotFoundError` for each. |
| F01-T16 | functional | `count_words` | A path that names a folder raises Python's own exception. | `tmp_path` itself, as a `str`. | Raises `IsADirectoryError` or `PermissionError`. On Linux, it raises `IsADirectoryError`. |
| F01-T17 | functional | `count_words` | A file the process may not read raises `PermissionError`. | Linux only: a file holding `one two`, with its mode set to `0o000`. The test skips on Windows, where a test cannot remove its own read right portably, and when the process runs as root, which can read the file anyway. It restores the mode afterward. | Raises `PermissionError`. |
| F01-T18 | functional | `count_words` | Content that is not valid UTF-8 raises Python's own exception (Q4). | Three files: `café` in Latin-1 (`63 61 66 E9`, as in the prototype); `ok ` followed by the cut-off sequence `E6 97`; and `hello` encoded as UTF-16 with its byte order mark. | Raises `UnicodeDecodeError` for each. |
| F01-T19 | functional | `count_words` | A `path` of any other type raises `TypeError`. | Call with `b"words.txt"` (`bytes`), with the integer file descriptor of an open file that holds `one two`, with `None`, with `3.5`, and with an object whose `__fspath__` returns `bytes`. The test closes the descriptor afterward. | Raises `TypeError` for each. |
| F01-T20 | functional | `count_words` | The function closes the file before it returns and before it raises. | Record warnings with `warnings.catch_warnings(record=True)` and `simplefilter("always", ResourceWarning)`. Call `count_words` once on a file holding `one two`, and once on a file that raises `UnicodeDecodeError`. Then run `gc.collect()` and rename each file to a new name in `tmp_path`. | No `ResourceWarning` is recorded, and both renames succeed. The rename catches an open file on Windows, which cannot rename one. |
| F01-T21 | functional | `count_words` | The function writes and stores nothing. | A file holding `one two`. Record its bytes, its modification time in nanoseconds, and the list of entries in `tmp_path`. Call `count_words` twice. | Both calls return `2`. The file's bytes and modification time are unchanged, and `tmp_path` holds the same entries as before. |

## 3. Performance cases

None. The design sets no performance target for `count_words`, and requirements 7.1 sets none for the project (R14).

## 4. Not tested

| What | Why |
| --- | --- |
| The text of an exception's message, such as `[Errno 2] No such file or directory: 'missing.txt'` in the design's example. | Python writes the message, and the design promises only the exception type (Q4). F01-T15 to F01-T19 check the type. |
| `PermissionError` for an unreadable file on Windows. | Removing a file's read right on Windows needs access control lists, which a portable test cannot set and reset reliably. F01-T17 checks the same behavior on Linux. |
| Performance. | No performance target exists (R14). |

## 5. Alignment with the Interface Designer

None. The design answered every question this plan raised.

## 6. Change log

| Version | Date | Change |
| --- | --- | --- |
| 0.1 | 2026-11-07 | First draft. |
