---
troy-doc: "v0.2-test-plan"
lang: "zh-CN"
version: "0.1"
updated: "2026-11-08"
status: "草稿。"
mirror-of: "test-plan.md"
---

# v0.2 版本测试方案

## 1. 版本

- 版本：v0.2
- 功能：F02
- 需求：[docs/requirements.zh-CN.md](../../requirements.zh-CN.md#6-版本计划)

## 2. 端到端场景

每个场景都遵循需求文档第 3 节的用户流程、F02 原型以及决定 Q2 到 Q5。场景以原型中的名字 `count_lines` 调用函数。如果 F02 的设计定下了别的名字，或者不接受 `pathlib.Path`，测试经理会在 v0.2 测试 PR 之前更新本方案。

Troy 的脚本以相对于当前工作目录的路径调用 `count_lines`，所以场景也这样调用，除非场景另有说明。每个测试在临时文件夹里自建文件，并以二进制方式写入场景给出的确切字节，这样 Windows 不会把 `\n` 改成 `\r\n`。非 ASCII 字符按 UTF-8 编码，除非场景给出了别的字节。需求只承诺异常的类型，不承诺异常的消息（Q4），所以预期异常的场景只检查类型。

Q2 只把 `\n`、`\r\n` 和 `\r` 定为换行符。所以没有场景使用 Python 的 `str.splitlines()` 视为换行符的其他字符，比如 U+2028 或换页符。这些字符由 F02 的设计和测试方案决定。

| 编号 | 场景 | 由谁运行 | 步骤 | 预期结果 |
| --- | --- | --- | --- | --- |
| v0.2-S01 | 统计一个最后一行没有换行符的文件的行数，与 F02 原型相同。 | Claude | 1. 写入 `notes.txt`，内容为 `Hello world\n  troy-mode  trial`，末尾没有换行符。2. 把 `notes.txt` 所在文件夹设为工作目录。3. 执行 `from troy_mode_trial import count_lines`。4. 调用 `count_lines("notes.txt")`。 | 返回 `2`，且结果的类型恰好是 `int`。 |
| v0.2-S02 | 统计一个使用 Windows 换行符的文件的行数，与 F02 原型相同。 | Claude | 1. 写入 `windows.txt`，内容为 `Hello world\r\n  troy-mode  trial`，末尾没有换行符。2. 把它所在文件夹设为工作目录。3. 调用 `count_lines("windows.txt")`。 | 返回 `2`。每个 `\r\n` 结束一行，而不是两行。 |
| v0.2-S03 | 统计一个空文件的行数，与 F02 原型相同。 | Claude | 1. 写入一个空的 `empty.txt`。2. 把它所在文件夹设为工作目录。3. 调用 `count_lines("empty.txt")`。 | 返回 `0`。 |
| v0.2-S04 | 统计一个不存在的文件，与 F02 原型相同。 | Claude | 1. 把一个空文件夹设为工作目录。2. 调用 `count_lines("missing.txt")`。 | 抛出 `FileNotFoundError`。 |
| v0.2-S05 | 统计一个不是合法 UTF-8 的文件。 | Claude | 1. 写入 `latin1.txt`，内容为 Latin-1 编码的 `café au lait\n`，所以其字节以 `63 61 66 E9 20` 开头。2. 把它所在文件夹设为工作目录。3. 调用 `count_lines("latin1.txt")`。 | 抛出 `UnicodeDecodeError`。 |
| v0.2-S06 | 统计一个只含一个换行符的文件。 | Claude | 1. 写入 `one-break.txt`，内容只有 `\n`。2. 把它所在文件夹设为工作目录。3. 调用 `count_lines("one-break.txt")`。 | 返回 `1`。 |
| v0.2-S07 | 统计一个含空行、末尾有换行符的文件。 | Claude | 1. 写入 `blank-lines.txt`，内容为 `first\n\nthird\n`。2. 把它所在文件夹设为工作目录。3. 调用 `count_lines("blank-lines.txt")`。 | 返回 `3`。空的第二行计入，末尾的 `\n` 不会开始第四行。 |
| v0.2-S08 | 统计一个混用全部三种换行符的文件。 | Claude | 1. 写入 `mixed-breaks.txt`，内容为 `one\rtwo\r\nthree\nfour`，末尾没有换行符。2. 把它所在文件夹设为工作目录。3. 调用 `count_lines("mixed-breaks.txt")`。 | 返回 `4`。 |
| v0.2-S09 | Troy 的一个脚本在 Troy 的电脑上、在自己的 Python 进程中统计在 Windows 和 Linux 上生成的文件的行数和词数，相同的文本无论换行符如何都得到相同的计数。 | Claude | 1. 写入三个文件。`windows.txt` 内容为字节 `EF BB BF` 后接 `Hello world\r\n  troy-mode  trial\r\n`，与记事本保存的一样。`linux.txt` 内容为 `Hello world\n  troy-mode  trial\n`。`mixed.txt` 内容为 `Wait -- what ... don't x--y 3.14 _\r\n日本語　テキスト 😀\n`，其中 `日本語` 和 `テキスト` 之间的空白是 U+3000。2. 记录每个文件的字节。3. 从文件所在文件夹以外的文件夹启动一个新的 Python 3.13 进程。4. 在该进程中导入 `troy_mode_trial`。5. 按第 1 步的顺序，对每个文件以 `pathlib.Path` 形式的绝对路径先调用 `troy_mode_trial.count_lines`，再调用 `troy_mode_trial.count_words`，并把两个计数打印在同一行，以一个空格分隔。所有步骤都在 Troy 的电脑上的 Windows 11 中执行。 | 进程以退出码 0 结束，并打印 `2 4`、`2 4` 和 `2 7` 这三行。每个文件的字节与第 2 步记录的相同。 |

虽然需求第 7 节承诺在 Windows 11 和 Linux 上得到相同的计数，但没有场景在 Linux 上运行。Claude 运行的场景只在 Troy 电脑上的发布测试中运行，那台电脑运行 Windows 11，而记录中没有 Troy 的 Linux 设备。v0.2-S02、v0.2-S08 和 v0.2-S09 改为在 Windows 上统计使用 Linux 换行符的文件。F02 的功能测试在 CI 中于 Linux 上运行。

## 3. 性能和压力用例

无。需求第 7.1 节没有设任何性能指标，所以 v0.2 没有性能或压力用例（R14）。

## 4. 设备

| 设备 | 操作系统 | 由谁运行 |
| --- | --- | --- |
| Troy 的电脑 | Windows 11，conda 环境 `troy-mode-trial` 中的 Python 3.13 | Claude |

Claude 运行的场景只在 Troy 电脑上的发布测试中运行，从不在 CI 中运行，所以 GitHub Actions 运行器不是这些场景的设备。v0.2 是一个没有用户界面的库，每个场景都从脚本调用 `count_lines` 或 `count_words`。所以没有场景需要只有 Troy 才有的设备。

## 5. 验收记录

无。Troy 尚未验收 v0.2。

## 6. 修改记录

| 版本 | 日期 | 修改 |
| --- | --- | --- |
| 0.1 | 2026-11-08 | 初稿。 |
