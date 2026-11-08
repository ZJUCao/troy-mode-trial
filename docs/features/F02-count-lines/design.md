---
troy-doc: "F02-design"
lang: "en"
version: "1.0"
updated: "2026-11-08"
status: "Approved by Troy on 2026-11-08"
mirror: "design.zh-CN.md"
---

# F02 Count lines: interface design

## 1. Feature

- ID and name: F02 Count lines
- Requirement: [docs/requirements.md](../../requirements.md#4-features)
- Hard dependencies: None
- Soft dependencies: None

## 2. Interfaces

### 2.1 `count_lines`

- Module: counting. Callers import it from the package `troy_mode_trial`, which `src/troy_mode_trial/__init__.py` defines, next to `count_words`.
- Purpose: Reads one UTF-8 text file and returns the number of lines in it. Only `\n`, `\r\n`, and `\r` end a line (Q2), and a last line without a line break still counts.

Signature:

```python
def count_lines(path: str | os.PathLike[str]) -> int:
```

Parameters:

| Name | Type | Meaning | Constraints |
| --- | --- | --- | --- |
| `path` | `str \| os.PathLike[str]` | The path of the file to count, absolute or relative to the current working directory. A `pathlib.Path` is an `os.PathLike[str]` and is accepted. | Names one existing, readable, regular file whose content is valid UTF-8. `bytes` paths are not accepted. |

- Return value: `int`, the number of lines in the file, 0 or more. The function decodes the file as UTF-8 and ignores one byte order mark (U+FEFF) at the start of the file (Q5). It then counts the line breaks in the text and adds 1 if any text follows the last line break, or if the text has no line break but is not empty.

  The rules for line breaks:

  - Exactly three sequences are line breaks: `\n`, `\r\n`, and `\r` (Q2). A `\r` directly followed by `\n` is one line break, `\r\n`, not two. So the same text with Windows or Linux line breaks gives the same count.
  - No other character ends a line. The other characters that Python's `str.splitlines()` treats as line breaks are ordinary characters for F02: `\v` (U+000B), `\f` (U+000C), U+001C, U+001D, U+001E, U+0085, U+2028, and U+2029. A line that holds them counts once, like any other line. The function must therefore not count with `str.splitlines()`.
  - A file that is empty, or holds only the byte order mark, returns 0 (Q3). A file that holds only one line break returns 1 (Q3). An empty line between two line breaks counts as a line.

  | Text after decoding (byte order mark removed) | Result |
  | --- | --- |
  | (empty) | `0` |
  | `\n` | `1` |
  | `Hello world\n  troy-mode  trial` | `2` |
  | `Hello world\r\n  troy-mode  trial\r\n` | `2` |
  | `first\n\nthird\n` | `3` |
  | `one\rtwo\r\nthree\nfour` | `4` |
  | `\r\r\n` | `2` |
  | `\n\r` | `2` |
  | `a b\fc\x85d` | `1` |

Errors:

The function defines no exception of its own (Q4). It lets Python's own exception reach the caller, the same as `count_words`.

| Error | When |
| --- | --- |
| `FileNotFoundError` | No file exists at `path`, or `path` is the empty string. |
| `IsADirectoryError` or `PermissionError` | `path` names a folder. Linux raises `IsADirectoryError`. Windows raises `PermissionError`. |
| `PermissionError` | The process may not read the file. |
| `UnicodeDecodeError` | The file content is not valid UTF-8. |
| `TypeError` | `path` is neither a `str` nor an `os.PathLike[str]`, for example `bytes` or an `int`. |

- Side effects: The function opens the file for reading and closes it before it returns or raises. It writes, sends, and stores nothing.
- Performance target: None

Example:

`notes.txt` is UTF-8 and holds the two lines `Hello world` and `  troy-mode  trial`, the second without a line break at the end. `windows.txt` holds the same text with `\r\n` line breaks. `empty.txt` is empty.

```python
>>> from pathlib import Path
>>> from troy_mode_trial import count_lines
>>> count_lines("notes.txt")
2
>>> count_lines(Path("windows.txt"))
2
>>> count_lines("empty.txt")
0
>>> count_lines("missing.txt")
Traceback (most recent call last):
  ...
FileNotFoundError: [Errno 2] No such file or directory: 'missing.txt'
```

## 3. Changes to existing interfaces

None. F02 adds `count_lines` and leaves `count_words` as it is.

## 4. Architect review

| Item | Result | Note |
| --- | --- | --- |
| Fits the module layout and the data model | Pass | `count_lines` belongs to the module counting, which owns `src/troy_mode_trial/**`, and callers reach it through the module's external interface `src/troy_mode_trial/__init__.py`, as R07 asks. Requirements Q6 settles that counting lines fits counting with no architecture change. The architecture defines no data model; the function takes a path and returns an `int`, like `count_words`. |
| Follows the error handling and naming conventions | Pass | Raises only Python's own exceptions and defines none of its own (Q4). The error table matches the one `count_words` implements, including `TypeError` for `bytes` paths and the empty string as `FileNotFoundError`. The name follows `count_words`: snake_case, verb `count_` plus the thing counted. |
| Does not duplicate an existing interface | Pass | The only existing interface is `count_words`, which counts words, not lines. No existing function counts line breaks. |
| Depends only on features earlier in the order | Pass | F02 has no hard or soft dependency and is last in the order F01, F03, F02. It uses no F01 or F03 interface. |
| Adds no hidden coupling between modules | Pass | The project has one module, and the design adds no module, no shared state, and no new import across modules. It uses the standard library only (requirements 7). |
| Changes an implemented interface only through the change flow | Pass | Section 3 changes no implemented interface: `count_words` keeps its signature and behavior. Exporting `count_lines` from `__init__.py` next to `count_words` adds a name and changes no existing one. |

| Round | Issue | Resolution |
| --- | --- | --- |
| 1 | None. All six items pass. | Approved. No change needed. |

## 5. Change log

| Version | Date | Change |
| --- | --- | --- |
| 0.1 | 2026-11-08 | First draft. |
| 1.0 | 2026-11-08 | Approved by Troy. |
