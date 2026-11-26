---
troy-doc: "F10-design"
lang: "en"
version: "0.1"
updated: "2026-11-26"
status: "Draft. In Architect review."
mirror: "design.zh-CN.md"
---

# F10 Count paragraphs function: interface design

## 1. Feature

- ID and name: F10 Count paragraphs function
- Requirement: [docs/requirements.md](../../requirements.md#4-features)
- Hard dependencies: F04
- Soft dependencies: None

## 2. Interfaces

F10 adds one interface, the library function `count_paragraphs`, in the module counting. It adds no file: the function lives in `src/troy_mode_trial/counting.py`, which counting already owns (architecture section 3). F10 adds no `wordcount` option, message, or file (requirements F10 and section 8).

### 2.1 `count_paragraphs`

- Module: counting, in `src/troy_mode_trial/counting.py`. Callers import it from the package `troy_mode_trial`: `src/troy_mode_trial/__init__.py` imports it next to `count_chars`, `count_lines`, `count_longest`, and `count_words`, and adds `"count_paragraphs"` to `__all__`.
- Purpose: Returns the number of paragraphs in a text that the caller already holds as a `str`. A paragraph is a run of lines that are not blank. Unlike the other counting functions, it takes the text itself, not a file's path, and reads no file.

Signature:

```python
def count_paragraphs(text: str) -> int:
```

Parameters:

| Name | Type | Meaning | Constraints |
| --- | --- | --- | --- |
| `text` | `str` | The text whose paragraphs are counted, for example the content of a file that the caller has read. | Any `str`, including the empty string and a subclass of `str`. Any other type, such as `bytes`, `None`, or a `pathlib.Path`, raises `TypeError`. The function never treats `text` as a path, so `count_paragraphs("notes.txt")` counts the one line `notes.txt` and returns 1. |

- Return value: `int`, the number of paragraphs in `text`, 0 or more. The function works out the count in four steps.

  1. **Byte order mark.** If `text` starts with U+FEFF, the function ignores that one character (Q29). A U+FEFF anywhere else, also a second one at the start, is an ordinary character.
  2. **Lines.** It splits the rest into lines. Exactly three sequences end a line: `\n`, `\r\n`, and `\r` (Q28). A `\r` directly followed by `\n` is one line end, `\r\n`, not two, so `a\r\nb` is two lines with no empty line between them. No other character ends a line: the other characters that Python's `str.splitlines()` treats as line breaks, `\v` (U+000B), `\f` (U+000C), U+001C, U+001D, U+001E, U+0085, U+2028, and U+2029, are ordinary characters, as in F02. The function must therefore not split with `str.splitlines()`. A text that ends with a line end has no extra empty line after it; this does not change the count, because such a line would be blank.
  3. **Blank lines.** A line is blank if it is empty or every character in it is one for which `str.isspace()` is true (Q27, Q1). So a line of spaces, tabs, U+3000, `\f`, or U+2028 is blank. A line that holds any other character is not blank, also when that character is invisible, such as U+200B or U+FEFF, because `str.isspace()` is false for them.
  4. **Paragraphs.** A paragraph is a maximal run of lines that are not blank. The result is the number of such runs: every line that is not blank and is either the first line or follows a blank line starts one paragraph. Any number of blank lines between two paragraphs separates them once, and blank lines at the start or the end count for nothing. An empty text, or a text of only blank lines, returns 0.

  | `text` (as a Python literal) | Result | Why |
  | --- | --- | --- |
  | `""` | `0` | Empty text. |
  | `"\n\n   \n"` | `0` | Only blank lines. |
  | `"\r\n"` | `0` | One empty line. |
  | `"One"` | `1` | One line, no line end. |
  | `"\n\nOne\n\n"` | `1` | Blank lines at the start and end count for nothing. |
  | `"First line\nstill the first paragraph\n\nSecond paragraph\n"` | `2` | The prototype's first example. |
  | `"One\r\n  \t\r\nTwo\r\n\r\n\r\nThree"` | `3` | A line of spaces and a tab is blank, and three blank lines separate once. |
  | `"a\r\nb"` | `1` | `\r\n` is one line end, so no empty line lies between. |
  | `"a\rb\r\rc"` | `2` | A lone `\r` ends a line: the lines are `a`, `b`, an empty line, and `c`. |
  | `"a\n\rb"` | `2` | `\n` then `\r` are two line ends with an empty line between. |
  | `"a\n　\nb"` | `2` | U+3000 is white space, so its line is blank. |
  | `"a\n\f\nb"` | `2` | `\f` is white space, so its line is blank. |
  | `"a\fb"` | `1` | `\f` does not end a line. |
  | `"a b"` | `1` | U+2029 does not end a line. |
  | `"﻿a\n\nb"` | `2` | The byte order mark at the start is ignored. |
  | `"﻿"` | `0` | Only the byte order mark. |
  | `"﻿﻿"` | `1` | Only the first U+FEFF is ignored, and the second is not white space. |
  | `"a\n﻿\nb"` | `1` | A line of U+FEFF is not blank, so the three lines are one paragraph. |

Errors:

The function reads no file, so it raises no file error (requirements section 3). It defines no exception of its own (architecture section 6).

| Error | When |
| --- | --- |
| `TypeError` | `text` is not a `str`, for example `bytes`, `None`, an `int`, or a `pathlib.Path`. The message names the type it got, for example `text must be str, not bytes`. As P01 asks, the code builds the message in a variable before it raises. |

- Side effects: None. The function reads no file, writes nothing, keeps no state, and leaves `text` as it is. The same `text` always gives the same result, on Windows and on Linux.
- Performance target: None

Example:

`notes.txt` is UTF-8 and holds three lines: `Hello world`, an empty line, and `troy-mode trial`.

```python
>>> from pathlib import Path
>>> from troy_mode_trial import count_paragraphs
>>> count_paragraphs("First line\nstill the first paragraph\n\nSecond paragraph\n")
2
>>> count_paragraphs("One\r\n  \t\r\nTwo\r\n\r\n\r\nThree")
3
>>> count_paragraphs("\n\n   \n")
0
>>> count_paragraphs("")
0
>>> count_paragraphs(Path("notes.txt").read_text(encoding="utf-8"))
2
>>> count_paragraphs(b"One\n\nTwo")
Traceback (most recent call last):
  ...
TypeError: text must be str, not bytes
```

## 3. Changes to existing interfaces

None. F10 is a new feature that Troy approved in requirements 9.0 (commit `ae27a27`). `src/troy_mode_trial/__init__.py` adds the name `count_paragraphs` to its imports and to `__all__`, and keeps every name it exports now. `count_chars`, `count_lines`, `count_longest`, and `count_words` keep their signatures, behavior, and errors. F10 uses no interface of F04 and changes none: `wordcount` and `main` print, write, and return exactly what they did before. No existing test case changes or retires.

## 4. Architect review

| Item | Result | Note |
| --- | --- | --- |
| Fits the module layout and the data model | Pass | The function goes in `src/troy_mode_trial/counting.py` and is exported from `src/troy_mode_trial/__init__.py`, the external interface of counting; counting owns both files, so the module table needs no change. It reads and writes no file and keeps no state, so it adds nothing to the data model in section 5 and keeps the rule of section 8 that counting writes no file. F09 may also add a name to `__init__.py`; the two changes touch the same file but not the same interface. |
| Follows the error handling and naming conventions | Pass | It defines no exception of its own and raises only Python's `TypeError`, as section 6 asks for counting. The message `text must be str, not <type>` follows the form of the existing `path must be str or os.PathLike, not <type>`, and the design builds it in a variable first, as P01 asks. The name follows `count_` plus the thing counted, in snake_case. |
| Does not duplicate an existing interface | Pass | No existing function counts paragraphs or takes the text itself. The line ends follow `count_lines` (`\n`, `\r\n`, a lone `\r`, never `str.splitlines()`) and blank lines follow the white space of Q1, so the design reuses the existing definitions instead of adding new ones. |
| Depends only on features earlier in the order | Pass | Its only hard dependency, F04, comes before F10 in the order, and F10 is last. The design uses no interface of F04. |
| Adds no hidden coupling between modules | Pass | Only counting changes. cli and settings do not change, and the function imports neither of them. |
| Changes an implemented interface only through the change flow | Pass | No implemented interface changes. `__init__.py` only adds one name to its imports and to `__all__` and keeps every name it exports now. |
| The summary for Troy says what the design says, and lists every point Troy decides | Pass | The summary gives the call, the text-not-path input, the blank-line and paragraph rules, the line ends, the byte order mark, the `TypeError`, and that `wordcount` does not change, all as the design fixes them. Its risks match the design's rows for U+200B, a U+FEFF that is not at the start, U+2029, and `bytes`. Q27 to Q29 are decided, and nothing is left for Troy. |

| Round | Issue | Resolution |
| --- | --- | --- |
| 1 | No blocking finding. One note for the Interface Designer, which does not block: in the table in step 4 of section 2.1, the rows for U+3000, U+2029, and U+FEFF hold these characters as they are, so the rows "Only the byte order mark." and "Only the first U+FEFF is ignored" look like the empty text, and the U+2029 row looks like a plain space. Writing them as escapes such as `"\ufeff"`, `"a\u2029b"`, and `"a\n\u3000\nb"` in a later version would help the Test Manager copy them right. | Approved in round 1. |

## 5. Change log

| Version | Date | Change |
| --- | --- | --- |
| 0.1 | 2026-11-26 | First draft. |
