---
troy-doc: "F05-test-plan"
lang: "zh-CN"
version: "0.1"
updated: "2026-11-23"
status: "草稿，正在与接口设计师对齐。"
mirror-of: "test-plan.md"
---

# F05 行数选项：测试方案

## 1. 功能

- 编号和名称：F05 行数选项
- 设计：[design.zh-CN.md](design.zh-CN.md)

## 2. 用例

F05 改动两个外部接口，用例按各自调用方的方式调用它们。

- **`main`。** F05-T01 到 F05-T18 在测试自己的进程里调用它：`from troy_mode_trial.cli import main`。它们用 pytest 的 `capsys` 读取标准输出和标准错误，并用 `monkeypatch.chdir` 把测试的 `tmp_path` 设为工作目录，用例另有说明的除外。通过 `capsys`，换行符在两个系统上都是 `\n`。
- **`wordcount`。** F05-T19 到 F05-T24 以新进程启动已安装的程序，不经过 shell，工作目录设为 `tmp_path`，以字节形式捕获标准输出和标准错误。测试按 F04 用例的方式查找程序：在运行测试的 Python 的脚本目录 `sysconfig.get_path("scripts")` 中用 `shutil.which("wordcount", path=...)` 查找。程序不在那里时测试失败，绝不跳过。这些用例中的 `<NL>` 是字节形式的 `os.linesep`：Linux 上是 `\n`，Windows 上是 `\r\n`。

每个测试在 `tmp_path` 里自建文件，并以二进制方式写入用例给出的确切字节。用例未另作说明时，`notes.txt` 内容为 `Hello world\n  troy-mode  trial\n`，即设计中的示例，共 2 行、4 个词。`windows.txt` 内容为 `Hello world\r\n  troy-mode  trial\r\n`。`latin1.txt` 内容为 Latin-1 编码的 `café au lait\n`，其字节以 `63 61 66 E9 20` 开头。`sub` 是 `tmp_path` 中的一个空文件夹。文件内容或文件名中的非 ASCII 字符用 UTF-8。测试套件在 Windows 11 和 Linux 上运行。用例未指明系统时，在两个系统上预期相同的结果。

“恰好是”指完整的文字：例如，标准错误恰好是 `wordcount: missing.txt: no such file\n`，指只有这一行，别无其他。

**用法行取决于 F06 的代码是否已合入。** F06 与 F05 同时开发，设计 2.1 的合入顺序一段给出了两种顺序下的用法行。本方案中的 `<USAGE>` 是：

- 被测分支上还没有 F06 的代码、因而 `--chars` 是未知选项时，为 `usage: wordcount [--lines] FILE`。
- 该分支上已有 F06 的代码时，为 `usage: wordcount [--lines | --chars] FILE`。

检查用法行的用例先通过它所测的同一个接口询问命令处于哪种状态，并丢弃这次调用的输出。`main` 用例调用 `main(["--chars", "notes.txt"])`：返回 `0` 表示 F06 的代码已合入；抛出 `code` 为 `2` 的 `SystemExit` 表示尚未合入。`wordcount` 用例以同样方式运行 `wordcount --chars notes.txt`：退出码 0 表示已合入，退出码 2 表示尚未合入。用例随后预期该状态下的确切用法行。这样，每个用例在两种合入顺序下都保持精确。固定一行行不通：F05 验收后，它的测试在每个 PR 中都必须通过（R10），而如果 F06 的代码后合入，F06 的实现 PR 会改变用法行，却不得修改测试（R08）。

“用法错误”指：`main` 抛出 `code` 为 `2` 的 `SystemExit`，或程序以退出码 2 退出，且标准输出为空，标准错误恰好有两行，第一行恰好是 `<USAGE>`，第二行以 `wordcount: error: ` 开头。

F05 的模拟实现让 `main` 与当时 main 分支上的完全一样，所以命令还没有 `--lines` 选项。在模拟实现上，每个用例都因 `--lines` 尚未实现而失败，没有一个因导入或构建错误而失败（R09）。用例不需要 main 分支上没有的名称，`wordcount` 也已由 F04 安装。每个计数用例和文件错误用例得到用法错误而不是其结果，因为模拟实现把 `--lines` 当作无法识别的参数。每个用法错误用例得到的第一行不含 `--lines`，是 `usage: wordcount FILE` 或 `usage: wordcount [--chars] FILE`，与 `<USAGE>` 不同。每个 `wordcount` 用例得到退出码 2 和用法行，而不是其输出。

