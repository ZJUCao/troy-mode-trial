---
troy-doc: "changelog"
lang: "zh-CN"
version: "0.1"
updated: "2026-11-08"
status: "已更新到 v0.1.0。"
mirror-of: "CHANGELOG.md"
---

# 更新日志

## v0.1.0 (2026-11-08)

### 新增

- F01：Troy 的脚本可以用一个 UTF-8 文本文件的路径调用 `count_words`，得到它的词数，类型为 `int`。文件不存在时抛出 `FileNotFoundError`，文件不是合法 UTF-8 时抛出 `UnicodeDecodeError`。

### 修改

- F03：一个词现在必须至少含一个字母或数字。只由其他字符组成的串，例如 `--` 或 `...`，不再算作词；`don't`、`x--y` 和 `3.14` 仍各算一个词。

### 修复

- B13：`count_words("")` 抛出 `IsADirectoryError` 或 `PermissionError`，而不是 `FileNotFoundError`（[#13](https://github.com/ZJUCao/troy-mode-trial/issues/13)）。
