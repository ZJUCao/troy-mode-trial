---
troy-doc: "F04-test-plan"
lang: "zh-CN"
version: "1.0"
updated: "2026-11-15"
status: "Troy 已于 2026-11-15 批准"
mirror-of: "test-plan.md"
---

# F04 字数统计命令：测试方案

## 1. 功能

- 编号和名称：F04 字数统计命令
- 设计：[design.zh-CN.md](design.zh-CN.md)

## 2. 用例

F04 有两个外部接口，用例按各自调用方的方式调用它们。

- **`main`。** F04-T01 到 F04-T16 在测试自己的进程里调用它：`from troy_mode_trial.cli import main`。它们用 pytest 的 `capsys` 读取标准输出和标准错误，并用 `monkeypatch.chdir` 把测试的 `tmp_path` 设为工作目录，用例另有说明的除外。通过 `capsys`，换行符在两个系统上都是 `\n`。
- **`wordcount`。** F04-T17 到 F04-T22 以新进程启动已安装的程序，不经过 shell，工作目录设为 `tmp_path`，以字节形式捕获标准输出和标准错误。测试在运行测试的 Python 的脚本目录 `sysconfig.get_path("scripts")` 中用 `shutil.which("wordcount", path=...)` 查找程序，这在 Windows 上也能找到 `wordcount.exe`。程序不在那里时测试失败，绝不跳过。这些用例中的 `<NL>` 是字节形式的 `os.linesep`：Linux 上是 `\n`，Windows 上是 `\r\n`，与设计 2.1 一致。

每个测试在 `tmp_path` 里自建文件，并以二进制方式写入用例给出的确切字节。用例未另作说明时，`notes.txt` 内容为 `Hello world\n  troy-mode  trial`，末尾没有换行符，即设计中的示例，共 4 个词。`latin1.txt` 内容为 Latin-1 编码的 `café au lait\n`，其字节以 `63 61 66 E9 20` 开头。`sub` 是 `tmp_path` 中的一个空文件夹。文件内容或文件名中的非 ASCII 字符用 UTF-8。测试套件在 Windows 11 和 Linux 上运行。用例未指明系统时，在两个系统上预期相同的结果。

“恰好是”指完整的文字：例如，标准错误恰好是 `wordcount: missing.txt: no such file\n`，指只有这一行，别无其他。“用法错误”指：`main` 抛出 `code` 为 `2` 的 `SystemExit`，或程序以退出码 2 退出，且标准输出为空，标准错误恰好有两行，第一行恰好是 `usage: wordcount FILE`，第二行以 `wordcount: error: ` 开头。

在模拟实现上，每个用例都因命令尚未实现而失败。这里假定模拟的 `main` 抛出 `NotImplementedError`，并且模拟 PR 已在 `[project.scripts]` 中声明 `wordcount = "troy_mode_trial.cli:main"`，使 CI 的安装生成该程序。于是每个 `main` 用例得到 `NotImplementedError` 而不是其结果，每个 `wordcount` 用例得到退出码 1 和回溯信息而不是其输出（R09）。如果模拟 PR 没有声明该程序，`wordcount` 用例会因程序不存在而失败，R09 不接受这种失败，所以测试工程师在测试 PR 之前报告此事。