| 编号 | 层级 | 接口 | 测什么 | 准备和输入 | 预期结果 |
| --- | --- | --- | --- | --- | --- |
| F05-T01 | 功能 | `main` | 设计中的示例：标准输出为行数和一个换行符，返回码 0。 | `main(["--lines", "notes.txt"])`。 | 返回 `0`，且结果的类型恰好是 `int`。标准输出恰好是 `2\n`。标准错误为空。 |
| F05-T02 | 功能 | `main` | 选项可以放在文件之后，给两次也只计一次。 | 三次调用：`main(["notes.txt", "--lines"])`、`main(["--lines", "--lines", "notes.txt"])` 和 `main(["notes.txt", "--lines", "--lines"])`。 | 每次调用都返回 `0`，向标准输出恰好写入 `2\n`，标准错误为空。 |
| F05-T03 | 功能 | `main` | 命令按 F02 的方式数行：`\n`、`\r\n` 和 `\r` 各结束一行，没有换行符的最后一行也算，其他字符都不结束一行。 | 九个文件，内容如下：`one-break.txt` 为 `\n`；`no-end.txt` 为 `Hello world\n  troy-mode  trial`；`windows.txt`；`blank.txt` 为 `first\n\nthird\n`；`mixed.txt` 为 `one\rtwo\r\nthree\nfour`；`cr-crlf.txt` 为 `\r\r\n`；`lf-cr.txt` 为 `\n\r`；`other-breaks.txt` 为 `a b\fc\x85d`，其中 `\x85` 是 U+0085；`unicode-breaks.txt` 为 `a\vb c d`。对每个文件各调用一次 `main(["--lines", <文件名>])`。 | 每次调用都返回 `0`，标准错误为空。标准输出按文件顺序依次恰好是 `1\n`、`2\n`、`2\n`、`3\n`、`4\n`、`2\n`、`2\n`、`1\n` 和 `1\n`。 |
| F05-T04 | 单元 | `main` | 空文件有 0 行，开头的一个字节顺序标记被忽略。 | 三个文件：`empty.txt` 为空，`bom-only.txt` 的字节为 `EF BB BF`，`bom.txt` 为 `EF BB BF` 后接 `a\nb`。对每个文件各调用一次 `main(["--lines", <文件名>])`。 | 每次调用都返回 `0`，标准错误为空。标准输出依次恰好是 `0\n`、`0\n` 和 `2\n`。 |
| F05-T05 | 单元 | `main` | 计数是普通的十进制数，没有符号、填充或分隔符。 | `many.txt` 内容为 12,345 个 `\n`。`main(["--lines", "many.txt"])`。 | 返回 `0`。标准输出恰好是 `12345\n`。 |
| F05-T06 | 单元 | `main` | `FILE` 可以是设计允许的任何路径形式，`--` 之后的文字 `--lines` 是文件名。 | `tmp_path` 中有 `notes.txt`，以及它的副本 `sub/notes.txt`、`my notes.txt`、`日本語.txt`、`-notes.txt` 和 `--lines`。六次调用，除第一次外工作目录都是 `tmp_path`：在工作目录 `sub` 中调用 `main(["--lines", <notes.txt 的绝对路径>])`；`main(["--lines", "sub/notes.txt"])`；`main(["--lines", "my notes.txt"])`；`main(["--lines", "日本語.txt"])`；`main(["--lines", "--", "-notes.txt"])`；`main(["--lines", "--", "--lines"])`。然后第七次调用 `main(["--", "--lines"])`。 | 前六次调用都返回 `0`，向标准输出恰好写入 `2\n`，标准错误为空。第七次返回 `0` 并恰好写入 `4\n`：它统计名为 `--lines` 的文件的词数。 |
| F05-T07 | 功能 | `main` | 设计和原型中文件不存在的示例：消息和返回码与不带选项时相同。 | 空的工作目录。先 `main(["--lines", "missing.txt"])`，再 `main(["missing.txt"])`。 | 两次都返回 `2`，标准输出为空。两次的标准错误都恰好是 `wordcount: missing.txt: no such file\n`。 |
| F05-T08 | 单元 | `main` | 带 `--lines` 时，每种“文件不存在”的情况都得到这个原因，且消息中是输入时的参数。 | `notes.txt` 和文件夹 `sub` 存在。五次调用：`main(["--lines", ""])`、`main(["--lines", "missing-folder/notes.txt"])`、`main(["--lines", "notes.txt/inner.txt"])`（把文件当文件夹用）、`main(["--lines", "缺失.txt"])` 和 `main(["missing.txt", "--lines"])`。 | 每次都返回 `2`，标准输出为空。标准错误依次恰好是 `wordcount: : no such file\n`、`wordcount: missing-folder/notes.txt: no such file\n`、`wordcount: notes.txt/inner.txt: no such file\n`、`wordcount: 缺失.txt: no such file\n` 和 `wordcount: missing.txt: no such file\n`。 |
| F05-T09 | 功能 | `main` | 内容不是合法 UTF-8 的文件得到原因 `not valid UTF-8`，无效字节出现在几行合法文字之后也是如此。 | `latin1.txt`；字节为 `6F 6B 20 FF FE` 的 `broken.txt`；以及内容为 `one\ntwo\n` 后接字节 `FF` 的 `late.txt`。对每个文件各调用一次 `main(["--lines", <文件名>])`。 | 每次都返回 `2`，标准输出为空，即不输出任何计数。标准错误依次恰好是 `wordcount: latin1.txt: not valid UTF-8\n`、`wordcount: broken.txt: not valid UTF-8\n` 和 `wordcount: late.txt: not valid UTF-8\n`。 |
| F05-T10 | 功能 | `main` | 文件夹在两个系统上都得到原因 `is a folder`。 | `main(["--lines", "sub"])` 和 `main(["--lines", "."])`。在 Windows 和 Linux 上都运行。 | 每次都返回 `2`，标准输出为空。标准错误依次恰好是 `wordcount: sub: is a folder\n` 和 `wordcount: .: is a folder\n`。 |
| F05-T11 | 功能 | `main` | 进程无权读取的文件得到原因 `permission denied`。 | 仅限 Linux：`secret.txt` 内容为 `one\ntwo\n`，权限设为 `0o000`。`main(["--lines", "secret.txt"])`。在 Windows 上跳过，因为在 Windows 上测试无法可移植地去掉自己的读权限；进程以 root 运行时也跳过，因为 root 仍能读取该文件。测试结束后恢复权限。 | 返回 `2`。标准输出为空。标准错误恰好是 `wordcount: secret.txt: permission denied\n`。 |
| F05-T12 | 单元 | `main` | 打开文件时的其他任何错误都得到原因 `cannot read file`。 | 一个由 300 个 `a` 加 `.txt` 组成的文件名，比两个系统允许的单个名称都长。仅在 Windows 上另加 `a?b.txt`，这是 Windows 不允许的名称。对每个名称各调用一次 `main(["--lines", <名称>])`。 | 每次都返回 `2`，标准输出为空。标准错误恰好是 `wordcount: <名称>: cannot read file\n`，其中 `<名称>` 是给出的参数原样。 |
| F05-T13 | 功能 | `main` | `--lines` 与 `--chars` 同时出现是用法错误，无论顺序和位置，且先于缺少 `FILE` 的检查：设计中的方案 2，以及 F06 代码尚未合入时设计合入顺序一段的说法。 | `notes.txt` 存在。按第 2 节的方式确定状态。四次调用：(a) `main(["--lines", "--chars", "notes.txt"])`，(b) `main(["--chars", "--lines", "notes.txt"])`，(c) `main(["--lines", "notes.txt", "--chars"])`，(d) `main(["--lines", "--chars"])`。 | 每次都是用法错误，标准输出中没有计数。标准错误的第二行恰好是：F06 代码已合入时，(a)、(c)、(d) 为 `wordcount: error: argument --chars: not allowed with argument --lines`，(b) 为 `wordcount: error: argument --lines: not allowed with argument --chars`；尚未合入时，(a)、(b)、(c) 为 `wordcount: error: unrecognized arguments: --chars`，(d) 为 `wordcount: error: the following arguments are required: FILE`。 |
| F05-T14 | 单元 | `main` | 带 `--lines` 的其他错误命令行都是用法错误，不是计数、文件错误或帮助文字。 | `notes.txt` 存在。按第 2 节的方式确定状态。七次调用：`main(["--lines"])`、`main(["-l", "notes.txt"])`、`main(["--line", "notes.txt"])`、`main(["--li", "notes.txt"])`、`main(["--lines", "-h", "notes.txt"])`、`main(["--lines", "notes.txt", "notes.txt"])` 和 `main(["--lines=x", "notes.txt"])`。 | 在两种状态下每次都是用法错误。前六次调用的标准错误第二行依次恰好是：`wordcount: error: the following arguments are required: FILE`、`wordcount: error: unrecognized arguments: -l`、`wordcount: error: unrecognized arguments: --line`、`wordcount: error: unrecognized arguments: --li`、`wordcount: error: unrecognized arguments: -h` 和 `wordcount: error: unrecognized arguments: notes.txt`。`--lines=x` 的第二行只需以 `wordcount: error: ` 开头。没有一次调用写出计数、帮助文字或 `wordcount: notes.txt: <原因>` 这样的行。 |
| F05-T15 | 单元 | `main` | 每个用法错误，无论是否带 `--lines`，都显示新的用法行，且无论 `sys.argv[0]` 是什么，程序名都是 `wordcount`。 | `monkeypatch.setattr(sys, "argv", ["other-name.py"])`。按第 2 节的方式确定状态。先调用 `main([])`，再调用 `main(["--lines", "missing.txt"])`。 | 第一次是用法错误：第一行恰好是 `<USAGE>`，第二行恰好是 `wordcount: error: the following arguments are required: FILE`。第二次返回 `2`，并向标准错误恰好写入 `wordcount: missing.txt: no such file\n`。 |
| F05-T16 | 单元 | `main` | 不带参数时，`main` 读取 `sys.argv[1:]`，与控制台脚本一致。 | `monkeypatch.setattr(sys, "argv", ["wordcount", "--lines", "notes.txt"])`。调用 `main()`，也调用 `main(None)`。 | 每次都返回 `0`，并向标准输出恰好写入 `2\n`。 |
| F05-T17 | 单元 | `main` | `argv` 可以是任何 `str` 序列，不只是列表。 | `main(("--lines", "notes.txt"))`，一个元组。 | 返回 `0`，并向标准输出恰好写入 `2\n`。 |
| F05-T18 | 单元 | `main` | `main` 在两次调用之间不保留状态，不写任何文件，不带选项时仍统计词数。 | `notes.txt` 和 `latin1.txt` 存在。记录 `tmp_path` 中每个文件的名称和字节、工作目录以及 `sys.argv`。在同一进程中依次以 `["--lines", "notes.txt"]`、`["notes.txt"]`、`["--lines", "missing.txt"]`、`["--lines", "latin1.txt"]`、`["notes.txt"]` 和 `["--lines", "notes.txt"]` 调用 `main`，每次调用后读取输出。 | 各次调用依次返回 `0`、`0`、`2`、`2`、`0` 和 `0`。每次调用的输出只有它自己的：`2\n`；`4\n`；`wordcount: missing.txt: no such file\n`；`wordcount: latin1.txt: not valid UTF-8\n`；`4\n`；`2\n`。之后 `tmp_path` 中的文件和字节不变，工作目录和 `sys.argv` 也不变。 |
| F05-T19 | 集成 | `wordcount` | 已安装的程序带选项时统计行数，不带时统计词数，与 F05 原型一致。 | 先运行 `wordcount --lines notes.txt`，再运行 `wordcount notes.txt`。 | 两次都以退出码 0 退出，标准错误为空。标准输出先恰好是 `2<NL>`，再恰好是 `4<NL>`。 |
| F05-T20 | 集成 | `wordcount` | 已安装的程序接受放在文件之后的选项，并把每个 Windows 行尾算作一个换行，与设计中的示例一致。 | 先运行 `wordcount notes.txt --lines`，再运行 `wordcount --lines windows.txt`。 | 两次都以退出码 0 退出，向标准输出恰好写入 `2<NL>`，标准错误为空。 |
| F05-T21 | 集成 | `wordcount` | 已安装的程序以退出码 2 报告文件不存在，与 F05 原型一致。 | 空的工作目录。运行 `wordcount --lines missing.txt`。 | 退出码 2。标准输出为空。标准错误恰好是 `wordcount: missing.txt: no such file<NL>`。 |
| F05-T22 | 集成 | `wordcount` | 已安装的程序在两个系统上都以退出码 2 报告不是合法 UTF-8 的文件和文件夹。 | 先运行 `wordcount --lines latin1.txt`，再运行 `wordcount --lines sub`。 | 两次都以退出码 2 退出，标准输出为空。标准错误先恰好是 `wordcount: latin1.txt: not valid UTF-8<NL>`，再恰好是 `wordcount: sub: is a folder<NL>`。 |
| F05-T23 | 集成 | `wordcount` | 错误的命令行以退出码 2 和该状态下的用法行退出，从而与文件错误区分开。 | `notes.txt` 存在。按第 2 节的方式确定状态。三次运行：`wordcount --lines --chars notes.txt`、`wordcount -l notes.txt` 和 `wordcount --lines`。 | 每次都是用法错误，退出码 2。标准错误恰好有两行，每行后接 `<NL>`：第一行是 `<USAGE>`；第二行对三次运行依次是：F06 代码已合入时为 `wordcount: error: argument --chars: not allowed with argument --lines`，尚未合入时为 `wordcount: error: unrecognized arguments: --chars`；`wordcount: error: unrecognized arguments: -l`；`wordcount: error: the following arguments are required: FILE`。 |
| F05-T24 | 集成 | `wordcount` | 参数按 Troy 输入的样子到达程序。 | `notes.txt` 的副本 `my notes.txt`、`日本語.txt` 和 `-notes.txt`。四次运行：在工作目录 `sub` 中运行 `wordcount --lines <notes.txt 的绝对路径>`；`wordcount --lines "my notes.txt"`，一个含空格的参数；`wordcount --lines 日本語.txt`；`wordcount --lines -- -notes.txt`。 | 每次都以退出码 0 退出，向标准输出恰好写入 `2<NL>`，标准错误为空。 |

