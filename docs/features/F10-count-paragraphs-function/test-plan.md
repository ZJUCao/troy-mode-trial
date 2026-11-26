---
troy-doc: "F10-test-plan"
lang: "en"
version: "0.1"
updated: "2026-11-26"
status: "Draft. Being aligned with the Interface Designer."
mirror: "test-plan.zh-CN.md"
---

# F10 Count paragraphs function: test plan

## 1. Feature

- ID and name: F10 Count paragraphs function: returns the number of paragraphs in a text that the caller holds as a Python `str`. A paragraph is a run of lines that are not blank.
- Design: [design.md](design.md)

## 2. Cases

Every case reaches the function the way a caller does: `from troy_mode_trial import count_paragraphs`. The inputs are Python string literals, and the test writes them exactly so. Every character that is invisible or looks like a space is written as an escape: `\xXX` and `\uXXXX` each name one Unicode character, for example `\u3000` (ideographic space), `\u2029` (paragraph separator), and `\ufeff` (byte order mark). The test never types these characters as they are. Where a case lists several inputs, the test checks each input on its own and reports which one failed. The suite runs on Windows 11 and on Linux, and every case expects the same result on both.

| ID | Level | Interface | What it tests | Setup and input | Expected result |
| --- | --- | --- | --- | --- | --- |
| F10-T01 | functional | `count_paragraphs` | The design's and the prototype's examples. | Four calls: `"First line\nstill the first paragraph\n\nSecond paragraph\n"`, `"One\r\n  \t\r\nTwo\r\n\r\n\r\nThree"`, `"\n\n   \n"`, and `""`. | Returns `2`, `3`, `0`, and `0`. The type of each result is exactly `int`. |
| F10-T02 | unit | `count_paragraphs` | An empty text, and a text of only blank lines, have no paragraph. | `""`, `"\n"`, `"\r"`, `"\r\n"`, `" "`, `"\t"`, `"\n\n   \n"`, `"\t\n\r\n\r \r"`, and `"\u3000\n\u3000"`. | Returns `0` for each. |
| F10-T03 | unit | `count_paragraphs` | A run of lines that are not blank is one paragraph, and blank lines at the start or the end count for nothing. | `"One"`, `"One\n"`, `"a\nb\nc"`, `"\n\nOne\n\n"`, `"  \n\t\nOne\r\n \r\n"`, and `"\r\rOne\r\r"`. | Returns `1` for each. |
| F10-T04 | unit | `count_paragraphs` | Any number of blank lines between two paragraphs separates them once. | `"a\n\nb"`, `"a\n\n\n\nb"`, `"a\n \n\t\n\nb"`, and `"a\nb\n\nc\nd\n\n\n\ne\n"`. | Returns `2`, `2`, `2`, and `3`. |
| F10-T05 | unit | `count_paragraphs` | A line is blank when every character in it is white space as `str.isspace()` defines it (Q27, Q1), also the white space that is not a space or a tab. | One text `"a\n" + c + "\nb"` for each `c` in: `" "`, `"\t"`, `"\u3000"`, `"\xa0"`, `"\f"`, `"\v"`, `"\x1c"`, `"\x1d"`, `"\x1e"`, `"\x85"`, `"\u2028"`, `"\u2029"`, and `" \t\u3000\f "`. | Returns `2` for each. |
| F10-T06 | unit | `count_paragraphs` | A line that holds a character that is not white space is not blank, also when the character is invisible. | `"a\n\u200b\nb"`, `"a\n \u200b \nb"`, `"a\n\ufeff\nb"`, and `"a\n\n\u200b\n\nb"`. | Returns `1`, `1`, `1`, and `3`. |
| F10-T07 | unit | `count_paragraphs` | Exactly `\n`, `\r\n`, and a lone `\r` end a line (Q28). A `\r` directly followed by `\n` is one line end. | `"a\r\nb"`, `"a\rb"`, `"a\rb\r\rc"`, `"a\n\rb"`, `"a\r\rb"`, `"a\r\n\r\nb"`, `"a\r\n\rb"`, and `"a\r\r\nb"`. | Returns `1`, `1`, `2`, `2`, `2`, `2`, `2`, and `2`. |
| F10-T08 | unit | `count_paragraphs` | The other characters that `str.splitlines()` treats as line breaks are ordinary characters, as in F02. | For each `c` in `"\v"`, `"\f"`, `"\x1c"`, `"\x1d"`, `"\x1e"`, `"\x85"`, `"\u2028"`, and `"\u2029"`: the text `"a" + c + "b"`, and the text `"a" + c + c + "b"`. | Returns `1` for each of the 16 texts. A split with `str.splitlines()` would give `2` for the second text of each pair. |
| F10-T09 | unit | `count_paragraphs` | The same text gives the same count whichever line ends it uses, also when they are mixed. | `"alpha\nbeta\n\ngamma\n\n\ndelta\n"`, `"alpha\r\nbeta\r\n\r\ngamma\r\n\r\n\r\ndelta\r\n"`, `"alpha\rbeta\r\rgamma\r\r\rdelta\r"`, and `"alpha\r\nbeta\r\rgamma\n\r\ndelta"`. | Returns `3` for each. |
| F10-T10 | unit | `count_paragraphs` | One U+FEFF at the start of the text is ignored (Q29). A second one at the start, or one anywhere else, is an ordinary character. | `"\ufeffa\n\nb"`, `"\ufeff"`, `"\ufeff\n \n"`, `"\ufeff\r\n\r\nOne"`, `"\ufeff\ufeff"`, `"\ufeff\ufeff\n\nb"`, `"a\n\n\ufeff"`, and `"a\n\ufeff\nb"`. | Returns `2`, `0`, `0`, `1`, `1`, `2`, `2`, and `1`. |
| F10-T11 | functional | `count_paragraphs` | The function counts the text it gets and never treats it as a path, even when a file of that name exists. | In `tmp_path`, `notes.txt` holds the bytes of `Hello world\n\ntroy-mode trial\n`. Make `tmp_path` the working directory with `monkeypatch.chdir`. Call with `"notes.txt"`, then with `str(tmp_path / "notes.txt")`. | Returns `1` for each, the one line of the path text, not the `2` paragraphs of the file. |
| F10-T12 | functional | `count_paragraphs` | A subclass of `str` is accepted and counted like a `str`. | A test class `class Text(str)`. Call with `Text("One\n\nTwo")` and with `Text("")`. | Returns `2` and `0`. The type of each result is exactly `int`. |
| F10-T13 | functional | `count_paragraphs` | A `text` that is not a `str` raises `TypeError`, whose message names the type it got. | Call with `b"One\n\nTwo"` (`bytes`), `None`, `3`, and `pathlib.Path("notes.txt")`, where `notes.txt` exists in the working directory as in F10-T11. | Raises `TypeError` for each. For `bytes`, the message is exactly `text must be str, not bytes`. For each of the others, the message starts with `text must be str, not ` and holds `type(x).__name__` of the value `x` passed. |
| F10-T14 | functional | `count_paragraphs` | The function keeps no state, writes nothing, and leaves `text` as it is. | Make `tmp_path` the working directory. Record its entries. Let `t = "One\r\n\r\nTwo\n"` and keep `copy = "".join(list(t))`. Call `count_paragraphs(t)` three times, with a call on `"x\n\ny\n\nz"` between the first and second. | Each call on `t` returns `2`, and the call between returns `3`. `t == copy`. `tmp_path` holds the same entries as before. |
| F10-T15 | integration | `count_paragraphs`, `count_lines` | The package exports `count_paragraphs` and keeps every name it exported before, and the design's example of a file read by the caller works. | `from troy_mode_trial import count_chars, count_lines, count_longest, count_paragraphs, count_words`. In `tmp_path`, `notes.txt` holds the bytes of `Hello world\n\ntroy-mode trial`. Call `count_paragraphs(pathlib.Path(...).read_text(encoding="utf-8"))` on it, and `count_lines` on its path. | `count_paragraphs` returns `2` and `count_lines` returns `3`. `troy_mode_trial.__all__` holds `"count_paragraphs"`, `"count_chars"`, `"count_lines"`, `"count_longest"`, and `"count_words"`. |