| 编号 | 层级 | 接口 | 测什么 | 准备和输入 | 预期结果 |
| --- | --- | --- | --- | --- | --- |
| F04-T01 | 功能 | `main` | 设计中的示例：标准输出为计数和一个换行符，返回码 0。 | `main(["notes.txt"])`。 | 返回 `0`，且结果的类型恰好是 `int`。标准输出恰好是 `4\n`。标准错误为空。 |
| F04-T02 | 功能 | `main` | 命令按 F03 的方式计数。 | 三个文件：`dashes.txt` 内容为 `Wait -- what ... don't x--y 3.14 _`，`only-symbols.txt` 内容为 `-- ... !!!`，`empty.txt` 为空。对每个文件名各调用一次 `main`。 | 每次调用都返回 `0`，标准错误为空。标准输出依次恰好是 `5\n`、`0\n` 和 `0\n`。 |
| F04-T03 | 单元 | `main` | 计数是普通的十进制数，没有符号、填充或分隔符。 | `many.txt` 内容为 12,345 个 `a `。`main(["many.txt"])`。 | 返回 `0`。标准输出恰好是 `12345\n`。 |
| F04-T04 | 单元 | `main` | `FILE` 可以是设计允许的任何路径形式。 | `tmp_path` 中有 `notes.txt`，以及它的副本 `sub/notes.txt`、`my notes.txt`、`日本語.txt` 和 `-notes.txt`。五次调用，除第一次外工作目录都是 `tmp_path`：在工作目录 `sub` 中调用 `main([<notes.txt 的绝对路径>])`；`main(["sub/notes.txt"])`；`main(["my notes.txt"])`；`main(["日本語.txt"])`；`main(["--", "-notes.txt"])`。 | 每次调用都返回 `0`，向标准输出恰好写入 `4\n`，标准错误为空。 |
| F04-T05 | 功能 | `main` | 设计中文件不存在的示例。 | 空的工作目录。`main(["missing.txt"])`。 | 返回 `2`。标准输出为空。标准错误恰好是 `wordcount: missing.txt: no such file\n`。 |
| F04-T06 | 单元 | `main` | 每种“文件不存在”的情况都得到这个原因，且消息中是输入时的参数，而不是解析后的路径或绝对路径。 | `notes.txt` 和文件夹 `sub` 存在。五次调用：`main([""])`、`main(["missing-folder/notes.txt"])`、`main(["notes.txt/inner.txt"])`（把文件当文件夹用）、`main(["sub/../missing.txt"])` 和 `main(["缺失.txt"])`。 | 每次都返回 `2`，标准输出为空。标准错误依次恰好是 `wordcount: : no such file\n`、`wordcount: missing-folder/notes.txt: no such file\n`、`wordcount: notes.txt/inner.txt: no such file\n`、`wordcount: sub/../missing.txt: no such file\n` 和 `wordcount: 缺失.txt: no such file\n`。 |
| F04-T07 | 功能 | `main` | 内容不是合法 UTF-8 的文件得到原因 `not valid UTF-8`。 | `latin1.txt`，以及字节为 `6F 6B 20 FF FE` 的 `broken.txt`。对每个文件名各调用一次 `main`。 | 每次都返回 `2`，标准输出为空。标准错误依次恰好是 `wordcount: latin1.txt: not valid UTF-8\n` 和 `wordcount: broken.txt: not valid UTF-8\n`。 |
| F04-T08 | 功能 | `main` | 文件夹在两个系统上都得到原因 `is a folder`，尽管 Python 在两个系统上抛出的错误不同。 | `main(["sub"])` 和 `main(["."])`。在 Windows 和 Linux 上都运行。 | 每次都返回 `2`，标准输出为空。标准错误依次恰好是 `wordcount: sub: is a folder\n` 和 `wordcount: .: is a folder\n`。 |
| F04-T09 | 功能 | `main` | 进程无权读取的文件得到原因 `permission denied`。 | 仅限 Linux：`secret.txt` 内容为 `one two`，权限设为 `0o000`。`main(["secret.txt"])`。在 Windows 上跳过，因为在 Windows 上测试无法可移植地去掉自己的读权限；进程以 root 运行时也跳过，因为 root 仍能读取该文件。测试结束后恢复权限。 | 返回 `2`。标准输出为空。标准错误恰好是 `wordcount: secret.txt: permission denied\n`。 |
| F04-T10 | 单元 | `main` | 打开文件时的其他任何错误都得到原因 `cannot read file`。 | 由 300 个 `a` 后接 `.txt` 组成的文件名，超过两个系统对单个名称允许的长度。仅在 Windows 上另加 `a?b.txt`，这是 Windows 不允许的名称。对每个名称各调用一次 `main`。 | 每次都返回 `2`，标准输出为空。标准错误恰好是 `wordcount: <name>: cannot read file\n`，其中 `<name>` 是传入的参数原样。 |
| F04-T11 | 功能 | `main` | 设计中缺少参数的示例。 | `main([])`。 | 用法错误。标准错误的第二行恰好是 `wordcount: error: the following arguments are required: FILE`。 |
| F04-T12 | 单元 | `main` | 其他每种错误的命令行都是用法错误，而不是计数、文件错误或帮助文字。 | `notes.txt` 存在，`missing.txt` 和 `other.txt` 不存在。六次调用：`main(["notes.txt", "notes.txt"])`、`main(["missing.txt", "other.txt"])`、`main(["-h"])`、`main(["--help"])`、`main(["-x", "notes.txt"])` 和 `main(["--"])`。 | 每次都是用法错误。第一次调用时，标准错误的第二行恰好是 `wordcount: error: unrecognized arguments: notes.txt`。没有一次调用写出帮助文字或 `wordcount: <FILE>: <reason>` 这样的行。 |
| F04-T13 | 单元 | `main` | 不论 `sys.argv[0]` 是什么，每条消息中的程序名都是 `wordcount`。 | `monkeypatch.setattr(sys, "argv", ["other-name.py"])`。先调用 `main([])`，再调用 `main(["missing.txt"])`。 | 第一次是用法错误，第一行恰好是 `usage: wordcount FILE`。第二次返回 `2`，向标准错误恰好写入 `wordcount: missing.txt: no such file\n`。 |
| F04-T14 | 单元 | `main` | 不传参数时，`main` 读取 `sys.argv[1:]`，与控制台脚本的做法相同。 | `monkeypatch.setattr(sys, "argv", ["wordcount", "notes.txt"])`。调用 `main()`，也调用 `main(None)`。 | 每次都返回 `0`，向标准输出恰好写入 `4\n`。 |
| F04-T15 | 单元 | `main` | `argv` 可以是任何 `str` 序列，不只是列表。 | `main(("notes.txt",))`，即一个元组。 | 返回 `0`，向标准输出恰好写入 `4\n`。 |
| F04-T16 | 单元 | `main` | `main` 在两次调用之间不保留状态，也不写任何文件。 | `notes.txt` 和 `latin1.txt` 存在。记下 `tmp_path` 中每个文件的名称和字节、工作目录以及 `sys.argv`。在同一进程中依次用 `["notes.txt"]`、`["missing.txt"]`、`["latin1.txt"]` 和 `["notes.txt"]` 调用 `main`，每次调用后读取输出。 | 各次调用依次返回 `0`、`2`、`2` 和 `0`。每次调用的输出只有它自己的：`4\n`；`wordcount: missing.txt: no such file\n`；`wordcount: latin1.txt: not valid UTF-8\n`；`4\n`。之后 `tmp_path` 中的文件和字节不变，工作目录和 `sys.argv` 也不变。 |
| F04-T17 | 集成 | `wordcount` | 已安装的程序统计一个文件，与 F04 原型一致。 | 运行 `wordcount notes.txt`。 | 退出码 0。标准输出恰好是 `4<NL>`。标准错误为空。 |
| F04-T18 | 集成 | `wordcount` | 已安装的程序以退出码 2 报告文件不存在。 | 空的工作目录。运行 `wordcount missing.txt`。 | 退出码 2。标准输出为空。标准错误恰好是 `wordcount: missing.txt: no such file<NL>`。 |
| F04-T19 | 集成 | `wordcount` | 已安装的程序以退出码 2 报告内容不是合法 UTF-8 的文件。 | 运行 `wordcount latin1.txt`。 | 退出码 2。标准输出为空。标准错误恰好是 `wordcount: latin1.txt: not valid UTF-8<NL>`。 |
| F04-T20 | 集成 | `wordcount` | 已安装的程序在两个系统上都以退出码 2 报告文件夹。 | 运行 `wordcount sub`。 | 退出码 2。标准输出为空。标准错误恰好是 `wordcount: sub: is a folder<NL>`。 |
| F04-T21 | 集成 | `wordcount` | 错误的命令行以退出码 2 和用法行退出，由此与文件错误区分。 | 三次运行：不带参数的 `wordcount`、`wordcount notes.txt notes.txt` 和 `wordcount -h`。 | 每次都是用法错误，退出码 2。标准错误中没有以 `wordcount: notes.txt: ` 开头的行。 |
| F04-T22 | 集成 | `wordcount` | 参数按 Troy 输入的样子到达程序。 | `notes.txt` 的副本 `my notes.txt`、`日本語.txt` 和 `-notes.txt`。四次运行：在工作目录 `sub` 中运行 `wordcount <notes.txt 的绝对路径>`；`wordcount "my notes.txt"`，即一个含空格的参数；`wordcount 日本語.txt`；`wordcount -- -notes.txt`。 | 每次都以退出码 0 退出，向标准输出恰好写入 `4<NL>`，标准错误为空。 |