## 3. 性能用例

无。设计 2.1 和 2.2 没有设定性能指标，需求 7.1 也没有为项目设定任何性能指标（R14）。

## 4. 不测试的内容

| 内容 | 原因 |
| --- | --- |
| `wordcount --chars FILE` 的计数和错误。 | 由 F06 的设计定义，由 F06 的测试方案检查。F05 只用 `--chars` 确定第 2 节的状态，并检查它不能与 `--lines` 同时出现。 |
| 不带选项的 `wordcount FILE` 的全部行为。 | F04 的用例检查它，并且它们在每个 PR 中都必须通过（R10）。F05-T18 和 F05-T19 再次检查在 `--lines` 旁边仍会统计词数。 |
| F04 和 F06 的测试方案所预期的用法行。 | 设计第 3 节列出了它们。F06 的测试方案 PR 修改 F04 的方案，F06 自己的方案归该团队负责。本方案不修改它们。 |
| `--lines=VALUE` 的确切消息。 | 设计把它交给 argparse 自己的措辞，只规定它是用法错误。F05-T14 检查这一点。 |
| 程序缺陷：文件错误以外的异常传给调用方，Python 写出回溯信息，程序以退出码 1 退出。 | 通过 `main` 或 `wordcount` 的任何输入都不会让计数抛出其他异常。要引发这样的异常，就得替换 cli 内部的计数函数，这测的是内部细节，不是外部接口。而且这样的测试在模拟实现上也会通过，这违反 R09。 |
| Windows 上无法读取的文件引发的 `PermissionError`。 | 在 Windows 上去掉文件的读权限需要访问控制列表，可移植的测试无法可靠地设置和恢复它。F05-T11 在 Linux 上检查同一个原因，F05-T10 检查 Windows 上文件夹引发的 `PermissionError`。 |
| 命令退出前关闭了文件。 | `main` 只通过 `count_lines` 读取文件，F02 的用例检查它会关闭文件。F05-T18 检查命令不写任何文件。 |
| 输出用的是 `write` 而不是 `print()`。 | 两者写出的文字相同，调用方无法区分。由 ruff 的 T20 规则保证（架构第 8 节）。 |
| `argv` 中不是 `str` 的元素，以及含字符 U+0000 的路径。 | 设计 2.2 只允许 `str` 元素，其他类型不在约定之内。任何 shell 都无法在参数中传入 U+0000，所以 `wordcount` 永远收不到它。 |
| Windows 上 `wordcount` 向管道写出时，标准错误中非 ASCII 文件名的字节。 | 这时 Python 按系统代码页编码标准错误，字节因机器而异。F05-T08 通过 `main` 检查这类消息的文字，F05-T24 检查这类文件名能到达程序并被统计。 |
| PowerShell 找到 `wordcount`、`$LASTEXITCODE`、PowerShell 去掉引号的方式，以及 F05 合入后需要重新安装项目。 | CI 在 Linux 上运行，没有 PowerShell。v0.3 版本测试方案在 Troy 的电脑上用 Windows PowerShell 运行该命令。F05-T24 检查带引号的参数作为一个参数到达程序。 |
| 性能。 | 没有性能指标（R14）。 |

## 5. 与接口设计师的对齐记录

无。设计已回答本方案提出的所有问题。设计的合入顺序一段给出了两种顺序下的用法行和 `--chars` 的含义，所以第 2 节检查分支所处状态下的那一行。设计第 4 节中架构师的说明要求：F05 和 F06 中后合入测试 PR 的一方更新预期的用法行。对 F04 的用例，F06 的测试方案 PR 现在只检查用法行的开头，所以 F05 的任何 PR 都不修改它们。对 F05 自己的用例，第 2 节的状态检查在两种顺序下都给出正确的那一行，所以之后的 PR 都不需要修改它们。

## 6. 修改记录

| 版本 | 日期 | 修改 |
| --- | --- | --- |
| 0.1 | 2026-11-23 | 初稿。 |
