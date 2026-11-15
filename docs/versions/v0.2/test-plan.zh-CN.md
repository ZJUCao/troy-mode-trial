---
troy-doc: "v0.2-test-plan"
lang: "zh-CN"
version: "0.2"
updated: "2026-11-14"
status: "草稿。"
mirror-of: "test-plan.md"
---

# v0.2 版本测试方案

## 1. 版本

- 版本：v0.2
- 功能：F02、F04
- 需求：[docs/requirements.zh-CN.md](../../requirements.zh-CN.md#6-版本计划)

## 2. 端到端场景

每个测试在临时文件夹里自建文件。它以二进制方式写入每个文件，内容为场景给出的确切字节，这样 Windows 不会把 `\n` 改成 `\r\n`。非 ASCII 字符按 UTF-8 编码，除非场景给出了别的字节。

### 2.1 在脚本中统计行数（F02）

v0.2-S01 到 v0.2-S09 遵循需求文档第 3 节的用户流程、F02 原型、决定 Q2 到 Q5 以及 F02 的设计。它们调用 `count_lines`，即 F02 的设计定下的名字。Troy 的脚本以相对于当前工作目录的路径调用它，所以场景也这样调用，除非场景另有说明。需求只承诺异常的类型，不承诺异常的消息（Q4），所以预期异常的场景只检查类型。

Q2 只把 `\n`、`\r\n` 和 `\r` 定为换行符。所以没有场景使用 Python 的 `str.splitlines()` 视为换行符的其他字符，比如 U+2028 或换页符。F02 的设计把它们当作普通字符，由 F02 的功能测试检查。

### 2.2 在 PowerShell 中统计词数（F04）

v0.2-S10 到 v0.2-S17 遵循需求文档第 3 节的 `wordcount FILE` 流程、F04 原型以及架构文档第 6 节的错误处理。F04 的设计尚不存在。如果它定下的错误文字不同于原型中的 `no such file`，测试经理会在 v0.2 测试 PR 之前更新本方案。

场景像 Troy 一样运行已安装的命令。发布测试在装好本项目的 conda 环境 `troy-mode-trial` 中运行，所以 `wordcount.exe` 位于该环境的脚本文件夹中，并在 `PATH` 上。如果 `PATH` 上没有 `wordcount`，测试失败，从不跳过。

- v0.2-S10 到 v0.2-S16 启动 `PATH` 上的 `wordcount`，即 PowerShell 为 `wordcount` 启动的程序，作为一个新进程，并传入场景给出的参数。每个测试捕获标准输出、标准错误和退出码。
- v0.2-S17 在 Windows PowerShell 中运行命令，即 `powershell.exe -NoProfile -NonInteractive -Command`，以检查 PowerShell 能找到该命令，并且 `$LASTEXITCODE` 保存着它的退出码。

场景比较输出时，把 `\r\n` 当作 `\n`。“一个换行符”指末尾的一个 `\n` 或一个 `\r\n`。除非场景另有说明，工作目录是文件所在的文件夹。

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
| v0.2-S10 | 用命令统计一个文件的词数，与 F04 原型相同。 | Claude | 1. 写入 `notes.txt`，内容为 `Hello world\n  troy-mode  trial`，末尾没有换行符。2. 运行 `wordcount notes.txt`。 | 标准输出恰好是 `4` 加一个换行符。标准错误为空。退出码为 0。 |
| v0.2-S11 | 用命令统计一个不存在的文件，与 F04 原型相同。 | Claude | 1. 把一个空文件夹设为工作目录。2. 运行 `wordcount missing.txt`。 | 标准输出为空。标准错误恰好是 `wordcount: missing.txt: no such file` 加一个换行符。退出码为 1。 |
| v0.2-S12 | 用命令统计一个不是合法 UTF-8 的文件。 | Claude | 1. 写入 `latin1.txt`，内容为 Latin-1 编码的 `café au lait\n`，所以其字节以 `63 61 66 E9 20` 开头。2. 运行 `wordcount latin1.txt`。 | 标准输出为空。标准错误是以 `wordcount: latin1.txt: ` 开头的一行，加一个换行符。退出码为 1。 |
| v0.2-S13 | 命令按 F03 的方式统计词数，与 F03 原型相同。 | Claude | 1. 写入 `dashes.txt`，内容为 `Wait -- what ... don't x--y 3.14 _`。2. 写入 `only-symbols.txt`，内容只有 `-- ... !!!`。3. 运行 `wordcount dashes.txt`。4. 运行 `wordcount only-symbols.txt`。 | 第 3 步打印 `5` 加一个换行符。第 4 步打印 `0` 加一个换行符。两次运行的标准错误都为空，退出码都为 0。 |
| v0.2-S14 | 用命令统计一个空文件的词数。 | Claude | 1. 写入一个空的 `empty.txt`。2. 运行 `wordcount empty.txt`。 | 标准输出恰好是 `0` 加一个换行符。标准错误为空。退出码为 0。 |
| v0.2-S15 | 从另一个文件夹以绝对路径指定在 Windows 和 Linux 上生成的文件，命令得到相同的计数。 | Claude | 1. 以 v0.2-S09 第 1 步的字节写入 `windows.txt`、`linux.txt` 和 `mixed.txt`。2. 记录每个文件的字节。3. 把文件所在文件夹以外的一个文件夹设为工作目录。4. 按第 1 步的顺序，对每个文件运行 `wordcount`，以该文件的绝对路径作为唯一参数。 | 三次运行依次打印 `4`、`4` 和 `7`，每个后接一个换行符。每次运行的标准错误都为空，退出码都为 0。每个文件的字节与第 2 步记录的相同。 |
| v0.2-S16 | 错误的命令行得到一行用法说明，而不是计数。 | Claude | 1. 按 v0.2-S10 写入 `notes.txt`。2. 不带参数运行 `wordcount`。3. 运行 `wordcount notes.txt notes.txt`。 | 每次运行的标准输出都为空，标准错误以 `usage:` 开头，退出码为 2。 |
| v0.2-S17 | Troy 在一个名字含空格的文件夹中，在 PowerShell 会话里统计词数，与 F04 原型相同。 | Claude | 1. 建一个名为 `my notes` 的文件夹，并按 v0.2-S10 在其中写入 `notes.txt`。2. 把 `my notes` 设为工作目录。3. 运行一个 Windows PowerShell 进程，即 `powershell.exe -NoProfile -NonInteractive -Command`，依次执行以下命令：`wordcount notes.txt`、`Write-Output "exit $LASTEXITCODE"`、`wordcount missing.txt`、`Write-Output "exit $LASTEXITCODE"`、`wordcount '<notes.txt 的绝对路径>'` 和 `Write-Output "exit $LASTEXITCODE"`。 | 标准输出恰好依次是 `4`、`exit 0`、`exit 1`、`4` 和 `exit 0` 这几行。标准错误含有 `missing.txt`。 |

虽然需求第 7 节承诺在 Windows 11 和 Linux 上得到相同的计数，但没有场景在 Linux 上运行。Claude 运行的场景只在 Troy 电脑上的发布测试中运行，那台电脑运行 Windows 11，而记录中没有 Troy 的 Linux 设备。v0.2-S02、v0.2-S08、v0.2-S09 和 v0.2-S15 改为在 Windows 上统计使用 Linux 换行符的文件。F02 和 F04 的功能测试在 CI 中于 Linux 上运行。

v0.2-S17 使用 Windows PowerShell 5.1，即 `powershell.exe`，因为每台 Windows 11 都有它。没有场景运行 PowerShell 7，即 `pwsh`。两者启动的是同一个 `wordcount.exe`，所以 v0.2-S10 到 v0.2-S16 对两者都成立。

## 3. 性能和压力用例

无。需求第 7.1 节没有设任何性能指标，所以 v0.2 没有性能或压力用例（R14）。

## 4. 设备

| 设备 | 操作系统 | 由谁运行 |
| --- | --- | --- |
| Troy 的电脑 | Windows 11，conda 环境 `troy-mode-trial` 中的 Python 3.13，以及 Windows PowerShell 5.1 | Claude |

Claude 运行的场景只在 Troy 电脑上的发布测试中运行，从不在 CI 中运行，所以 GitHub Actions 运行器不是这些场景的设备。每个场景都从脚本调用 `count_lines` 或 `count_words`，或者运行 `wordcount` 命令，而脚本可以在 Troy 的电脑上启动该命令并读取其输出。所以没有场景需要只有 Troy 才有的设备。

## 5. 验收记录

无。Troy 尚未验收 v0.2。

## 6. 修改记录

| 版本 | 日期 | 修改 |
| --- | --- | --- |
| 0.1 | 2026-11-08 | 初稿。 |
| 0.2 | 2026-11-14 | v0.2 加入 F04，即 `wordcount` 命令。新场景 v0.2-S10 到 v0.2-S17 直接运行该命令，并在 Windows PowerShell 中运行它。第 2.1 节遵循已批准的 F02 设计，该设计定下了名字 `count_lines`，并接受 `pathlib.Path`。第 4 节加入 Windows PowerShell 5.1。F02 的场景没有改变。 |