## 3. 性能用例

无。设计 2.1 和 2.2 没有设性能指标，需求 7.1 也没有给项目设任何性能指标（R14）。

## 4. 不测的内容

| 内容 | 原因 |
| --- | --- |
| 程序缺陷：文件错误以外的异常传给调用方，Python 写出回溯信息，程序以退出码 1 退出。Ctrl+C 也不捕获。 | 通过 `main` 或 `wordcount` 的任何输入都不会让计数抛出其他异常。要引发这样的异常，就得替换 cli 内部的计数函数，这测的是内部细节，不是外部接口。而且这样的测试在模拟实现上也会通过，这违反 R09。 |
| Windows 上无法读取的文件引发的 `PermissionError`。 | 在 Windows 上去掉文件的读权限需要访问控制列表，可移植的测试无法可靠地设置和恢复它。F04-T09 在 Linux 上检查同一个原因，F04-T08 检查 Windows 上文件夹引发的 `PermissionError`。 |
| 命令退出前关闭了文件。 | `main` 只通过 `count_words` 读取文件，F01 的用例检查它会关闭文件。F04-T16 检查命令不写任何文件。 |
| 输出用的是 `write` 而不是 `print()`。 | 两者写出的文字相同，调用方无法区分。由 ruff 的 T20 规则保证（架构第 8 节）。 |
| `argv` 中不是 `str` 的元素，以及含字符 U+0000 的路径。 | 设计 2.2 只允许 `str` 元素，其他类型不在约定之内。任何 shell 都无法在参数中传入 U+0000，所以 `wordcount` 永远收不到它。 |
| Windows 上 `wordcount` 向管道写出时，标准错误中非 ASCII 文件名的字节。 | 这时 Python 按系统代码页编码标准错误，字节因机器而异。F04-T06 通过 `main` 检查这类消息的文字，F04-T22 检查这类文件名能到达程序并被统计。 |
| PowerShell 找到 `wordcount`、`$LASTEXITCODE`、PowerShell 去掉引号的方式，以及 F04 合入后需要重新安装项目。 | CI 在 Linux 上运行，没有 PowerShell。v0.2 版本测试方案在 Troy 的电脑上用 Windows PowerShell 运行该命令。F04-T22 检查带引号的参数作为一个参数到达程序。 |
| 性能。 | 没有性能指标（R14）。 |

## 5. 与接口设计师的对齐记录

无。设计已回答本方案提出的所有问题。设计第 4 节中架构师的说明要求：Windows 和 Linux 行为不同之处，每个系统各有一个用例，或者跳过并写明原因。F04-T08 和 F04-T20 在两个系统上都运行，F04-T09 只在 Linux 上运行并写明原因，F04-T10 另加一个只用于 Windows 的名称。说明还要求测试只凭标准错误区分文件错误和错误的命令行：F04-T12 和 F04-T21 正是如此。

## 6. 修改记录

| 版本 | 日期 | 修改 |
| --- | --- | --- |
| 0.1 | 2026-11-15 | 初稿。 |
| 1.0 | 2026-11-15 | Troy 批准。 |
