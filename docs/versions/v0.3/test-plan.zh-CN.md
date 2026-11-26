---
troy-doc: "v0.3-test-plan"
lang: "zh-CN"
version: "0.3"
updated: "2026-11-26"
status: "草稿。"
mirror-of: "test-plan.md"
---

# v0.3 版本测试方案

## 1. 版本

- 版本：v0.3
- 功能：F05、F06、F07、F08、F09
- 需求：[docs/requirements.zh-CN.md](../../requirements.zh-CN.md#6-版本计划)

## 2. 端到端场景

每个测试在临时文件夹里自建文件。它以二进制方式写入每个文件，内容为场景给出的确切字节，这样 Windows 不会把 `\n` 改成 `\r\n`。非 ASCII 字符按 UTF-8 编码，除非场景给出了别的字节。

这些场景遵循需求文档第 3 节的 `wordcount --lines FILE`、`wordcount --chars FILE`、`wordcount --longest FILE`、`wordcount --again FILE` 和 `wordcount --sentences FILE` 流程、F05 到 F09 原型、决定 Q5、Q7、Q8 以及 Q10 到 Q26、架构文档第 5 节的数据模型，还有架构文档第 6 节的错误处理。Troy 已批准 F05、F06 和 F07 的设计，这三个功能都已验收。F08 和 F09 的设计尚未编写。所以场景只依赖需求、原型、架构 4.0 以及已批准的 F04 到 F07 设计已经定下的内容：

- 文件错误向标准错误写一行 `wordcount: <FILE>: <reason>`，并以退出码 2 结束（ADR-0002）。Q8 以及 F06 到 F09 的需求规定，每个选项给出的消息和退出码与 `wordcount FILE` 相同。所以对一个不是合法 UTF-8 的文件，场景把该选项的输出与同一文件的 `wordcount FILE` 输出相比较，而不固定原因文字。
- 错误的命令行以退出码 2 结束，标准输出为空，并向标准错误写一行用法说明。F07 的设计定下了用法说明 `usage: wordcount [--lines | --chars | --longest] FILE`，F08 和 F09 的设计可能修改它以列出 `--again` 和 `--sentences`。所以场景只检查标准错误以 `usage:` 开头。
- `--again` 的设置错误和设置警告各写一行指明设置文件的内容（需求 Q20 和 Q22，架构第 6 节）。F08 原型展示了一个设置错误，但把确切文字留给 F08 的设计。所以场景检查标准错误恰好是一行含有设置文件绝对路径的内容；在 PowerShell 会话中，则检查标准错误含有 `settings.json`。
- 设置文件是 UTF-8 JSON：一个恰好有一个键的对象，对没有计数选项的运行，其值为 `null`，否则为该次运行的选项名（架构第 5 节）。F08 的设计定下键和这些名字。所以 v0.3-S35 检查文件的结构，而不检查其键或名字；v0.3-S32 只写入无论 F08 的设计选什么键都破坏该结构的内容。

场景像 Troy 一样运行已安装的命令。发布测试在装好本项目的 conda 环境 `troy-mode-trial` 中运行，所以 `wordcount.exe` 位于该环境的脚本文件夹中，并在 `PATH` 上。如果 `PATH` 上没有 `wordcount`，测试失败，从不跳过。

Claude 运行的场景从不读写 Troy 真正的数据文件夹（架构第 10 节）。`version-tests/conftest.py` 中的自动 fixture 为每个测试把 `APPDATA` 和 `XDG_DATA_HOME` 设为文件所在文件夹之外的一个新的空文件夹。本方案把该文件夹称为数据文件夹。测试启动的每个 `wordcount` 和 `powershell.exe` 进程都继承这两个变量，所以设置文件是 `<数据文件夹>\wordcount\settings.json`。本方案把这个路径称为设置文件。需要第二个数据文件夹的场景会写明。

- v0.3-S01 到 v0.3-S14、v0.3-S17 到 v0.3-S24、v0.3-S26 到 v0.3-S37 以及 v0.3-S39 到 v0.3-S47 启动 `PATH` 上的 `wordcount`，即 PowerShell 为 `wordcount` 启动的程序，作为一个新进程，并传入场景给出的参数。每个测试捕获标准输出、标准错误和退出码。
- v0.3-S15、v0.3-S25、v0.3-S38 和 v0.3-S48 在 Windows PowerShell 中运行命令，即 `powershell.exe -NoProfile -NonInteractive -Command`，以检查 PowerShell 能找到带各个选项的命令，并且 `$LASTEXITCODE` 保存着它的退出码。

场景比较输出时，把 `\r\n` 当作 `\n`。“一个换行符”指末尾的一个 `\n` 或一个 `\r\n`。除非场景另有说明，工作目录是文件所在的文件夹。

### 2.1 在 PowerShell 中统计行数（F05）

v0.3-S01 到 v0.3-S06 运行 `wordcount --lines`。该命令按 F02 的方式统计行数：`\n`、`\r\n` 和 `\r` 各结束一行，没有换行符的最后一行也计入，空文件有 0 行（Q2、Q3）。

### 2.2 在 PowerShell 中统计字符数（F06）

v0.3-S07 到 v0.3-S12 运行 `wordcount --chars`。一个字符是解码后文本中的一个 Unicode 码位，行尾也计入。`\r\n` 是两个字符，命令不转换任何行尾（Q11）。文件开头的一个字节顺序标记不计入（Q12）。

### 2.3 错误的命令行和 PowerShell（F05 到 F09）

v0.3-S13 和 v0.3-S14 检查需求第 8 节以及决定 Q7、Q10 和 Q13 排除的命令行。v0.3-S15 像 Troy 一样在 PowerShell 中运行 `--lines` 和 `--chars`。v0.3-S16 由 Troy 手动运行，用到全部五个选项。

### 2.4 在 PowerShell 中查找最长的词（F07）

v0.3-S17 到 v0.3-S25 运行 `wordcount --longest`。一个词就是 F03 算作词的内容：一整段非空白字符，且其中至少有一个字母或数字。紧挨着词的标点属于该词（Q15）。长度是 Unicode 码位的个数，与 `--chars` 相同。文件开头的一个字节顺序标记不属于任何词（Q5）。没有词的文件打印 0。v0.3-S24 检查需求第 8 节以及决定 Q14 和 Q16 排除的命令行。

### 2.5 在 PowerShell 中以上次的选项再次运行（F08）

v0.3-S26 到 v0.3-S38 运行 `wordcount --again`。每次打印出计数的运行都把它的选项，或它没有选项这一点，保存在设置文件中，`--again FILE` 用该选项统计 FILE（Q17、Q18）。失败的运行，无论是文件错误还是错误的命令行，都让设置文件保持原样（Q19）。没有已保存的选项，或设置文件无法读取时，`--again` 是一个设置错误，退出码为 2（Q20）。`--again` 与计数选项一起使用是错误的命令行（Q21）。设置文件无法写入时，计数仍然打印，退出码为 0，并有一条警告写到标准错误（Q22）。在每个场景中，“v0.3-S27 的文件”指工作目录中按 v0.3-S01 写入的 `notes.txt` 和按 v0.3-S27 写入的 `greeting.txt`。

### 2.6 在 PowerShell 中统计句子数（F09）

v0.3-S39 到 v0.3-S48 运行 `wordcount --sentences`。一个句子是一段以一串 `.`、`!` 或 `?` 结尾的文本，且其中至少有一个字母或数字，即一个使 `str.isalnum()` 为真的字符（Q23、Q24）。最后一个标点之后的文本不是句子（Q25）。标点无论出现在哪里都结束一个句子，在数字中也是如此。换行符不结束句子，中文标点 `。`、`！` 和 `？` 也不结束句子（Q26）。文件开头的一个字节顺序标记被忽略（Q5）。v0.3-S46 检查需求第 8 节以及决定 Q13 排除的命令行。v0.3-S47 检查 `--again` 也会保存 `--sentences`（需求第 5 节）。

### 2.7 全部场景

下表按编号顺序列出第 2.1 到 2.6 节的场景。

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
| v0.3-S16 | Troy 在 Windows Terminal 里统计一个含中文的文件的行数、字符数和句子数，查找其最长词的长度，以上次的选项再次运行，并查看 Troy 自己数据文件夹中的设置文件。 | Troy | 1. 打开 Windows Terminal，在 conda 环境 `troy-mode-trial` 里用 PowerShell。2. 把一个文件夹设为工作目录。3. 运行 `Set-Content -Path chinese.txt -Encoding UTF8 -Value '你好 世界','第二 行'`。4. 运行 `wordcount --lines chinese.txt`。5. 运行 `wordcount --chars chinese.txt`。6. 运行 `wordcount chinese.txt`。7. 运行 `wordcount --longest chinese.txt`。8. 运行 `wordcount --again chinese.txt`。9. 运行 `wordcount --sentences chinese.txt`。10. 运行 `Get-Content "$env:APPDATA\wordcount\settings.json"`。 | 第 4 到 9 步依次显示 `2`、`13`、`4`、`2`、`2` 和 `0`，各占一行，没有错误。第 10 步显示已保存的选项，即 sentences，既不含 `chinese.txt`，也不含该文件的任何文字。 |
| v0.3-S17 | 带选项查找一个文件最长词的长度，不带选项统计其词数，与 F07 原型相同。 | Claude | 1. 按 v0.3-S01 写入 `notes.txt`。2. 运行 `wordcount --longest notes.txt`。3. 运行 `wordcount notes.txt`。 | 第 2 步恰好打印 `9` 加一个换行符。第 3 步恰好打印 `4` 加一个换行符。两次运行的标准错误都为空，退出码都为 0。 |
| v0.3-S18 | 按字符而不是字节计量最长的词，连同其标点，与 F07 原型相同。 | Claude | 1. 写入 `greeting.txt`，内容为 `你好 世界!\r\n`。2. 运行 `wordcount --longest greeting.txt`。 | 标准输出恰好是 `3` 加一个换行符。标准错误为空。退出码为 0。 |
| v0.3-S19 | 查找没有词的文件的最长词，与 F07 原型相同。 | Claude | 1. 写入 `dashes.txt`，内容为 `-- ...\n`。2. 写入一个空的 `empty.txt`。3. 写入 `bom-only.txt`，内容只有字节 `EF BB BF`。4. 运行 `wordcount --longest dashes.txt`。5. 运行 `wordcount --longest empty.txt`。6. 运行 `wordcount --longest bom-only.txt`。 | 第 4、5、6 步各打印 `0` 加一个换行符。每次运行的标准错误都为空，退出码都为 0。 |
| v0.3-S20 | 查找一个不存在的文件的最长词，与 F07 原型相同。 | Claude | 1. 把一个空文件夹设为工作目录。2. 运行 `wordcount --longest missing.txt`。 | 标准输出为空。标准错误恰好是 `wordcount: missing.txt: no such file` 加一个换行符。退出码为 2。 |
| v0.3-S21 | 查找一个不是合法 UTF-8 的文件的最长词。 | Claude | 1. 按 v0.3-S03 写入 `latin1.txt`。2. 运行 `wordcount --longest latin1.txt`。3. 运行 `wordcount latin1.txt`。 | 第 2 步的标准输出为空，向标准错误写一行以 `wordcount: latin1.txt: ` 开头的内容加一个换行符，退出码为 2。它的标准错误和退出码与第 3 步的相同。 |
| v0.3-S22 | 该选项按码位计量整个词，包括标点，并跳过没有字母或数字的字符段。 | Claude | 1. 写入 `punct.txt`，内容为 `don't, stop.\n`。2. 写入 `combining.txt`，内容为 `cafe`，接着 U+0301，再接着 ` tea\n`。3. 以 v0.3-S06 第 1 步的字节写入 `mixed.txt`。4. 按第 1 到 3 步的顺序，对每个文件以其文件名运行 `wordcount --longest`。 | 三次运行依次打印 `6`、`5` 和 `5`，每个后接一个换行符。每次运行的标准错误都为空，退出码都为 0。 |
| v0.3-S23 | 对在 Windows 和 Linux 上生成的文件，该选项得到相同的长度，跳过字节顺序标记，并接受从另一个文件夹给出的绝对路径。 | Claude | 1. 以 v0.3-S06 第 1 步的字节写入 `windows.txt` 和 `linux.txt`。2. 按 v0.3-S12 第 2 步写入 `breaks.txt`。3. 写入 `bom-word.txt`，内容为字节 `EF BB BF` 后接 `troy-mode trial\n`。4. 记录每个文件的字节。5. 把文件所在文件夹以外的一个文件夹设为工作目录。6. 按第 1 到 3 步的顺序，对每个文件以其绝对路径运行 `wordcount --longest`。 | 四次运行依次打印 `9`、`9`、`5` 和 `9`，每个后接一个换行符。每次运行的标准错误都为空，退出码都为 0。每个文件的字节与第 4 步记录的相同。 |
| v0.3-S24 | 带 `--longest` 的错误命令行得到一行用法说明，而不是计数。 | Claude | 1. 按 v0.3-S01 写入 `notes.txt`。2. 运行 `wordcount --longest --lines notes.txt`。3. 运行 `wordcount --lines --longest notes.txt`。4. 运行 `wordcount --longest --chars notes.txt`。5. 运行 `wordcount --chars --longest notes.txt`。6. 不带文件运行 `wordcount --longest`。7. 运行 `wordcount --longest notes.txt notes.txt`。8. 运行 `wordcount -L notes.txt`。 | 每次运行的标准输出都为空，标准错误以 `usage:` 开头，退出码为 2。 |
| v0.3-S25 | Troy 在一个名字含空格的文件夹中，在 PowerShell 会话里查找最长的词，与 F07 原型相同。 | Claude | 1. 建一个名为 `my notes` 的文件夹。按 v0.3-S01 在其中写入 `notes.txt`，按 v0.3-S18 写入 `greeting.txt`。2. 把 `my notes` 设为工作目录。3. 运行一个 Windows PowerShell 进程，即 `powershell.exe -NoProfile -NonInteractive -Command`，依次执行以下命令：`wordcount --longest notes.txt`、`Write-Output "exit $LASTEXITCODE"`、`wordcount --longest '<greeting.txt 的绝对路径>'`、`Write-Output "exit $LASTEXITCODE"`、`wordcount --longest missing.txt` 和 `Write-Output "exit $LASTEXITCODE"`。 | 标准输出恰好依次是 `9`、`exit 0`、`3`、`exit 0` 和 `exit 2` 这几行。标准错误含有一次 `missing.txt`。 |
| v0.3-S26 | 在任何运行保存选项之前再次运行，与 F08 原型相同。 | Claude | 1. 按 v0.3-S01 写入 `notes.txt`。2. 运行 `wordcount --again notes.txt`。 | 标准输出为空。标准错误恰好是一行含有设置文件绝对路径的内容加一个换行符。退出码为 2。之后设置文件不存在。 |
| v0.3-S27 | 以上次的选项再次运行，以及在上次没有选项时再次运行，与 F08 原型相同。 | Claude | 1. 按 v0.3-S01 写入 `notes.txt`，并写入 `greeting.txt`，内容为 `你好 世界!\r\n`。2. 运行 `wordcount --lines notes.txt`。3. 运行 `wordcount --again greeting.txt`。4. 运行 `wordcount notes.txt`。5. 运行 `wordcount --again greeting.txt`。 | 第 2 到 5 步依次打印 `2`、`1`、`4` 和 `2`，每个后接一个换行符。每次运行的标准错误都为空，退出码都为 0。 |
| v0.3-S28 | 在 `--chars` 和 `--longest` 之后再次运行，并多次再次运行。 | Claude | 1. 写入 v0.3-S27 的文件。2. 运行 `wordcount --chars notes.txt`。3. 运行 `wordcount --again greeting.txt`。4. 运行 `wordcount --again notes.txt`。5. 运行 `wordcount --longest notes.txt`。6. 运行 `wordcount --again greeting.txt`。7. 运行 `wordcount --again greeting.txt`。 | 第 2 到 7 步依次打印 `31`、`8`、`31`、`9`、`3` 和 `3`，每个后接一个换行符。每次运行的标准错误都为空，退出码都为 0。 |
| v0.3-S29 | 失败的运行保留已保存的选项，与 F08 原型相同。 | Claude | 1. 写入 v0.3-S27 的文件，并按 v0.3-S03 写入 `latin1.txt`。2. 运行 `wordcount --longest notes.txt`。3. 记录设置文件的字节。4. 运行 `wordcount --longest missing.txt`。5. 运行 `wordcount --lines latin1.txt`。6. 运行 `wordcount --lines --chars notes.txt`。7. 不带文件运行 `wordcount --chars`。8. 运行 `wordcount --again greeting.txt`。 | 第 2 步打印 `9` 加一个换行符。第 4 步的标准输出为空，向标准错误恰好写入 `wordcount: missing.txt: no such file` 加一个换行符，退出码为 2。第 5 到 7 步的标准输出都为空，退出码都为 2。第 4 到 7 步每步之后，设置文件的字节都与第 3 步记录的相同。第 8 步打印 `3` 加一个换行符，标准错误为空，退出码为 0。 |
| v0.3-S30 | 失败的首次运行不保存任何选项。 | Claude | 1. 按 v0.3-S01 写入 `notes.txt`。2. 运行 `wordcount --lines missing.txt`。3. 运行 `wordcount --chars --lines notes.txt`。4. 运行 `wordcount --again notes.txt`。 | 第 2 步和第 3 步的标准输出都为空，退出码都为 2。这两步每步之后，设置文件都不存在。第 4 步的结果与 v0.3-S26 相同。 |
| v0.3-S31 | 对一个不存在的文件和一个不是合法 UTF-8 的文件再次运行。 | Claude | 1. 写入 v0.3-S27 的文件，并按 v0.3-S03 写入 `latin1.txt`。2. 运行 `wordcount --lines notes.txt`。3. 记录设置文件的字节。4. 运行 `wordcount --again missing.txt`。5. 运行 `wordcount --again latin1.txt`。6. 运行 `wordcount latin1.txt`。7. 运行 `wordcount --again greeting.txt`。 | 第 4 步的标准输出为空，向标准错误恰好写入 `wordcount: missing.txt: no such file` 加一个换行符，退出码为 2。第 5 步的标准输出为空，向标准错误写一行以 `wordcount: latin1.txt: ` 开头的内容加一个换行符，退出码为 2。它的标准错误和退出码与第 6 步的相同。第 4 到 6 步每步之后，设置文件的字节都与第 3 步记录的相同。第 7 步打印 `1` 加一个换行符，标准错误为空，退出码为 0。 |
| v0.3-S32 | 在设置文件无法读取时再次运行。 | Claude | 1. 按 v0.3-S01 写入 `notes.txt`。2. 建立数据文件夹中的 `wordcount` 文件夹。3. 依次对下列每种设置文件，用它替换设置文件，并运行 `wordcount --again notes.txt`：文字 `{not json`、一个空文件、文字 `[]`、文字 `{}`、文字 `{"a": null, "b": null}`、文字 `{"option": 5}`、文字 `{"option": "again"}`、字节 `FF FE FD`，以及一个代替该文件的、名为 `settings.json` 的空文件夹。 | 每次运行的标准输出都为空，标准错误恰好是一行含有设置文件绝对路径的内容加一个换行符，退出码为 2。每次运行之后，设置文件的字节都与第 3 步写入的相同，或者文件夹 `settings.json` 仍在且为空。 |
| v0.3-S33 | 一次计数替换掉无法读取的设置文件。 | Claude | 1. 写入 v0.3-S27 的文件。2. 建立数据文件夹中的 `wordcount` 文件夹，并把设置文件写为文字 `{not json`。3. 运行 `wordcount --lines notes.txt`。4. 运行 `wordcount --again greeting.txt`。 | 第 3 步和第 4 步依次打印 `2` 和 `1`，每个后接一个换行符。两次运行的标准错误都为空，退出码都为 0。 |
| v0.3-S34 | 带 `--again` 的错误命令行得到一行用法说明，而不是计数，并保留已保存的选项。 | Claude | 1. 写入 v0.3-S27 的文件。2. 运行 `wordcount --lines notes.txt`。3. 记录设置文件的字节。4. 运行 `wordcount --again --lines notes.txt`。5. 运行 `wordcount --lines --again notes.txt`。6. 运行 `wordcount --again --chars notes.txt`。7. 运行 `wordcount --again --longest notes.txt`。8. 运行 `wordcount --again --sentences notes.txt`。9. 不带文件运行 `wordcount --again`。10. 运行 `wordcount --again notes.txt notes.txt`。11. 运行 `wordcount -a notes.txt`。12. 运行 `wordcount --again greeting.txt`。 | 第 4 到 11 步每步的标准输出都为空，标准错误以 `usage:` 开头，退出码为 2，之后设置文件的字节与第 3 步记录的相同。第 12 步打印 `1` 加一个换行符，标准错误为空，退出码为 0。 |
| v0.3-S35 | 设置文件位于数据文件夹中，并且只保存选项。 | Claude | 1. 在文件所在文件夹之外建第二个空的数据文件夹，并在本场景的运行中把 `XDG_DATA_HOME` 设为它。`APPDATA` 仍是数据文件夹。2. 建一个名为 `private-notes` 的文件夹，在其中写入 `secret-plan.txt`，内容为 `Hello world\n  troy-mode  trial\n`，并把 `private-notes` 设为工作目录。3. 运行 `wordcount --lines secret-plan.txt`。4. 读取设置文件。5. 运行 `wordcount secret-plan.txt`。6. 读取设置文件。 | 第 3 步和第 5 步依次打印 `2` 和 `4`，每个后接一个换行符，标准错误都为空，退出码都为 0。这两步每步之后，数据文件夹中只有文件夹 `wordcount`，其中只有文件 `settings.json`。第二个数据文件夹保持为空，`private-notes` 中只有 `secret-plan.txt`。在第 4 步和第 6 步中，设置文件是 UTF-8 JSON：一个恰好有一个键的对象。其值在第 4 步是一个字符串，在第 6 步是 `null`。两次读取的内容都不含 `secret-plan`、`private-notes`、`Hello`、`world`、`troy-mode` 或 `trial`。 |
| v0.3-S36 | 从另一个文件夹以绝对路径再次运行。 | Claude | 1. 建文件夹 `first` 和 `elsewhere`。按 v0.3-S01 在 `first` 中写入 `notes.txt`，按 v0.3-S27 在 `elsewhere` 中写入 `greeting.txt`。2. 把 `first` 设为工作目录。3. 运行 `wordcount --chars notes.txt`。4. 把第三个文件夹设为工作目录。5. 以 `greeting.txt` 的绝对路径运行 `wordcount --again`。 | 第 3 步和第 5 步依次打印 `31` 和 `8`，每个后接一个换行符。两次运行的标准错误都为空，退出码都为 0。 |
| v0.3-S37 | 设置文件无法写入时，计数仍然打印。 | Claude | 1. 按 v0.3-S01 写入 `notes.txt`。2. 在数据文件夹中写入一个名为 `wordcount` 的文件，而不是文件夹，内容为文字 `x`。3. 运行 `wordcount --lines notes.txt`。4. 运行 `wordcount notes.txt`。5. 运行 `wordcount --again notes.txt`。6. 删除文件 `wordcount`。建立文件夹 `wordcount`，并在其中建一个名为 `settings.json` 的空文件夹。7. 运行 `wordcount --chars notes.txt`。 | 第 3、4、7 步依次打印 `2`、`4` 和 `31`，每个后接一个换行符。这三步各向标准错误恰好写一行含有设置文件绝对路径的内容加一个换行符，退出码为 0。第 5 步的标准输出为空，向标准错误恰好写一行含有设置文件绝对路径的内容加一个换行符，退出码为 2。第 5 步之后，文件 `wordcount` 的内容仍是 `x`。第 7 步之后，文件夹 `settings.json` 仍在且为空。 |
| v0.3-S38 | Troy 在一个名字含空格的文件夹中，在 PowerShell 会话里以上次的选项再次运行，与 F08 原型相同。 | Claude | 1. 建一个名为 `my notes` 的文件夹，并在其中写入 v0.3-S27 的文件。2. 把 `my notes` 设为工作目录。3. 运行一个 Windows PowerShell 进程，即 `powershell.exe -NoProfile -NonInteractive -Command`，依次执行以下命令：`wordcount --again notes.txt`、`Write-Output "exit $LASTEXITCODE"`、`wordcount --lines notes.txt`、`Write-Output "exit $LASTEXITCODE"`、`wordcount --again greeting.txt`、`Write-Output "exit $LASTEXITCODE"`、`wordcount notes.txt`、`Write-Output "exit $LASTEXITCODE"`、`wordcount --again '<greeting.txt 的绝对路径>'`、`Write-Output "exit $LASTEXITCODE"`、`wordcount --longest notes.txt`、`Write-Output "exit $LASTEXITCODE"`、`wordcount --longest missing.txt`、`Write-Output "exit $LASTEXITCODE"`、`wordcount --again greeting.txt` 和 `Write-Output "exit $LASTEXITCODE"`。 | 标准输出恰好依次是 `exit 2`、`2`、`exit 0`、`1`、`exit 0`、`4`、`exit 0`、`2`、`exit 0`、`9`、`exit 0`、`exit 2`、`3` 和 `exit 0` 这几行。标准错误含有一次 `settings.json` 和一次 `missing.txt`。 |
| v0.3-S39 | 带选项统计一个文件的句子数，不带选项统计其词数，与 F09 原型相同。 | Claude | 1. 写入 `story.txt`，内容为 `It rains. Does it stop? Yes!!\nWait...\n`。2. 运行 `wordcount --sentences story.txt`。3. 运行 `wordcount story.txt`。 | 第 2 步恰好打印 `4` 加一个换行符。第 3 步恰好打印 `7` 加一个换行符。两次运行的标准错误都为空，退出码都为 0。 |
| v0.3-S40 | 最后一个标点之后的文本，以及数字中的标点，与 F09 原型相同。 | Claude | 1. 写入 `draft.txt`，内容为 `Done. Not yet\r\n`。2. 写入 `pi.txt`，内容为 `Pi is 3.14.\n`。3. 运行 `wordcount --sentences draft.txt`。4. 运行 `wordcount --sentences pi.txt`。 | 第 3 步打印 `1` 加一个换行符。第 4 步打印 `2` 加一个换行符。两次运行的标准错误都为空，退出码都为 0。 |
| v0.3-S41 | 统计没有句子的文件的句子数，与 F09 原型相同。 | Claude | 1. 写入 `dashes.txt`，内容为 `-- ...\n`。2. 写入一个空的 `empty.txt`。3. 写入 `bom-only.txt`，内容只有字节 `EF BB BF`。4. 运行 `wordcount --sentences dashes.txt`。5. 运行 `wordcount --sentences empty.txt`。6. 运行 `wordcount --sentences bom-only.txt`。 | 第 4、5、6 步各打印 `0` 加一个换行符。每次运行的标准错误都为空，退出码都为 0。 |
| v0.3-S42 | 统计一个不存在的文件的句子数，与 F09 原型相同。 | Claude | 1. 把一个空文件夹设为工作目录。2. 运行 `wordcount --sentences missing.txt`。 | 标准输出为空。标准错误恰好是 `wordcount: missing.txt: no such file` 加一个换行符。退出码为 2。 |
| v0.3-S43 | 统计一个不是合法 UTF-8 的文件的句子数。 | Claude | 1. 按 v0.3-S03 写入 `latin1.txt`。2. 运行 `wordcount --sentences latin1.txt`。3. 运行 `wordcount latin1.txt`。 | 第 2 步的标准输出为空，向标准错误写一行以 `wordcount: latin1.txt: ` 开头的内容加一个换行符，退出码为 2。它的标准错误和退出码与第 3 步的相同。 |
| v0.3-S44 | 该选项只在字母或数字之后的一串 `.`、`!` 或 `?` 处结束一个句子。 | Claude | 1. 写入 `runs.txt`，内容为 `Really?! Yes... No!?!\n`。2. 写入 `lines.txt`，内容为 `Wait\nfor me.\nOK\n`。3. 写入 `chinese.txt`，内容为 `你好。世界！真的？\n`，其中的标点是 U+3002、U+FF01 和 U+FF1F。4. 写入 `mixed-marks.txt`，内容为 `你好。世界!\n`，其中第一个标点是 U+3002，第二个是 `!`。5. 写入 `no-alnum.txt`，内容为 `Hi. ... -- ?! Bye.\n`。6. 按第 1 到 5 步的顺序，对每个文件以其文件名运行 `wordcount --sentences`。 | 五次运行依次打印 `3`、`1`、`0`、`1` 和 `2`，每个后接一个换行符。每次运行的标准错误都为空，退出码都为 0。 |
| v0.3-S45 | 对在 Windows 和 Linux 上生成的文件，该选项得到相同的计数，跳过字节顺序标记，并接受从另一个文件夹给出的绝对路径。 | Claude | 1. 写入 `windows-story.txt`，内容为字节 `EF BB BF` 后接 `It rains. Does it stop? Yes!!\r\nWait...\r\n`。2. 按 v0.3-S39 写入 `story.txt`。3. 写入 `breaks.txt`，内容为 `One.\rTwo?\r\nThree!\nfour`，末尾没有换行符。4. 以 v0.3-S06 第 1 步的字节写入 `mixed.txt`。5. 记录每个文件的字节。6. 把文件所在文件夹以外的一个文件夹设为工作目录。7. 按第 1 到 4 步的顺序，对每个文件以其绝对路径运行 `wordcount --sentences`。 | 四次运行依次打印 `4`、`4`、`3` 和 `2`，每个后接一个换行符。每次运行的标准错误都为空，退出码都为 0。每个文件的字节与第 5 步记录的相同。 |
| v0.3-S46 | 带 `--sentences` 的错误命令行得到一行用法说明，而不是计数。 | Claude | 1. 按 v0.3-S01 写入 `notes.txt`。2. 运行 `wordcount --sentences --lines notes.txt`。3. 运行 `wordcount --lines --sentences notes.txt`。4. 运行 `wordcount --sentences --chars notes.txt`。5. 运行 `wordcount --chars --sentences notes.txt`。6. 运行 `wordcount --sentences --longest notes.txt`。7. 运行 `wordcount --longest --sentences notes.txt`。8. 不带文件运行 `wordcount --sentences`。9. 运行 `wordcount --sentences notes.txt notes.txt`。10. 运行 `wordcount -s notes.txt`。 | 每次运行的标准输出都为空，标准错误以 `usage:` 开头，退出码为 2。 |
| v0.3-S47 | 在 `--sentences` 之后再次运行。 | Claude | 1. 按 v0.3-S39 写入 `story.txt`，按 v0.3-S40 写入 `draft.txt` 和 `pi.txt`。2. 运行 `wordcount --sentences story.txt`。3. 运行 `wordcount --again pi.txt`。4. 运行 `wordcount --again draft.txt`。 | 第 2 到 4 步依次打印 `4`、`2` 和 `1`，每个后接一个换行符。每次运行的标准错误都为空，退出码都为 0。 |
| v0.3-S48 | Troy 在一个名字含空格的文件夹中，在 PowerShell 会话里统计句子数，与 F09 原型相同。 | Claude | 1. 建一个名为 `my notes` 的文件夹。按 v0.3-S39 在其中写入 `story.txt`，按 v0.3-S40 写入 `pi.txt`。2. 把 `my notes` 设为工作目录。3. 运行一个 Windows PowerShell 进程，即 `powershell.exe -NoProfile -NonInteractive -Command`，依次执行以下命令：`wordcount --sentences story.txt`、`Write-Output "exit $LASTEXITCODE"`、`wordcount --sentences '<pi.txt 的绝对路径>'`、`Write-Output "exit $LASTEXITCODE"`、`wordcount --sentences missing.txt`、`Write-Output "exit $LASTEXITCODE"`、`wordcount --again story.txt` 和 `Write-Output "exit $LASTEXITCODE"`。 | 标准输出恰好依次是 `4`、`exit 0`、`2`、`exit 0`、`exit 2`、`4` 和 `exit 0` 这几行。标准错误含有一次 `missing.txt`。 |

如果命令违反第 2.4 节的某条规则，v0.3-S22 和 v0.3-S23 的计数就会失败：

- `punct.txt` 因 `don't,` 打印 `6`。去掉逗号，这个词只有 5 个字符。
- `combining.txt` 因写成五个码位的 `café` 打印 `5`。合成为一个 `é` 后，这个词只有 4 个字符。
- `mixed.txt` 因 `don't` 打印 `5`。U+3000 把 `日本語` 和 `テキスト` 分开，而 `_` 和 `😀` 都不含字母或数字，所以都不是词。
- `breaks.txt` 因 `three` 打印 `5`。单独的 `\r` 是空白，所以 `one` 和 `two` 是两个词。
- `bom-word.txt` 因 `troy-mode` 打印 `9`。算上字节顺序标记，这个词会有 10 个字符。

如果命令违反第 2.6 节的某条规则，v0.3-S44 和 v0.3-S45 的计数就会失败：

- `runs.txt` 打印 `3`，因为 `?!` 或 `!?!` 这样的一串标点只结束一个句子（Q23）。每个标点算一个句子会得到 `8`。
- `lines.txt` 打印 `1`，因为换行符不结束句子。`Wait` 和 `OK` 都不以标点结尾。
- `chinese.txt` 打印 `0`，因为 `。`、`！` 和 `？` 不结束句子（Q26）。把它们算上会得到 `3`。
- `mixed-marks.txt` 因那一个 `!` 打印 `1`。把 `。` 算上会得到 `2`。
- `no-alnum.txt` 因 `Hi.` 和 `Bye.` 打印 `2`。`...` 和 `-- ?!` 这两段不含字母或数字（Q24）。把它们算上会得到 `4`。
- `breaks.txt` 打印 `3`，因为 `four` 不以标点结尾（Q25）。把它算上会得到 `4`。
- `mixed.txt` 因 `Wait -- what ...` 和 `don't x--y 3.` 打印 `2`，因为 `3.14` 中的小数点也结束一个句子。其后的文本不以标点结尾。

在 v0.3-S32 中，文字 `{}` 没有键，文字 `{"a": null, "b": null}` 有两个键。文字 `{"option": 5}` 和 `{"option": "again"}` 有一个键，但 `5` 不是字符串，`again` 不是计数选项。所以无论 F08 的设计选什么键，它们都破坏架构第 5 节的结构。

v0.3-S34 和 v0.3-S46 运行 `-a` 和 `-s`。需求第 8 节排除了 `--lines`、`--chars`、`--longest`、`--sentences` 和 `--again` 以外的所有选项，所以该命令没有 `--again` 或 `--sentences` 的短形式。

虽然需求第 7 节承诺在 Windows 11 和 Linux 上得到相同的计数，但没有场景在 Linux 上运行。Claude 运行的场景只在 Troy 电脑上的发布测试中运行，那台电脑运行 Windows 11，而记录中没有 Troy 的 Linux 设备。v0.3-S05、v0.3-S06、v0.3-S12、v0.3-S23 和 v0.3-S45 改为在 Windows 上统计使用 Linux 换行符的文件。F05、F06 和 F07 的功能测试在 CI 中于 Linux 上运行，F08 和 F09 的功能测试也将如此。

出于同样的原因，没有场景检查设置文件在 Linux 上的位置：`$XDG_DATA_HOME/wordcount/settings.json`，或未设置 `XDG_DATA_HOME` 时的 `~/.local/share/wordcount/settings.json`（Q17）。在 Troy 的电脑上，该命令只使用 `APPDATA`，v0.3-S35 检查它在那里忽略 `XDG_DATA_HOME`。F08 的功能测试在 CI 中检查 Linux 上的路径。

没有场景在未设置 `APPDATA` 时运行。架构第 6 节把这种情况定为设置错误，但没有需求或已批准的设计定下此时错误或警告的内容，因为没有可指明的设置文件。由 F08 的设计决定，并由它的功能测试检查所决定的行为。

v0.3-S15、v0.3-S25、v0.3-S38 和 v0.3-S48 使用 Windows PowerShell 5.1，即 `powershell.exe`，因为每台 Windows 11 都有它。没有场景运行 PowerShell 7，即 `pwsh`。两种 shell 启动的是同一个 `wordcount.exe`，所以 Claude 的其他每个场景对两者都成立。

在 v0.3-S16 中，`Set-Content` 写入 `你好 世界\r\n第二 行\r\n`，共 13 个字符，其中没有 `.`、`!` 或 `?`。Windows PowerShell 5.1 还会在开头写一个字节顺序标记，PowerShell 7 不会。该标记不计入字符数（Q12），不属于任何词（Q5），统计句子时也被忽略，所以 Troy 在两种 shell 中都看到 `13`、`2` 和 `0`。第 7 步保存 `--longest`，所以无论 Troy 的设置文件之前保存了什么选项，第 8 步都打印 `2`。v0.3-S16 是唯一写入 Troy 真正数据文件夹中设置文件的场景，Troy 运行的每次计数也都会这样写入。

没有场景检查放在文件之后的选项，比如 `wordcount notes.txt --lines`，也没有场景检查缩写的选项，比如 `--line`。需求只给出 `wordcount --lines FILE` 这一种形式。已批准的 F05、F06 和 F07 设计规定选项可以放在文件之后、缩写的选项算错误的命令行，并由它们的功能测试检查这两点。F08 和 F09 的设计为 `--again` 和 `--sentences` 决定同样的问题，并由它们的功能测试检查所决定的行为。

## 3. 性能和压力用例

无。需求第 7.1 节没有设任何性能指标，所以 v0.3 没有性能或压力用例（R14）。

## 4. 设备

| 设备 | 操作系统 | 由谁运行 |
| --- | --- | --- |
| Troy 的电脑 | Windows 11，conda 环境 `troy-mode-trial` 中的 Python 3.13，以及 Windows PowerShell 5.1 | Claude |
| Troy 的电脑，在 Windows Terminal 里 | Windows 11 | Troy |

Claude 运行的场景只在 Troy 电脑上的发布测试中运行，从不在 CI 中运行，所以 GitHub Actions 运行器不是这些场景的设备。Claude 的每个场景都用自己的数据文件夹运行 `wordcount` 命令，而脚本可以在 Troy 的电脑上启动该命令并读取其输出。v0.3-S16 由 Troy 运行：它检查 Windows Terminal 本身显示的内容，这是脚本读不到的；它还检查 Troy 真正数据文件夹中的设置文件，这是 Claude 的场景不得触碰的。

## 5. 验收记录

无。Troy 尚未验收 v0.3。

## 6. 修改记录

| 版本 | 日期 | 修改 |
| --- | --- | --- |
| 0.1 | 2026-11-23 | 初稿，覆盖 F05 和 F06。 |
| 0.2 | 2026-11-25 | 根据需求 7.0 加入 F07，即 `--longest` 选项：新场景 v0.3-S17 到 v0.3-S25，并在 v0.3-S16 中加一个 `--longest` 步骤。方案现在依据已批准的 F05 和 F06 设计。v0.3-S01 到 v0.3-S15 不变。 |
| 0.3 | 2026-11-26 | 根据需求 8.0 和架构 4.0 加入 F08，即 `--again` 选项，以及 F09，即 `--sentences` 选项：每个测试使用自己的数据文件夹，为 F08 新增场景 v0.3-S26 到 v0.3-S38，为 F09 新增场景 v0.3-S39 到 v0.3-S48，并在 v0.3-S16 中加入 `--again`、`--sentences` 和设置文件的步骤。方案现在也依据已批准的 F07 设计。其他场景不变。 |
