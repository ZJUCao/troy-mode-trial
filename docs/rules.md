---
troy-doc: "rules"
lang: "en"
version: "3.0"
updated: "2026-11-08"
status: "Approved by Troy on 2026-11-08"
mirror: "rules.zh-CN.md"
---

# troy-mode-trial rules

## 1. Rule types

- **Hard** blocks the merge.
- **Soft** allows the PR when its description gives a reason.
- **Review** is checked by a role.
- **Process** is followed by troy-mode itself.

## 2. Rules

| ID | Rule | Type | Enforced by | Scope | Since |
| --- | --- | --- | --- | --- | --- |
| R01 | Each PR has exactly one commit, and its subject line equals the PR title. Review fixes amend that commit, or the PR is squash-merged. | Hard | CI | troy-mode | 2026-11-07 |
| R02 | Each PR holds one stage's output only: documents, source, or tests. | Hard | CI | troy-mode | 2026-11-07 |
| R03 | A source PR changes at most 500 lines (added plus deleted, not counting lock files or generated files) in at most 5 files. Test PRs have no limit. A PR that only splits a file may pass the limit and says so. | Soft | CI | troy-mode | 2026-11-07 |
| R04 | A function body has at most 50 lines, not counting comments, doc comments, or blank lines. A complex external interface calls single-purpose internal functions. | Hard | Lint | troy-mode | 2026-11-07 |
| R05 | Doc comments follow Google style. Code comments are in English only. | Hard | Lint | troy-mode | 2026-11-07 |
| R06 | A source file has at most 500 lines in total, comments included. Larger files are split. | Soft | Lint | troy-mode | 2026-11-07 |
| R07 | Modules depend on each other only in the directions the architecture allows, only through external interfaces, and never in a cycle. | Hard | Dependency checker | troy-mode | 2026-11-07 |
| R08 | The Developer never edits test files. | Hard | Hook and CI | troy-mode | 2026-11-07 |
| R09 | Every new test in a test PR fails against the mock. | Hard | CI | troy-mode | 2026-11-07 |
| R10 | Every test is tagged with its case ID or bug ID: the test's own name starts with it, for example `test_f04_t07_writes_header`. Tests of features not yet accepted and of bugs not yet fixed count as expected failures. Every other test must pass. | Hard | Test runner config and CI | troy-mode | 2026-11-07 |
| R11 | In an implementation PR, the changed code has at least 90% line coverage and 80% branch coverage. 95% is a target, not a gate. An excluded line needs a written reason and the Test Manager's approval. | Hard | CI | troy-mode | 2026-11-07 |
| R12 | English documents are the source of truth. A PR that changes an English document also updates its Chinese mirror. The mirror's header names the English version it matches. | Hard | CI | troy-mode | 2026-11-07 |
| R13 | A status label says how far a feature really goes, for example "passes tests on main" versus "usable on Troy's devices". | Review | Product Manager | troy-mode | 2026-11-07 |
| R14 | Only interfaces with a performance target get performance tests. They run on a fixed machine, with a margin, against the previous baseline. | Review | Test Manager | troy-mode | 2026-11-07 |
| R15 | Every fixed bug keeps its reproduction test. | Review | Test Manager | troy-mode | 2026-11-07 |
| R16 | A new third-party dependency needs the Architect's approval. | Review | Architect. CI flags every change to dependency files. | troy-mode | 2026-11-07 |
| R17 | A review loop stops at 3 rounds and escalates. | Process | troy-mode | troy-mode | 2026-11-07 |
| R18 | Troy merges PR 1 and PR 2 of the first 3 features. Claude merges every other PR once its checks and reviews pass. Troy decides when Claude merges everything. | Process | troy-mode | troy-mode | 2026-11-07 |
| R19 | Commits use the email in Troy's global CLAUDE.md. Commit messages, PR titles, and PR descriptions carry no Claude attribution and do not mention Claude or Anthropic at all, unless `.troy-mode/config.toml` sets the attribution mode to `trailers`. | Hard | Hook and CI | troy-mode | 2026-11-07 |
| R20 | A merged document or PR description holds no template markers or template guidance. | Hard | CI | troy-mode | 2026-11-07 |
| R21 | Every change reaches `main` through a PR from its own branch. Never commit on `main`, push `main`, or open a PR from `main`. | Hard | Hook and CI | troy-mode | 2026-11-07 |
| P01 | An exception message is never an f-string written inside the raise. Build the message in a variable first, for example msg = f"...", then raise ValueError(msg). | Hard | Lint (ruff EM102) | project | 2026-11-08 |
| P02 | Every error message says which file it is about. This includes Python's own exceptions that the library lets through: if Python's message does not name the file, catch the exception and raise the same type again with the file's path in its message. An error that is about no file, such as a path argument of the wrong type, is exempt. | Review | Code Reviewer. The Architect checks the error tables in design reviews. | project | 2026-11-08 |

## 3. Change log

| Version | Date | Change |
| --- | --- | --- |
| 1.0 | 2026-11-07 | Seeded with R01 to R21 from troy-mode. |
| 2.0 | 2026-11-08 | Added P01, no f-string inside an exception message, approved by Troy. Existing code: fixed by cleanup PRs. |
| 3.0 | 2026-11-08 | Added P02, every error message names its file, approved by Troy. Existing code: fixed when touched. |
