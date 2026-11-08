---
troy-doc: "F03-test-plan"
lang: "en"
version: "1.0"
updated: "2026-11-07"
status: "Approved by Troy on 2026-11-07"
mirror: "test-plan.zh-CN.md"
---

# F03 Words need a letter or digit: test plan

## 1. Feature

- ID and name: F03 Words need a letter or digit
- Design: [design.md](design.md)

## 2. Cases

F03 adds no interface. Every case calls F01's `count_words` the way a caller does: `from troy_mode_trial import count_words`. Each test makes its own files in pytest's `tmp_path` and writes them in binary mode, as the exact bytes the case gives, so that Windows never turns `\n` into `\r\n`. In the inputs, `\uXXXX` and `\UXXXXXXXX` name one Unicode character, which the test encodes as UTF-8. The suite runs on Windows 11 and on Linux, and every case expects the same result on both.

The column "F01 result" gives what `count_words` returns under F01's word, before F03 is implemented. Every input of every case gives a different result under F03, so every F03 test fails against the current code (R09), whichever way the Test Engineer splits a case into tests.

| ID | Level | Interface | What it tests | Setup and input | Expected result |
| --- | --- | --- | --- | --- | --- |
| F03-T01 | functional | `count_words` | The design's example: runs without a letter or digit (`--`, `...`, `_`) are not words, and runs that hold one (`don't`, `x--y`, `3.14`) are one word each. | `dashes.txt` holds `Wait -- what ... don't x--y 3.14 _`. Call `count_words` with its path as a `str`. F01 result: `8`. | Returns `5`, and the type of the result is exactly `int`. |
| F03-T02 | functional | `count_words` | The design's second example: a file that holds only runs without a letter or digit returns 0. | `only-symbols.txt` holds `-- ... !!!`. F01 result: `3`. | Returns `0`. |
| F03-T03 | unit | `count_words` | One run of ASCII punctuation or symbols, with no letter or digit, is not a word. The underscore counts as neither a letter nor a digit. | Six files: `--`, `...`, `_`, `!@#$%^&*()`, `"'`, and `+-*/=<>`. F01 result: `1` for each. | Returns `0` for each. |
| F03-T04 | unit | `count_words` | Runs without a letter or digit on several lines, between several kinds of white space, still give 0. | `--\r\n...\n\t_ \v!!!\f`. F01 result: `4`. | Returns `0`. |
| F03-T05 | unit | `count_words` | A run that holds at least one letter or digit counts once, wherever the letter or digit stands in the run and whatever else the run holds. | `don't x--y 3.14 --a-- !1! _x --`. F01 result: `7`. | Returns `6`. Only the last `--` does not count. |
| F03-T06 | unit | `count_words` | Words with letters outside ASCII still count once each, and an emoji alone is not a word. Replaces F01-T09. | `café naïve 日本語 \U0001F600 Ελληνικά` (the fourth run is the emoji U+1F600). F01 result: `5`. | Returns `4`. |
| F03-T07 | unit | `count_words` | Runs of Unicode symbols and punctuation that hold no letter or digit are not words. | `\U0001F600 — «» € © → 。、 …` (emoji, em dash, guillemets, euro sign, copyright sign, right arrow, CJK full stop and comma, ellipsis). F01 result: `8`. | Returns `0`. |
| F03-T08 | unit | `count_words` | "Letter or digit" means `str.isalnum()`: it includes digits and numerals that are not ASCII, and numeric characters that are not decimal digits. | `² ½ Ⅻ ٣ ß -- …` (superscript two, one half, Roman numeral twelve, Arabic-Indic digit three, sharp s, two hyphens, ellipsis). F01 result: `7`. | Returns `5`. |
| F03-T09 | unit | `count_words` | A U+FEFF anywhere other than the first character is not white space. A run made of it alone is not a word, and a run that holds it with a letter is one word. Replaces F01-T11. | Three files: `a ﻿ b`; the bytes `EF BB BF EF BB BF` (two marks at the start, nothing else); and `a﻿b ﻿`. F01 results: `3`, `1`, and `2`. | Returns `2`, `0`, and `1`. |
| F03-T10 | unit | `count_words` | The count stays right in a large file, where a run without a letter or digit, or a run whose only letter or digit is at one end, may cross any internal read boundary. | One file: 100,000 `-` followed by `x`, a space, 100,000 `.`, a line break, `7` followed by 100,000 `_`, a space, then 200,000 copies of `ab -- `. The file is 1,500,005 bytes, larger than 1 MiB. F01 result: `400003`. | Returns `200002`. |

Retired F01 cases: F03 changes the expected results of F01-T09 and F01-T11, which F01's test plan 1.1 moves to its "Not tested" section. F03-T06 and F03-T09 cover their inputs with the new results. In F03's test PR, the Test Engineer removes `test_f01_t09_non_ascii_words` and `test_f01_t11_inner_bom_is_word_part` from `tests/test_count_words.py`, because F01 is accepted and its tests must pass (R10), and these two would fail once F03 is implemented. The new tests take F03 case IDs, so no test keeps the name `test_f01_t11_inner_bom_is_word_part`, which no longer describes the case.

## 3. Performance cases

None. F03 keeps F01's performance target for `count_words`, which is None, and requirements 7.1 sets none for the project (R14).

## 4. Not tested

| What | Why |
| --- | --- |
| The parts of `count_words` that F03 keeps: the signature, the accepted path forms, the errors, ignoring one byte order mark at the start, white space as separator, closing the file, and writing nothing. | F01-T01 to F01-T08, F01-T10, F01-T12 to F01-T21, and the B13 reproduction test check them, and they keep their expected results under F03. A new F03 case for them would pass against the current code, which R09 forbids. |
| The text of the doc comment of `count_words`. | It is not behavior a caller observes through the interface. Design 3.1 asks for the change, and the review of F03's implementation PR checks it. |
| Performance. | No performance target exists (R14). |

## 5. Alignment with the Interface Designer

None. The design answered every question this plan raised.

## 6. Change log

| Version | Date | Change |
| --- | --- | --- |
| 0.1 | 2026-11-07 | First draft. |
