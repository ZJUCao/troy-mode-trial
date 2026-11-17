---
troy-doc: "F02-test-plan"
lang: "zh-CN"
version: "1.0"
updated: "2026-11-17"
status: "Troy 已于 2026-11-17 批准"
mirror-of: "test-plan.md"
---

# F02 统计行数：测试方案

## 1. 功能

- 编号和名称：F02 统计行数：统计一个 UTF-8 文本文件里的行数。末尾没有换行符的最后一行也算一行。
- 设计：[design.zh-CN.md](design.zh-CN.md)

## 2. 用例

每个用例都像调用方一样调用函数：`from troy_mode_trial import count_lines`。每个测试在 pytest 的 `tmp_path` 里自建文件，并以二进制方式写入用例给出的确切字节，这样 Windows 不会把 `\n` 改成 `\r\n`。输入中的 `\xXX` 和 `\uXXXX` 表示一个 Unicode 字符，测试把它编码为 UTF-8；`EF BB BF` 表示字节顺序标记的字节。测试套件在 Windows 11 和 Linux 上运行，除非用例另有说明，每个用例在两个平台上预期相同的结果。

| 编号 | 层级 | 接口 | 测什么 | 准备和输入 | 预期结果 |
| --- | --- | --- | --- | --- | --- |
| F02-T01 | 功能 | `count_lines` | 设计中的示例：两行，第二行末尾没有换行符。 | `notes.txt` 内容为 `Hello world\n  troy-mode  trial`。以 `str` 形式传入其路径调用 `count_lines`。 | 返回 `2`，且结果的类型恰好是 `int`。 |
| F02-T02 | 单元 | `count_lines` | `\r\n` 结束一行而不是两行，所以 Windows 换行符得到与 F02-T01 相同的计数。 | 两个文件：`windows.txt` 内容为 `Hello world\r\n  troy-mode  trial`，第二个文件内容为 `Hello world\r\n  troy-mode  trial\r\n`。分别以 `pathlib.Path` 传入路径调用。 | 每个都返回 `2`。 |
| F02-T03 | 单元 | `count_lines` | 空文件和只含字节顺序标记的文件没有行（Q3、Q5）。 | 两个文件：一个空文件，一个只有字节 `EF BB BF` 的文件。 | 每个都返回 `0`。 |
| F02-T04 | 单元 | `count_lines` | 只含一个换行符的文件有一行（Q3），三种换行符都如此。 | 三个文件：`\n`、`\r\n` 和 `\r`。 | 每个都返回 `1`。 |
| F02-T05 | 单元 | `count_lines` | 末尾没有换行符的最后一行算一行，末尾的换行符不会开始新的一行。 | 四个文件：`a`、`a\n`、`a\nb` 和 `a\nb\n`。 | 依次返回 `1`、`1`、`2` 和 `2`。 |
| F02-T06 | 单元 | `count_lines` | 两个换行符之间的空行算一行。 | 三个文件：`first\n\nthird\n`、`\n\n\n` 和 `\r\n\r\n`。 | 依次返回 `3`、`3` 和 `2`。 |
| F02-T07 | 单元 | `count_lines` | 同一文件中的三种换行符各结束一行（Q2）。 | `one\rtwo\r\nthree\nfour` | 返回 `4`。 |
| F02-T08 | 单元 | `count_lines` | 只有紧跟 `\n` 的 `\r` 才合成一个换行符。`\r` 和 `\n` 的其他排列每个换行符各算一行。 | 五个文件：`\r\r\n`、`\n\r`、`\r\r`、`\r\n\n` 和 `a\r\rb`。 | 依次返回 `2`、`2`、`2`、`2` 和 `3`。 |
| F02-T09 | 单元 | `count_lines` | `str.splitlines()` 视为换行符的其他字符，对 F02 来说是普通字符。 | 设计中的文件 `a b\fc\x85d`。然后为 `\v`、`\f`、`\x1c`、`\x1d`、`\x1e`、`\x85`、` ` 和 ` ` 各建一个文件，内容为 `a`、该字符和 `b`。最后一个文件为 `a b\nc `。 | 设计中的文件和这八个文件都返回 `1`，最后一个文件返回 `2`。 |
| F02-T10 | 单元 | `count_lines` | 同一段文字无论用哪种换行符，计数都相同。 | 三个文件，文字相同：`alpha\nbeta\n\ngamma`、`alpha\r\nbeta\r\n\r\ngamma` 和 `alpha\rbeta\r\rgamma`。 | 每个都返回 `4`。 |
| F02-T11 | 单元 | `count_lines` | 忽略文件开头的一个字节顺序标记（Q5），出现在其他位置的 U+FEFF 是普通文字。 | 五个文件：`EF BB BF` 后接 `one\ntwo`；`EF BB BF` 后接 `\n`；`EF BB BF` 后接 `x`；`EF BB BF EF BB BF`，两个标记；以及 `a\n﻿`。 | 依次返回 `2`、`1`、`1`、`1` 和 `2`。 |
| F02-T12 | 单元 | `count_lines` | 在大文件中计数仍然正确，此时 `\r\n` 可能被任何内部读取边界分开。 | 一个文件：100,000 个 `abcde\r\n`（每个 7 字节，所以对任何不超过 64 KiB 的 2 的幂读取大小，都有某个边界落在 `\r` 和它的 `\n` 之间），其后接 100,000 个 `x\r`，再接 100,000 个 `y\n`，最后是由 100,000 个 `z` 组成、没有换行符的一行。文件共 1,200,000 字节，大于 1 MiB。 | 返回 `300001`。 |
| F02-T13 | 功能 | `count_lines` | `path` 的每种合法形式得到相同的计数。 | 一个内容为 `a\nb\nc` 的文件。分别以 `str` 形式的绝对路径、`pathlib.Path`，以及一个实现了 `__fspath__` 并返回 `str` 的测试类对象调用。 | 每个都返回 `3`。 |
| F02-T14 | 功能 | `count_lines` | 相对路径按当前工作目录解析。 | 在 `tmp_path` 中建文件 `lines.txt`，内容为 `alpha\nbeta`。用 `monkeypatch.chdir` 把 `tmp_path` 设为工作目录，再分别以 `"lines.txt"` 和 `pathlib.Path("lines.txt")` 调用。 | 每个都返回 `2`。 |
| F02-T15 | 功能 | `count_lines` | 文件不存在，或 `path` 为空字符串时，抛出 Python 自带的异常（Q4）。 | `tmp_path` 中一个不存在任何东西的路径，分别以 `str` 和 `pathlib.Path` 传入。然后传入空字符串 `""`。 | 每个都抛出 `FileNotFoundError`。 |
| F02-T16 | 功能 | `count_lines` | 路径指向文件夹时抛出 Python 自带的异常。 | `tmp_path` 本身，分别以 `str` 和 `pathlib.Path` 传入。 | 每个都抛出 `IsADirectoryError` 或 `PermissionError`。在 Linux 上抛出 `IsADirectoryError`。 |
| F02-T17 | 功能 | `count_lines` | 进程无权读取的文件抛出 `PermissionError`。 | 仅限 Linux：一个内容为 `one\ntwo` 的文件，权限设为 `0o000`。在 Windows 上跳过，因为测试无法可移植地去掉自己的读权限；以 root 运行时也跳过，因为 root 仍能读取该文件。测试结束后恢复权限。 | 抛出 `PermissionError`。 |
| F02-T18 | 功能 | `count_lines` | 内容不是合法 UTF-8 时抛出 Python 自带的异常（Q4）。 | 三个文件：Latin-1 编码的 `café au lait\n`（字节以 `63 61 66 E9 20` 开头）；`ok\nfine\n` 后接被截断的序列 `E6 97`；带字节顺序标记的 UTF-16 编码的 `hello\n`。 | 每个都抛出 `UnicodeDecodeError`。 |
| F02-T19 | 功能 | `count_lines` | 其他类型的 `path` 抛出 `TypeError`。 | 分别以 `b"lines.txt"`（`bytes`）、一个已打开文件（内容为 `one\ntwo`）的整数文件描述符、`None`、`3.5`，以及一个 `__fspath__` 返回 `bytes` 的对象调用。测试结束后关闭该描述符。 | 每个都抛出 `TypeError`。 |
| F02-T20 | 功能 | `count_lines` | 函数在返回和抛出异常之前关闭文件。 | 用 `warnings.catch_warnings(record=True)` 和 `simplefilter("always", ResourceWarning)` 记录警告。对内容为 `one\ntwo` 的文件调用一次 `count_lines`，再对一个会抛出 `UnicodeDecodeError` 的文件调用一次。然后运行 `gc.collect()`，并把每个文件改名为 `tmp_path` 中的新名字。 | 没有记录到 `ResourceWarning`，两次改名都成功。在 Windows 上，改名能发现仍打开的文件，因为 Windows 无法给打开的文件改名。 |
| F02-T21 | 功能 | `count_lines` | 函数不写入也不保存任何东西。 | 一个内容为 `one\ntwo\r\n` 的文件。记录它的字节、以纳秒计的修改时间，以及 `tmp_path` 中的条目列表。调用 `count_lines` 两次。 | 两次都返回 `2`。文件的字节和修改时间不变，`tmp_path` 中的条目与之前相同。 |
| F02-T22 | 集成 | `count_lines`、`count_words` | 包在 `count_words` 旁边导出 `count_lines`，两者按各自的设计统计同一个文件。 | `from troy_mode_trial import count_lines, count_words`。一个文件，内容为 `EF BB BF` 后接 `Hello world\r\n  troy-mode  trial\r\n`。对其路径先调用 `count_lines`，再调用 `count_words`。 | `count_lines` 返回 `2`，`count_words` 返回 `4`。`"count_lines"` 和 `"count_words"` 都在 `troy_mode_trial.__all__` 中。 |

