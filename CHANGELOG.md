---
troy-doc: "changelog"
lang: "en"
version: "0.1"
updated: "2026-11-08"
status: "Up to date with v0.1.0."
mirror: "CHANGELOG.zh-CN.md"
---

# Changelog

## v0.1.0 (2026-11-08)

### Added

- F01: Troy's scripts can call `count_words` with the path of a UTF-8 text file and get its number of words as an `int`. A missing file raises `FileNotFoundError`, and a file that is not valid UTF-8 raises `UnicodeDecodeError`.

### Changed

- F03: a word must now hold at least one letter or digit. A run of other characters only, such as `--` or `...`, no longer counts as a word; `don't`, `x--y`, and `3.14` still count as one word each.

### Fixed

- B13: `count_words("")` raised `IsADirectoryError` or `PermissionError` instead of `FileNotFoundError` ([#13](https://github.com/ZJUCao/troy-mode-trial/issues/13)).
