---
troy-doc: "F03-design"
lang: "en"
version: "1.0"
updated: "2026-11-07"
status: "Approved by Troy on 2026-11-07"
mirror: "design.zh-CN.md"
---

# F03 Words need a letter or digit: interface design

## 1. Feature

- ID and name: F03 Words need a letter or digit
- Requirement: [docs/requirements.md](../../requirements.md#4-features)
- Hard dependencies: F01
- Soft dependencies: None

## 2. Interfaces

None. F03 adds no interface. It changes what F01's `count_words` counts, as section 3 describes.

## 3. Changes to existing interfaces

Requirements 2.0 approved this change in the merged [docs] PR [#16](https://github.com/ZJUCao/troy-mode-trial/pull/16).

### 3.1 `count_words` counts only runs that hold a letter or digit

The change is to F01 design 2.1, [`count_words`](../F01-count-words-count-the-words-in-one-utf-8-text-file-a-word-is-a-run-of-characters-that-are-not-white-space/design.md#21-count_words), in the module counting.

What stays as it is:

- Signature: `def count_words(path: str | os.PathLike[str]) -> int:`
- Parameters, errors, side effects, and the performance target (None).
- The function decodes the file as UTF-8 and ignores one byte order mark (U+FEFF) at the start of the file (Q5).
- Every character for which `str.isspace()` is true separates runs (Q1). Line breaks are white space.

What changes:

| Field | F01 design 1.0 | After F03 |
| --- | --- | --- |
| Purpose | A word is a run of one or more characters for which `str.isspace()` is false. | A word is a run of one or more characters for which `str.isspace()` is false, and at least one character in the run is one for which `str.isalnum()` is true. |
| Return value | The number of runs of characters that are not white space. A U+FEFF anywhere other than the first character counts as part of a word. | The number of runs that are words by the new Purpose. A run that holds no character for which `str.isalnum()` is true, such as `--`, `...`, `_`, `😀`, or a lone U+FEFF, is not a word and does not count. A U+FEFF anywhere other than the first character is still not white space: it stays part of the run it is in, and that run is a word only if it holds a letter or digit. A file that is empty, holds only white space, or holds only runs without a letter or digit returns 0. |

A run that holds a letter or digit counts once, whatever else it holds. So `don't`, `x--y`, and `3.14` are one word each.

The doc comment of `count_words` in `src/troy_mode_trial/counting.py` changes to the new word in F03's implementation PR.

Effect on F01's tests: F01-T09 and F01-T11 expect the old word and change with F03. Every other F01 case and the B13 reproduction test keep their expected results.

| Case | Input | F01 expects | F03 expects | Why |
| --- | --- | --- | --- | --- |
| F01-T09 | `café naïve 日本語 😀 Ελληνικά` | `5` | `4` | `😀` holds no letter or digit. |
| F01-T11 | `a <U+FEFF> b`, `a<U+FEFF>b`, and two U+FEFF at the start | `3`, `1`, `1` | `2`, `1`, `0` | A lone U+FEFF is not a word. In the third file the first mark is ignored and the second is a run without a letter or digit. |

Example:

`dashes.txt` is UTF-8 and holds the line `Wait -- what ... don't x--y 3.14 _`. `only-symbols.txt` holds `-- ... !!!` and nothing else.

```python
>>> from troy_mode_trial import count_words
>>> count_words("dashes.txt")
5
>>> count_words("only-symbols.txt")
0
```

## 4. Architect review

| Item | Result | Note |
| --- | --- | --- |
| Fits the module layout and the data model | Pass | The change stays inside `count_words` in the module counting, which owns `src/troy_mode_trial/**` and counts the words of a text. Callers still reach it through `src/troy_mode_trial/__init__.py`. The architecture defines no data model, and the function still takes a path and returns an `int`. |
| Follows the error handling and naming conventions | Pass | The signature, the parameter name, and the errors stay as F01 design 2.1 gives them, so the design still follows Q4: no exception of its own. The architecture 1.0 sets no other error or naming rules. |
| Does not duplicate an existing interface | Pass | F03 adds no interface. It changes the existing `count_words` instead of adding a second counting function next to it. |
| Depends only on features earlier in the order | Pass | F03 depends only on F01, which comes before it in the order (F01, F03, F02) and passes tests on main. |
| Adds no hidden coupling between modules | Pass | The project has one module. The new rule uses only `str.isspace()` and `str.isalnum()` from the standard library and adds no shared or global state. |
| Changes an implemented interface only through the change flow | Pass | Troy approved the changed requirements (2.0) in [docs] PR #16, which is merged. Section 3 names the changed fields of F01 design 2.1, keeps the signature and errors, and lists the two F01 cases, F01-T09 and F01-T11, whose expected results change. I checked the other F01 cases and the B13 test against the new word: their results stay the same. |

| Round | Issue | Resolution |
| --- | --- | --- |
| 1 | No blocking finding. Two notes, which do not block. For the Test Manager: the test name `test_f01_t11_inner_bom_is_word_part` no longer describes the case once a lone U+FEFF stops counting. For the Developer: keep `count_words` within 50 lines (R04), for example with a private helper that tells whether a run holds a letter or digit. | Approved in round 1. |

## 5. Change log

| Version | Date | Change |
| --- | --- | --- |
| 0.1 | 2026-11-07 | First draft. |
