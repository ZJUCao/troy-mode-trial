---
troy-doc: "changelog"
lang: "zh-CN"
version: "0.2"
updated: "2026-11-17"
status: "已更新到 v0.2.0。"
mirror-of: "CHANGELOG.md"
---

# 更新日志

## v0.2.0 (2026-11-17)

### 新增

- F04：Troy 可以在 PowerShell 里输入 `wordcount FILE`，打印一个 UTF-8 文本文件的词数，按 F03 的方式计数。文件出错时，例如文件不存在或不是合法 UTF-8，在标准错误上打印一行 `wordcount: <FILE>: <reason>`，退出码为 2；命令行写错时打印用法行，退出码也是 2。
- F02：Troy 的脚本可以用一个 UTF-8 文本文件的路径调用 `count_lines`，得到它的行数，类型为 `int`。`\n`、`\r\n` 和 `\r` 各结束一行，最后一行没有换行也算一行，所以同一个文件的 Windows 版和 Linux 版行数相同。

### 修改

无

### 修复

无

## v0.1.0 (2026-11-08)

### 新增

- F01：Troy 的脚本可以用一个 UTF-8 文本文件的路径调用 `count_words`，得到它的词数，类型为 `int`。文件不存在时抛出 `FileNotFoundError`，文件不是合法 UTF-8 时抛出 `UnicodeDecodeError`。

### 修改

- F03：一个词现在必须至少含一个字母或数字。只由其他字符组成的串，例如 `--` 或 `...`，不再算作词；`don't`、`x--y` 和 `3.14` 仍各算一个词。

### 修复

- B13：`count_words("")` 抛出 `IsADirectoryError` 或 `PermissionError`，而不是 `FileNotFoundError`（[#13](https://github.com/ZJUCao/troy-mode-trial/issues/13)）。
