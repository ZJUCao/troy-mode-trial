---
troy-doc: "ADR-0002"
lang: "en"
version: "1.0"
updated: "2026-11-14"
status: "Approved by Troy on 2026-11-14"
mirror: "ADR-0002-file-error-exit-code-2.zh-CN.md"
---

# ADR-0002: A file error in `wordcount` exits with code 2

## 1. Status

Accepted

## 2. Context

ADR-0001, point 4 of its decision, and architecture 2.0, section 6, say that cli returns exit code 1 for a file error: a missing file, a file it may not read, or a file that is not valid UTF-8. The F04 prototype shows `$LASTEXITCODE` 1 for a missing file. A wrong command line exits with code 2, as `argparse` does, and an uncaught exception exits with code 1 through Python's traceback.

On PR #39, the F04 interface design, Troy commented: "when the file is missing or cannot be read, `wordcount` exits with code 2, not 1. My scripts treat 2 as an error. Keep the message as it is." Troy then approved this architecture change.

The forces:

- Troy's scripts must see every file error as an error.
- The error line `wordcount: <FILE as typed>: <reason>` on standard error stays as it is.
- The requirements ask only that a missing file gives an exit code that is not 0, so either code meets them.
- `argparse` always exits with code 2 for a wrong command line, and Python always exits with code 1 for an uncaught exception. Neither can change without extra code.

## 3. Decision

1. For every file error that cli catches, `OSError` and its subclasses and `UnicodeDecodeError`, cli writes the same one line `wordcount: <FILE as typed>: <reason>` to standard error and returns exit code 2. This replaces "returns 1" in point 4 of ADR-0001. The rest of ADR-0001 stands.
2. A file error and a wrong command line share code 2. Only the text on standard error tells them apart: the line `wordcount: <FILE as typed>: <reason>` for a file error, and a usage line for a wrong command line.
3. cli still does not catch any other exception. Python writes the traceback to standard error and exits with code 1, so code 1 means only a bug.
4. The exit codes of `wordcount` are 0 for success, 2 for a file error or a wrong command line, and 1 for a bug.

## 4. Options considered

| Option | Pros | Cons |
| --- | --- | --- |
| Code 2 for every file error, with the message unchanged (chosen) | Troy's scripts see every file error as an error. Code 1 is left to bugs, so a script can tell a bug from bad input. No new code: `argparse` already uses 2. | A file error and a wrong command line share a code, so a script must read standard error to tell them apart. The F04 prototype and the v0.2 test plan show code 1 and are out of date. |
| Keep code 1 for a file error (ADR-0001 as written) | Matches the prototype and the v0.2 test plan. A file error and a wrong command line have different codes. | Against Troy's decision. Troy's scripts do not treat 1 as an error. A file error and a bug share code 1. |
| A code of its own for a file error, such as 3, or one code for each reason | Every kind of failure has its own code. | Troy's scripts treat 2 as an error, not 3. More codes to document and test, for a difference that the error line already shows. |

## 5. Consequences

- A script that runs `wordcount` sees 0 for a count, 2 for a file error or a wrong command line, and 1 only for a bug in the program.
- To tell a file error from a wrong command line, a script reads standard error. The line `wordcount: <FILE as typed>: <reason>` means a file error, and a line that starts with `usage:` means a wrong command line.
- The error line, the reason texts, and standard output do not change. The requirements do not change.
- F04's interface design states code 2 for file errors from its version 0.2 on. F04's test plan, not yet written, expects code 2.
- The v0.2 test plan expects code 1 in the scenarios for a missing file, for a file that is not valid UTF-8, and for the PowerShell session. They must change to 2 in a `[docs]` PR before the v0.2 tests are written. The F04 prototype still shows `$LASTEXITCODE` 1; F04's design records the difference.
- Once Troy's scripts rely on code 2, changing it again would break them.

## 6. Related

- Features: F04
- Rules: None
- Decision records: ADR-0001, point 4 of its decision
- Architecture: version 2.1, the error handling and the decision records