## 3. Performance cases

None. The design sets no performance target for `count_paragraphs` (R14).

## 4. Not tested

| What | Why |
| --- | --- |
| That `wordcount` and `main` print, write, and return exactly what they did before, and have no option for paragraphs. | F10 changes neither interface (design section 3). The existing test cases of F04 to F09 already check their output and keep running. A new test of an unchanged behavior would pass against the mock, which R09 does not allow. |
| The exact message text of `TypeError` for types other than `bytes`. | The design gives the exact text only for `bytes`, and the form `text must be str, not <type>` for the rest. F10-T13 checks the exact text for `bytes`, and the form and the type's name for the others. |
| Performance, and texts larger than the cases above. | No performance target exists (R14). The design promises nothing about size. |

## 5. Alignment with the Interface Designer

None. The design answered every question this plan raised. Following the Architect's round 1 note on the design, this plan writes the U+3000, U+2029, and U+FEFF inputs of the design's table in section 2.1 as escapes (`\u3000`, `\u2029`, `\ufeff`). I read those rows by code point: they hold `"a\n\u3000\nb"`, `"a\u2029b"`, `"\ufeffa\n\nb"`, `"\ufeff"`, `"\ufeff\ufeff"`, and `"a\n\ufeff\nb"`, and F10-T05, F10-T08, and F10-T10 cover each.

## 6. Change log

| Version | Date | Change |
| --- | --- | --- |
| 0.1 | 2026-11-26 | First draft. |
