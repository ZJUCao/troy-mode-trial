---
troy-doc: "v0.3-test-plan"
lang: "zh-CN"
version: "0.2"
updated: "2026-11-25"
status: "草稿。"
mirror-of: "test-plan.md"
---

# v0.3 版本测试方案

## 1. 版本

- 版本：v0.3
- 功能：F05、F06、F07
- 需求：[docs/requirements.zh-CN.md](../../requirements.zh-CN.md#6-版本计划)

## 2. 端到端场景

每个测试在临时文件夹里自建文件。它以二进制方式写入每个文件，内容为场景给出的确切字节，这样 Windows 不会把 `\n` 改成 `\r\n`。非 ASCII 字符按 UTF-8 编码，除非场景给出了别的字节。

这些场景遵循需求文档第 3 节的 `wordcount --lines FILE`、`wordcount --chars FILE` 和 `wordcount --longest FILE` 流程、F05、F06 和 F07 原型、决定 Q5、Q7、Q8 以及 Q10 到 Q16，还有架构文档第 6 节的错误处理。Troy 已批准 F05 和 F06 的设计，这两个功能都已验收。F07 的设计尚未编写。所以场景只依赖需求、原型以及已批准的 F04、F05 和 F06 设计已经定下的内容：

- 文件错误向标准错误写一行 `wordcount: <FILE>: <reason>`，并以退出码 2 结束（ADR-0002）。Q8 以及 F06 和 F07 的需求规定，每个选项给出的消息和退出码与 `wordcount FILE` 相同。所以对一个不是合法 UTF-8 的文件，场景把该选项的输出与同一文件的 `wordcount FILE` 输出相比较，而不固定原因文字。
- 错误的命令行以退出码 2 结束，标准输出为空，并向标准错误写一行用法说明。F05 的设计定下了用法说明 `usage: wordcount [--lines | --chars] FILE`，F07 的设计可能修改它以列出 `--longest`。所以场景只检查标准错误以 `usage:` 开头。

场景像 Troy 一样运行已安装的命令。发布测试在装好本项目的 conda 环境 `troy-mode-trial` 中运行，所以 `wordcount.exe` 位于该环境的脚本文件夹中，并在 `PATH` 上。如果 `PATH` 上没有 `wordcount`，测试失败，从不跳过。

- v0.3-S01 到 v0.3-S14 以及 v0.3-S17 到 v0.3-S24 启动 `PATH` 上的 `wordcount`，即 PowerShell 为 `wordcount` 启动的程序，作为一个新进程，并传入场景给出的参数。每个测试捕获标准输出、标准错误和退出码。
- v0.3-S15 和 v0.3-S25 在 Windows PowerShell 中运行命令，即 `powershell.exe -NoProfile -NonInteractive -Command`，以检查 PowerShell 能找到带各个选项的命令，并且 `$LASTEXITCODE` 保存着它的退出码。

场景比较输出时，把 `\r\n` 当作 `\n`。“一个换行符”指末尾的一个 `\n` 或一个 `\r\n`。除非场景另有说明，工作目录是文件所在的文件夹。

### 2.1 在 PowerShell 中统计行数（F05）

v0.3-S01 到 v0.3-S06 运行 `wordcount --lines`。该命令按 F02 的方式统计行数：`\n`、`\r\n` 和 `\r` 各结束一行，没有换行符的最后一行也计入，空文件有 0 行（Q2、Q3）。

### 2.2 在 PowerShell 中统计字符数（F06）

v0.3-S07 到 v0.3-S12 运行 `wordcount --chars`。一个字符是解码后文本中的一个 Unicode 码位，行尾也计入。`\r\n` 是两个字符，命令不转换任何行尾（Q11）。文件开头的一个字节顺序标记不计入（Q12）。

### 2.3 错误的命令行和 PowerShell（F05、F06 和 F07）

v0.3-S13 和 v0.3-S14 检查需求第 8 节以及决定 Q7、Q10 和 Q13 排除的命令行。v0.3-S15 像 Troy 一样在 PowerShell 中运行 `--lines` 和 `--chars`。v0.3-S16 由 Troy 手动运行，用到全部三个选项。

### 2.4 在 PowerShell 中查找最长的词（F07）

v0.3-S17 到 v0.3-S25 运行 `wordcount --longest`。一个词就是 F03 算作词的内容：一整段非空白字符，且其中至少有一个字母或数字。紧挨着词的标点属于该词（Q15）。长度是 Unicode 码位的个数，与 `--chars` 相同。文件开头的一个字节顺序标记不属于任何词（Q5）。没有词的文件打印 0。v0.3-S24 检查需求第 8 节以及决定 Q14 和 Q16 排除的命令行。

### 2.5 全部场景

下表按编号顺序列出第 2.1 到 2.4 节的场景。

| 编号 | 场景 | 由谁运行 | 步骤 | 预期结果 |
| --- | --- | --- | --- | --- |
| v0.3-S01 | 带选项统计一个文件的行数，不带选项统计其词数，与 F05 原型相同。 | Claude | 1. 写入 `notes.txt`，内容为 `Hello world\n  troy-mode  trial\n`。2. 运行 `wordcount --lines notes.txt`。3. 运行 `wordcount notes.txt`。 | 第 2 步恰好打印 `2` 加一个换行符。第 3 步恰好打印 `4` 加一个换行符。两次运行的标准错误都为空，退出码都为 0。 |
| v0.3-S02 | 统计一个不存在的文件的行数，与 F05 原型相同。 | Claude | 1. 把一个空文件夹设为工作目录。2. 运行 `wordcount --lines missing.txt`。 | 标准输出为空。标准错误恰好是 `wordcount: missing.txt: no such file` 加一个换行符。退出码为 2。 |
| v0.3-S03 | 统计一个不是合法 UTF-8 的文件的行数。 | Claude | 1. 写入 `latin1.txt`，内容为 Latin-1 编码的 `café au lait\n`，所以其字节以 `63 61 66 E9 20` 开头。2. 运行 `wordcount --lines latin1.txt`。3. 运行 `wordcount latin1.txt`。 | 第 2 步的标准输出为空，向标准错误写一行以 `wordcount: latin1.txt: ` 开头的内容加一个换行符，退出码为 2。它的标准错误和退出码与第 3 步的相同。 |
| v0.3-S04 | 统计一个空文件和一个只含一个换行符的文件的行数。 | Claude | 1. 写入一个空的 `empty.txt`。2. 写入 `one-break.txt`，内容只有 `\n`。3. 运行 `wordcount --lines empty.txt`。4. 运行 `wordcount --lines one-break.txt`。 | 第 3 步打印 `0` 加一个换行符。第 4 步打印 `1` 加一个换行符。两次运行的标准错误都为空，退出码都为 0。 |
| v0.3-S05 | 统计含空行的文件和混用全部三种换行符的文件的行数。 | Claude | 1. 写入 `blank-lines.txt`，内容为 `first\n\nthird\n`。2. 写入 `mixed-breaks.txt`，内容为 `one\rtwo\r\nthree\nfour`，末尾没有换行符。3. 运行 `wordcount --lines blank-lines.txt`。4. 运行 `wordcount --lines mixed-breaks.txt`。 | 第 3 步打印 `3` 加一个换行符。第 4 步打印 `4` 加一个换行符。两次运行的标准错误都为空，退出码都为 0。 |
| v0.3-S06 | 从另一个文件夹以绝对路径指定在 Windows 和 Linux 上生成的文件，该选项得到相同的行数。 | Claude | 1. 写入三个文件。`windows.txt` 内容为字节 `EF BB BF` 后接 `Hello world\r\n  troy-mode  trial\r\n`，与记事本保存的一样。`linux.txt` 内容为 `Hello world\n  troy-mode  trial\n`。`mixed.txt` 内容为 `Wait -- what ... don't x--y 3.14 _\r\n日本語　テキスト 😀\n`，其中 `日本語` 和 `テキスト` 之间的空白是 U+3000。2. 记录每个文件的字节。3. 把文件所在文件夹以外的一个文件夹设为工作目录。4. 按第 1 步的顺序，对每个文件以其绝对路径运行 `wordcount --lines`。 | 三次运行依次打印 `2`、`2` 和 `2`，每个后接一个换行符。每次运行的标准错误都为空，退出码都为 0。每个文件的字节与第 2 步记录的相同。 |
| v0.3-S07 | 带选项统计一个文件的字符数，不带选项统计其词数，与 F06 原型相同。 | Claude | 1. 写入 `notes.txt`，内容为 `Hello world\n  troy-mode  trial\n`。2. 运行 `wordcount --chars notes.txt`。3. 运行 `wordcount notes.txt`。 | 第 2 步恰好打印 `31` 加一个换行符。第 3 步恰好打印 `4` 加一个换行符。两次运行的标准错误都为空，退出码都为 0。 |
| v0.3-S08 | 统计字符而不是字节，与 F06 原型相同。 | Claude | 1. 写入 `hello.txt`，内容为 `你好\r\n`，共 8 个字节。2. 运行 `wordcount --chars hello.txt`。 | 标准输出恰好是 `4` 加一个换行符。标准错误为空。退出码为 0。 |
| v0.3-S09 | 统计一个不存在的文件的字符数，与 F06 原型相同。 | Claude | 1. 把一个空文件夹设为工作目录。2. 运行 `wordcount --chars missing.txt`。 | 标准输出为空。标准错误恰好是 `wordcount: missing.txt: no such file` 加一个换行符。退出码为 2。 |
| v0.3-S10 | 统计一个不是合法 UTF-8 的文件的字符数。 | Claude | 1. 按 v0.3-S03 写入 `latin1.txt`。2. 运行 `wordcount --chars latin1.txt`。3. 运行 `wordcount latin1.txt`。 | 第 2 步的标准输出为空，向标准错误写一行以 `wordcount: latin1.txt: ` 开头的内容加一个换行符，退出码为 2。它的标准错误和退出码与第 3 步的相同。 |
| v0.3-S11 | 统计一个空文件和一个只含字节顺序标记的文件的字符数。 | Claude | 1. 写入一个空的 `empty.txt`。2. 写入 `bom-only.txt`，内容只有字节 `EF BB BF`。3. 运行 `wordcount --chars empty.txt`。4. 运行 `wordcount --chars bom-only.txt`。 | 第 3 步和第 4 步各打印 `0` 加一个换行符。两次运行的标准错误都为空，退出码都为 0。 |
| v0.3-S12 | 该选项按文件中的原样统计每个行尾，跳过字节顺序标记，并在 Troy 的电脑上从另一个文件夹以绝对路径指定文件时，对同一文件得到相同的计数。 | Claude | 1. 以 v0.3-S06 第 1 步的字节写入 `windows.txt`、`linux.txt` 和 `mixed.txt`。2. 写入 `breaks.txt`，内容为 `one\rtwo\r\nthree\nfour`，末尾没有换行符。3. 记录每个文件的字节。4. 把文件所在文件夹以外的一个文件夹设为工作目录。5. 按第 1 步和第 2 步的顺序，对每个文件以其绝对路径运行 `wordcount --chars`。 | 四次运行依次打印 `33`、`31`、`47` 和 `19`，每个后接一个换行符。每次运行的标准错误都为空，退出码都为 0。每个文件的字节与第 3 步记录的相同。 |
| v0.3-S13 | 一条命令中同时给出两个选项，得到一行用法说明，而不是计数。 | Claude | 1. 按 v0.3-S01 写入 `notes.txt`。2. 运行 `wordcount --lines --chars notes.txt`。3. 运行 `wordcount --chars --lines notes.txt`。 | 每次运行的标准输出都为空，标准错误以 `usage:` 开头，退出码为 2。 |
| v0.3-S14 | 带选项的其他错误命令行得到一行用法说明，而不是计数。 | Claude | 1. 按 v0.3-S01 写入 `notes.txt`。2. 不带文件运行 `wordcount --lines`。3. 不带文件运行 `wordcount --chars`。4. 运行 `wordcount --lines notes.txt notes.txt`。5. 运行 `wordcount --chars notes.txt notes.txt`。6. 运行 `wordcount -l notes.txt`。7. 运行 `wordcount -c notes.txt`。 | 每次运行的标准输出都为空，标准错误以 `usage:` 开头，退出码为 2。 |
| v0.3-S15 | Troy 在一个名字含空格的文件夹中，在 PowerShell 会话里统计行数和字符数，与 F05 和 F06 原型相同。 | Claude | 1. 建一个名为 `my notes` 的文件夹，并按 v0.3-S01 在其中写入 `notes.txt`。2. 把 `my notes` 设为工作目录。3. 运行一个 Windows PowerShell 进程，即 `powershell.exe -NoProfile -NonInteractive -Command`，依次执行以下命令：`wordcount --lines notes.txt`、`Write-Output "exit $LASTEXITCODE"`、`wordcount --chars notes.txt`、`Write-Output "exit $LASTEXITCODE"`、`wordcount --lines missing.txt`、`Write-Output "exit $LASTEXITCODE"`、`wordcount --chars '<notes.txt 的绝对路径>'`、`Write-Output "exit $LASTEXITCODE"`、`wordcount --chars missing.txt` 和 `Write-Output "exit $LASTEXITCODE"`。 | 标准输出恰好依次是 `2`、`exit 0`、`31`、`exit 0`、`exit 2`、`31`、`exit 0` 和 `exit 2` 这几行。标准错误两次含有 `missing.txt`。 |
| v0.3-S16 | Troy 在 Windows Terminal 里统计一个含中文的文件的行数和字符数，并查找其最长词的长度。 | Troy | 1. 打开 Windows Terminal，在 conda 环境 `troy-mode-trial` 里用 PowerShell。2. 把一个文件夹设为工作目录。3. 运行 `Set-Content -Path chinese.txt -Encoding UTF8 -Value '你好 世界','第二 行'`。4. 运行 `wordcount --lines chinese.txt`。5. 运行 `wordcount --chars chinese.txt`。6. 运行 `wordcount chinese.txt`。7. 运行 `wordcount --longest chinese.txt`。 | Windows Terminal 依次显示 `2`、`13`、`4` 和 `2`，各占一行，没有错误。 |
| v0.3-S17 | 带选项查找一个文件最长词的长度，不带选项统计其词数，与 F07 原型相同。 | Claude | 1. 按 v0.3-S01 写入 `notes.txt`。2. 运行 `wordcount --longest notes.txt`。3. 运行 `wordcount notes.txt`。 | 第 2 步恰好打印 `9` 加一个换行符。第 3 步恰好打印 `4` 加一个换行符。两次运行的标准错误都为空，退出码都为 0。 |
| v0.3-S18 | 按字符而不是字节计量最长的词，连同其标点，与 F07 原型相同。 | Claude | 1. 写入 `greeting.txt`，内容为 `你好 世界!\r\n`。2. 运行 `wordcount --longest greeting.txt`。 | 标准输出恰好是 `3` 加一个换行符。标准错误为空。退出码为 0。 |
| v0.3-S19 | 查找没有词的文件的最长词，与 F07 原型相同。 | Claude | 1. 写入 `dashes.txt`，内容为 `-- ...\n`。2. 写入一个空的 `empty.txt`。3. 写入 `bom-only.txt`，内容只有字节 `EF BB BF`。4. 运行 `wordcount --longest dashes.txt`。5. 运行 `wordcount --longest empty.txt`。6. 运行 `wordcount --longest bom-only.txt`。 | 第 4、5、6 步各打印 `0` 加一个换行符。每次运行的标准错误都为空，退出码都为 0。 |
| v0.3-S20 | 查找一个不存在的文件的最长词，与 F07 原型相同。 | Claude | 1. 把一个空文件夹设为工作目录。2. 运行 `wordcount --longest missing.txt`。 | 标准输出为空。标准错误恰好是 `wordcount: missing.txt: no such file` 加一个换行符。退出码为 2。 |
| v0.3-S21 | 查找一个不是合法 UTF-8 的文件的最长词。 | Claude | 1. 按 v0.3-S03 写入 `latin1.txt`。2. 运行 `wordcount --longest latin1.txt`。3. 运行 `wordcount latin1.txt`。 | 第 2 步的标准输出为空，向标准错误写一行以 `wordcount: latin1.txt: ` 开头的内容加一个换行符，退出码为 2。它的标准错误和退出码与第 3 步的相同。 |
| v0.3-S22 | 该选项按码位计量整个词，包括标点，并跳过没有字母或数字的字符段。 | Claude | 1. 写入 `punct.txt`，内容为 `don't, stop.\n`。2. 写入 `combining.txt`，内容为 `cafe`，接着 U+0301，再接着 ` tea\n`。3. 以 v0.3-S06 第 1 步的字节写入 `mixed.txt`。4. 按第 1 到 3 步的顺序，对每个文件以其文件名运行 `wordcount --longest`。 | 三次运行依次打印 `6`、`5` 和 `5`，每个后接一个换行符。每次运行的标准错误都为空，退出码都为 0。 |
| v0.3-S23 | 对在 Windows 和 Linux 上生成的文件，该选项得到相同的长度，跳过字节顺序标记，并接受从另一个文件夹给出的绝对路径。 | Claude | 1. 以 v0.3-S06 第 1 步的字节写入 `windows.txt` 和 `linux.txt`。2. 按 v0.3-S12 第 2 步写入 `breaks.txt`。3. 写入 `bom-word.txt`，内容为字节 `EF BB BF` 后接 `troy-mode trial\n`。4. 记录每个文件的字节。5. 把文件所在文件夹以外的一个文件夹设为工作目录。6. 按第 1 到 3 步的顺序，对每个文件以其绝对路径运行 `wordcount --longest`。 | 四次运行依次打印 `9`、`9`、`5` 和 `9`，每个后接一个换行符。每次运行的标准错误都为空，退出码都为 0。每个文件的字节与第 4 步记录的相同。 |
| v0.3-S24 | 带 `--longest` 的错误命令行得到一行用法说明，而不是计数。 | Claude | 1. 按 v0.3-S01 写入 `notes.txt`。2. 运行 `wordcount --longest --lines notes.txt`。3. 运行 `wordcount --lines --longest notes.txt`。4. 运行 `wordcount --longest --chars notes.txt`。5. 运行 `wordcount --chars --longest notes.txt`。6. 不带文件运行 `wordcount --longest`。7. 运行 `wordcount --longest notes.txt notes.txt`。8. 运行 `wordcount -L notes.txt`。 | 每次运行的标准输出都为空，标准错误以 `usage:` 开头，退出码为 2。 |
| v0.3-S25 | Troy 在一个名字含空格的文件夹中，在 PowerShell 会话里查找最长的词，与 F07 原型相同。 | Claude | 1. 建一个名为 `my notes` 的文件夹。按 v0.3-S01 在其中写入 `notes.txt`，按 v0.3-S18 写入 `greeting.txt`。2. 把 `my notes` 设为工作目录。3. 运行一个 Windows PowerShell 进程，即 `powershell.exe -NoProfile -NonInteractive -Command`，依次执行以下命令：`wordcount --longest notes.txt`、`Write-Output "exit $LASTEXITCODE"`、`wordcount --longest '<greeting.txt 的绝对路径>'`、`Write-Output "exit $LASTEXITCODE"`、`wordcount --longest missing.txt` 和 `Write-Output "exit $LASTEXITCODE"`。 | 标准输出恰好依次是 `9`、`exit 0`、`3`、`exit 0` 和 `exit 2` 这几行。标准错误含有一次 `missing.txt`。 |

如果命令违反第 2.4 节的某条规则，v0.3-S22 和 v0.3-S23 的计数就会失败：

- `punct.txt` 因 `don't,` 打印 `6`。去掉逗号，这个词只有 5 个字符。
- `combining.txt` 因写成五个码位的 `café` 打印 `5`。合成为一个 `é` 后，这个词只有 4 个字符。
- `mixed.txt` 因 `don't` 打印 `5`。U+3000 把 `日本語` 和 `テキスト` 分开，而 `_` 和 `😀` 都不含字母或数字，所以都不是词。
- `breaks.txt` 因 `three` 打印 `5`。单独的 `\r` 是空白，所以 `one` 和 `two` 是两个词。
- `bom-word.txt` 因 `troy-mode` 打印 `9`。算上字节顺序标记，这个词会有 10 个字符。

虽然需求第 7 节承诺在 Windows 11 和 Linux 上得到相同的计数，但没有场景在 Linux 上运行。Claude 运行的场景只在 Troy 电脑上的发布测试中运行，那台电脑运行 Windows 11，而记录中没有 Troy 的 Linux 设备。v0.3-S05、v0.3-S06、v0.3-S12 和 v0.3-S23 改为在 Windows 上统计使用 Linux 换行符的文件。F05 和 F06 的功能测试在 CI 中于 Linux 上运行，F07 的功能测试也将如此。

v0.3-S15 和 v0.3-S25 使用 Windows PowerShell 5.1，即 `powershell.exe`，因为每台 Windows 11 都有它。没有场景运行 PowerShell 7，即 `pwsh`。两种 shell 启动的是同一个 `wordcount.exe`，所以 v0.3-S01 到 v0.3-S14 以及 v0.3-S17 到 v0.3-S24 对两者都成立。

在 v0.3-S16 中，`Set-Content` 写入 `你好 世界\r\n第二 行\r\n`，共 13 个字符。Windows PowerShell 5.1 还会在开头写一个字节顺序标记，PowerShell 7 不会。该标记不计入字符数（Q12），也不属于任何词（Q5），所以 Troy 在两种 shell 中都看到 `13` 和 `2`。

没有场景检查放在文件之后的选项，比如 `wordcount notes.txt --lines`，也没有场景检查缩写的选项，比如 `--line`。需求只给出 `wordcount --lines FILE` 这一种形式。已批准的 F05 和 F06 设计规定选项可以放在文件之后、缩写的选项算错误的命令行，并由它们的功能测试检查这两点。F07 的设计为 `--longest` 决定同样的问题，并由它的功能测试检查所决定的行为。

## 3. 性能和压力用例

无。需求第 7.1 节没有设任何性能指标，所以 v0.3 没有性能或压力用例（R14）。

## 4. 设备

| 设备 | 操作系统 | 由谁运行 |
| --- | --- | --- |
| Troy 的电脑 | Windows 11，conda 环境 `troy-mode-trial` 中的 Python 3.13，以及 Windows PowerShell 5.1 | Claude |
| Troy 的电脑，在 Windows Terminal 里 | Windows 11 | Troy |

Claude 运行的场景只在 Troy 电脑上的发布测试中运行，从不在 CI 中运行，所以 GitHub Actions 运行器不是这些场景的设备。Claude 的每个场景都运行 `wordcount` 命令，而脚本可以在 Troy 的电脑上启动该命令并读取其输出。v0.3-S16 由 Troy 运行：它检查 Windows Terminal 本身显示的内容，这是脚本读不到的。

## 5. 验收记录

无。Troy 尚未验收 v0.3。

## 6. 修改记录

| 版本 | 日期 | 修改 |
| --- | --- | --- |
| 0.1 | 2026-11-23 | 初稿，覆盖 F05 和 F06。 |
| 0.2 | 2026-11-25 | 根据需求 7.0 加入 F07，即 `--longest` 选项：新场景 v0.3-S17 到 v0.3-S25，并在 v0.3-S16 中加一个 `--longest` 步骤。方案现在依据已批准的 F05 和 F06 设计。v0.3-S01 到 v0.3-S15 不变。 |