## 3. 性能用例

无。设计没有给 `count_lines` 设性能指标，需求 7.1 也没有给项目设任何性能指标（R14）。

## 4. 不测的内容

| 内容 | 原因 |
| --- | --- |
| 异常消息的文字，例如设计示例中的 `[Errno 2] No such file or directory: 'missing.txt'`。 | 消息由 Python 生成，设计只承诺异常类型（Q4）。F02-T15 到 F02-T19 检查类型。 |
| Windows 上不可读文件的 `PermissionError`。 | 在 Windows 上去掉文件的读权限需要访问控制列表，可移植的测试无法可靠地设置和恢复。F02-T17 在 Linux 上检查同一行为。 |
| Windows 对文件夹抛出 `IsADirectoryError` 还是 `PermissionError`。 | 设计允许 Windows 抛出其中任一个。F02-T16 在 Windows 上接受任一个，在 Linux 上要求 `IsADirectoryError`。 |
| 性能。 | 没有性能指标（R14）。 |

## 5. 与接口设计师的对齐记录

无。设计已回答本方案提出的所有问题。

## 6. 修改记录

| 版本 | 日期 | 修改 |
| --- | --- | --- |
| 0.1 | 2026-11-16 | 初稿。 |
| 1.0 | 2026-11-17 | Troy 批准。 |
