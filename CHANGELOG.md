---
troy-doc: "changelog"
lang: "en"
version: "0.2"
updated: "2026-11-17"
status: "Up to date with v0.2.0."
mirror: "CHANGELOG.zh-CN.md"
---

# Changelog

## v0.2.0 (2026-11-17)

### Added

- F04: Troy can type `wordcount FILE` in PowerShell to print the number of words in one UTF-8 text file, counted as F03 counts them. A file error, such as a missing file or a file that is not valid UTF-8, prints one line `wordcount: <FILE>: <reason>` on standard error and exits with code 2; a wrong command line prints the usage line and also exits with code 2.
- F02: Troy's scripts can call `count_lines` with the path of a UTF-8 text file and get its number of lines as an `int`. `\n`, `\r\n`, and `\r` each end one line, and a last line without a line break still counts, so a file from Windows and the same file from Linux give the same count.

### Changed

None

### Fixed

None

## v0.1.0 (2026-11-08)

### Added

- F01: Troy's scripts can call `count_words` with the path of a UTF-8 text file and get its number of words as an `int`. A missing file raises `FileNotFoundError`, and a file that is not valid UTF-8 raises `UnicodeDecodeError`.

### Changed

- F03: a word must now hold at least one letter or digit. A run of other characters only, such as `--` or `...`, no longer counts as a word; `don't`, `x--y`, and `3.14` still count as one word each.

### Fixed

- B13: `count_words("")` raised `IsADirectoryError` or `PermissionError` instead of `FileNotFoundError` ([#13](https://github.com/ZJUCao/troy-mode-trial/issues/13)).
