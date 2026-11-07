---
troy-doc: "F01-design"
lang: "en"
version: "1.0"
updated: "2026-11-07"
status: "Approved by Troy on 2026-11-07"
mirror: "design.zh-CN.md"
---

# F01 Count words: interface design

## 1. Feature

- ID and name: F01 Count words: count the words in one UTF-8 text file. A word is a run of characters that are not white space.
- Requirement: [docs/requirements.md](../../requirements.md#4-features)
- Hard dependencies: None
- Soft dependencies: None

## 2. Interfaces

### 2.1 `count_words`

- Module: counting. Callers import it from the package `troy_mode_trial`, which `src/troy_mode_trial/__init__.py` defines.
- Purpose: Reads one UTF-8 text file and returns the number of words in it. A word is a run of one or more characters for which `str.isspace()` is false.

Signature:

```python
def count_words(path: str | os.PathLike[str]) -> int:
```

Parameters:

| Name | Type | Meaning | Constraints |
| --- | --- | --- | --- |
| `path` | `str \| os.PathLike[str]` | The path of the file to count, absolute or relative to the current working directory. | Names one existing, readable, regular file whose content is valid UTF-8. `bytes` paths are not accepted. |

- Return value: `int`, the number of words in the file, 0 or more. The function decodes the file as UTF-8 and ignores one byte order mark (U+FEFF) at the start of the file (Q5). Every character for which `str.isspace()` is true separates words, including Unicode white space such as U+3000 (Q1). Line breaks are white space, so `\n`, `\r\n`, and `\r` give the same count. A file that is empty or holds only white space returns 0 (Q3). A U+FEFF anywhere other than the first character is not white space and counts as part of a word.

Errors:

The function defines no exception of its own (Q4). It lets Python's own exception reach the caller.

| Error | When |
| --- | --- |
| `FileNotFoundError` | No file exists at `path`. |
| `IsADirectoryError` or `PermissionError` | `path` names a folder. Linux raises `IsADirectoryError`. Windows raises `PermissionError`. |
| `PermissionError` | The process may not read the file. |
| `UnicodeDecodeError` | The file content is not valid UTF-8. |
| `TypeError` | `path` is neither a `str` nor an `os.PathLike[str]`. |

- Side effects: The function opens the file for reading and closes it before it returns or raises. It writes, sends, and stores nothing.
- Performance target: None

Example:

`notes.txt` is UTF-8 and holds the two lines `Hello world` and `  troy-mode  trial`, the second without a line break at the end. `empty.txt` is empty.

```python
>>> from troy_mode_trial import count_words
>>> count_words("notes.txt")
4
>>> count_words("empty.txt")
0
>>> count_words("missing.txt")
Traceback (most recent call last):
  ...
FileNotFoundError: [Errno 2] No such file or directory: 'missing.txt'
```

## 3. Changes to existing interfaces

None

## 4. Architect review

| Item | Result | Note |
| --- | --- | --- |
| Fits the module layout and the data model | Pass | `count_words` belongs to the module counting, which owns `src/troy_mode_trial/**`. Callers reach it through the package `troy_mode_trial`, the module's only external interface. The architecture defines no data model, and the function keeps no data: it takes a path and returns an `int`. |
| Follows the error handling and naming conventions | Pass | The architecture 1.0 sets no error or naming rules of its own. The design follows requirement Q4: it defines no exception and lets Python's own exceptions reach the caller. The name and the parameter are snake_case, as Python's convention asks. |
| Does not duplicate an existing interface | Pass | The project has no source code and no other design yet. |
| Depends only on features earlier in the order | Pass | F01 has no hard or soft dependency and is first in the order. |
| Adds no hidden coupling between modules | Pass | The function lives in one module, uses the standard library only, and keeps no shared or global state. |
| Changes an implemented interface only through the change flow | Pass | Section 3 changes nothing, and no interface is implemented yet. |

| Round | Issue | Resolution |
| --- | --- | --- |
| 1 | No blocking finding. One note for the Developer, which does not block: `open()` accepts `bytes` paths and integer file descriptors, so the `TypeError` that the design gives for any other type of `path` needs an explicit type check. | Approved in round 1. |

## 5. Change log

| Version | Date | Change |
| --- | --- | --- |
| 0.1 | 2026-11-07 | First draft. |
