---
troy-doc: "F06-test-plan"
lang: "zh-CN"
version: "1.0"
updated: "2026-11-23"
status: "Troy 已于 2026-11-23 批准"
mirror-of: "test-plan.md"
---

# F06 字符数选项：测试方案

## 1. 功能

- 编号和名称：F06 字符数选项
- 设计：[design.zh-CN.md](design.zh-CN.md)

## 2. 用例

F06 有三个外部接口，用例按各自调用方的方式调用它们。

- **`count_chars`。** F06-T01 到 F06-T17 像调用方一样导入它：`from troy_mode_trial import count_chars`。
- **`main`。** F06-T18 到 F06-T31 在测试自身的进程里调用它：`from troy_mode_trial.cli import main`。它们用 pytest 的 `capsys` 读取标准输出和标准错误，除非用例另有说明，用 `monkeypatch.chdir` 把测试的 `tmp_path` 设为工作目录。通过 `capsys`，换行符在两个系统上都是 `\n`。
- **`wordcount`。** F06-T32 到 F06-T35 以新进程启动已安装的程序，做法与 F04 的方案相同：不经过 shell，工作目录设为 `tmp_path`，以字节形式捕获标准输出和标准错误，用 `shutil.which("wordcount", path=sysconfig.get_path("scripts"))` 找到程序。找不到程序时测试失败，从不跳过。在这些用例中，`<NL>` 是字节形式的 `os.linesep`。

每个测试在 `tmp_path` 里自建文件，并以二进制方式写入用例给出的确切字节，这样 `\r\n` 以两个字符到达程序，Windows 也不会把 `\n` 改成 `\r\n`。输入中的 `\xXX`、`\uXXXX` 和 `\UXXXXXXXX` 表示一个 Unicode 码位，测试把它编码为 UTF-8；`EF BB BF` 表示字节顺序标记的字节。除非用例另有说明，下列文件的内容如下：

- `notes.txt` 内容为 `Hello world\n  troy-mode  trial\n`，即设计中的示例：31 个字符，4 个词。
- `windows.txt` 内容为 `EF BB BF` 后接 `Hello world\r\n  troy-mode  trial\r\n`，与记事本保存的一样：33 个字符。
- `hello.txt` 内容为 `你好\r\n`：8 个字节，4 个字符。
- `latin1.txt` 内容为 Latin-1 编码的 `café au lait\n`，其字节以 `63 61 66 E9 20` 开头。
- `sub` 是一个空文件夹。

文件名中 ASCII 以外的字符用 UTF-8。测试套件在 Windows 11 和 Linux 上运行，除非用例指明系统，每个用例在两个系统上预期相同的结果。

“恰好是”指完整的文字，与 F04 的方案相同。“用法错误”指：`main` 抛出 `code` 为 `2` 的 `SystemExit`，或程序以退出码 2 退出，且标准输出为空，标准错误恰好有两行，第一行以 `usage: wordcount ` 开头并含有 `--chars`，第二行以 `wordcount: error: ` 开头。用法行中的 `--chars` 正是 F06 的用法行与 F04 的区别，所以每个用法错误用例都会对着模拟实现失败。F05 加入 `--lines` 之后，这一点仍然成立。

“F06 用法行”指与正则表达式 `^usage: wordcount \[[^\]]*--chars[^\]]*\] FILE$` 匹配的一整行：以 `usage: wordcount ` 开头，在一对方括号内含有 `--chars`，以 ` FILE` 结尾。设计第 2.1 节的 `usage: wordcount [--chars] FILE` 与它匹配，`usage: wordcount [--lines | --chars] FILE` 也匹配；F04 的 `usage: wordcount FILE` 不匹配。只有 F06-T28 和 F06-T34 用这个模式检查完整的用法行。F06 的任何 PR 中都不会有已验收功能的测试失败，因为 F04 的方案 1.1 不再固定完整的用法行：F04-T11、F04-T12、F04-T13 和 F04-T21 只检查它以 `usage: wordcount ` 开头，以及退出码 2、空的标准输出和错误行。它们在 F06 的代码合入前后都能通过。

F05 与 F06 同时开发。它的设计（PR #67，已由架构师批准）规定两个功能都落地后用法行为 `usage: wordcount [--lines | --chars] FILE`；设计第 3 节规定 F05 和 F06 中后落地的一个保留另一个的选项。F06-T28 和 F06-T34 对这两种用法行都能通过，所以不依赖哪个功能先落地，F05 落地时 F06 的用例都不需要修改。它们仍会对着模拟实现失败，因为模拟实现的用法行是 F04 的（R09）。

对着模拟实现运行时，每个用例都因为选项尚未实现而失败。这假定模拟 PR 添加了函数体抛出 `NotImplementedError` 的 `count_chars`，从 `troy_mode_trial` 导出它，并让 `main` 及其用法行保持 F04 实现时的样子。这样每个 `count_chars` 用例得到 `NotImplementedError`，而不是它的结果或它的异常；每个 `main` 用例得到一个不认识 `--chars` 的用法错误，或得到用法行 `usage: wordcount FILE` 而不是新的用法行；每个 `wordcount` 用例得到退出码 2 和这个用法错误，而不是它的输出（R09）。如果模拟实现已经接受 `--chars` 并显示新的用法行，用法错误的用例就会对着它通过，这是 R09 不允许的，所以测试工程师要在测试 PR 之前报告。

| 编号 | 层级 | 接口 | 测什么 | 准备和输入 | 预期结果 |
| --- | --- | --- | --- | --- | --- |
| F06-T01 | 功能 | `count_chars` | 设计中的示例：解码后文本的每个字符都计数，包括行尾。 | `notes.txt`。以 `str` 形式传入其路径调用 `count_chars`。 | 返回 `31`，且结果的类型恰好是 `int`。 |
| F06-T02 | 单元 | `count_chars` | 行尾按文件中的原样计数，不做转换：`\n` 算 1，`\r` 算 1，`\r\n` 算 2（需求 Q11）。 | 六个文件：`\n`、`\r`、`\r\n`、`\r\r\n\n`、`one\rtwo\r\nthree\nfour` 和 `windows.txt`。分别以 `pathlib.Path` 传入路径调用。 | 返回 `1`、`1`、`2`、`4`、`19` 和 `33`。 |
| F06-T03 | 单元 | `count_chars` | 一个字符是一个码位，而不是一个字节。 | 五个文件：`hello.txt`；`日本語`（9 个字节）；`\xe9`（单个码位的 `é`，2 个字节）；`\U0001F600`（一个表情符号，4 个字节）；以及 `a\U0001F600b你c`。 | 返回 `4`、`3`、`1`、`1` 和 `5`。 |
| F06-T04 | 单元 | `count_chars` | 每个码位都算一次，不论它是什么；由多个码位组成的字符，每个码位各算一次。 | 三个文件：`é`（`e` 加组合重音符）；`\U0001F468‍\U0001F469‍\U0001F467`（用 U+200D 连接的一个家庭表情符号）；以及 `a\tb　c\x00d\x0ce\x85f g`。 | 返回 `2`、`5` 和 `13`。 |
| F06-T05 | 单元 | `count_chars` | 空文件和只含字节顺序标记的文件有 0 个字符。 | 两个文件：一个空文件，一个只有字节 `EF BB BF` 的文件。 | 每个都返回 `0`。 |
| F06-T06 | 单元 | `count_chars` | 只去掉文件最开头的一个字节顺序标记（需求 Q12）。其他位置的 U+FEFF，包括紧跟在第一个之后的第二个，都算一个字符。 | 五个文件：`EF BB BF` 后接 `x`；`EF BB BF EF BB BF` 后接 `a`；只有 `EF BB BF EF BB BF`；`a﻿`；以及 `a﻿b`。 | 返回 `1`、`2`、`1`、`2` 和 `3`。 |
| F06-T07 | 单元 | `count_chars` | 在大文件中计数仍然正确，其中 `\r\n` 或多字节字符可能被任意一个内部读取边界切开。 | 一个文件：`EF BB BF`，然后是 100,000 个 `abcde\r\n`（每个 7 字节），然后是 100,000 个 `你\r`（每个 4 字节），然后是 100,000 个 `z`。文件共 1,200,003 字节，超过 1 MiB。 | 返回 `1000000`。 |
| F06-T08 | 功能 | `count_chars` | `path` 的每种可接受形式得到相同的计数。 | `notes.txt`。分别以 `str` 形式的绝对路径、`pathlib.Path`，以及一个实现了 `__fspath__` 并返回 `str` 的测试类对象调用。 | 每个都返回 `31`。 |
| F06-T09 | 功能 | `count_chars` | 相对路径相对于当前工作目录解析。 | `tmp_path` 中的 `hello.txt`，用 `monkeypatch.chdir` 把 `tmp_path` 设为工作目录。分别以 `"hello.txt"` 和 `pathlib.Path("hello.txt")` 调用。 | 每个都返回 `4`。 |
| F06-T10 | 功能 | `count_chars` | 文件不存在，或 `path` 为空字符串时，抛出 Python 自己的异常（需求 Q4）。 | `tmp_path` 中一个不存在任何东西的路径，分别以 `str` 和 `pathlib.Path` 传入。然后是空字符串 `""`。 | 每个都抛出 `FileNotFoundError`。 |
| F06-T11 | 功能 | `count_chars` | 指向文件夹的路径抛出 Python 自己的异常。 | `tmp_path` 本身，分别以 `str` 和 `pathlib.Path` 传入。 | 每个都抛出 `IsADirectoryError` 或 `PermissionError`。在 Linux 上抛出 `IsADirectoryError`。 |
| F06-T12 | 功能 | `count_chars` | 进程无权读取的文件抛出 `PermissionError`。 | 仅限 Linux：一个内容为 `one two` 的文件，权限设为 `0o000`。在 Windows 上测试跳过，因为测试无法可移植地去掉自己的读权限；进程以 root 运行时也跳过，因为 root 仍能读取该文件。测试结束后恢复权限。 | 抛出 `PermissionError`。 |
| F06-T13 | 功能 | `count_chars` | 不是有效 UTF-8 的内容抛出 Python 自己的异常，不论无效字节在哪里。 | 四个文件：`latin1.txt`；100,000 个 `a` 后接字节 `FF`；`ok\nfine\n` 后接被截断的序列 `E6 97`；以及带字节顺序标记的 UTF-16 编码的 `hello\n`。 | 每个都抛出 `UnicodeDecodeError`。 |
| F06-T14 | 功能 | `count_chars` | 其他类型的 `path` 抛出 `TypeError`。 | 分别以 `b"notes.txt"`（`bytes`）、一个内容为 `one two` 的已打开文件的整数文件描述符、`None`、`3.5`，以及一个 `__fspath__` 返回 `bytes` 的对象调用。测试结束后关闭该描述符。 | 每个都抛出 `TypeError`。 |
| F06-T15 | 功能 | `count_chars` | 函数在返回和抛出异常之前关闭文件。 | 用 `warnings.catch_warnings(record=True)` 和 `simplefilter("always", ResourceWarning)` 记录警告。对 `notes.txt` 调用一次 `count_chars`，再对会抛出 `UnicodeDecodeError` 的 `latin1.txt` 调用一次。然后运行 `gc.collect()`，并把每个文件改名为 `tmp_path` 中的新名字。 | 第一次调用返回 `31`。没有记录到 `ResourceWarning`，两次改名都成功。在 Windows 上，改名能发现仍打开的文件，因为 Windows 无法给打开的文件改名。 |
| F06-T16 | 功能 | `count_chars` | 函数不写入也不保存任何东西。 | `windows.txt`。记录它的字节、以纳秒计的修改时间，以及 `tmp_path` 中的条目列表。调用 `count_chars` 两次。 | 两次都返回 `33`。文件的字节和修改时间不变，`tmp_path` 中的条目与之前相同。 |
| F06-T17 | 集成 | `count_chars`、`count_words`、`count_lines` | 包在 `count_words` 和 `count_lines` 旁边导出 `count_chars`，三者按各自的设计统计同一个文件。 | `from troy_mode_trial import count_chars, count_lines, count_words`。对 `windows.txt` 分别调用。 | `count_chars` 返回 `33`，`count_words` 返回 `4`，`count_lines` 返回 `2`。`"count_chars"`、`"count_lines"` 和 `"count_words"` 都在 `troy_mode_trial.__all__` 中。 |
| F06-T18 | 功能 | `main` | 设计中的示例：带 `--chars` 时，标准输出是字符数和一个换行符，返回 0。 | `notes.txt` 和 `hello.txt`。先 `main(["--chars", "notes.txt"])`，再 `main(["--chars", "hello.txt"])`。 | 每次都返回 `0`，且结果的类型恰好是 `int`。标准输出先恰好是 `31\n`，再恰好是 `4\n`。标准错误保持为空。 |
| F06-T19 | 功能 | `main` | 选项可以放在文件之后，给两次也只计数一次（设计提议 3）。 | `notes.txt`。先 `main(["notes.txt", "--chars"])`，再 `main(["--chars", "--chars", "notes.txt"])`。 | 每次都返回 `0`，向标准输出恰好写入 `31\n`，标准错误为空。 |
| F06-T20 | 单元 | `main` | 选项只改变统计的内容。`main` 在调用之间不保留状态，也不写任何文件。 | `notes.txt` 和 `latin1.txt`。记录 `tmp_path` 中每个文件的名字和字节、工作目录和 `sys.argv`。在一个进程里依次以 `["--chars", "notes.txt"]`、`["notes.txt"]`、`["--chars", "missing.txt"]`、`["--chars", "latin1.txt"]` 和 `["--chars", "notes.txt"]` 调用 `main`，每次调用后读取输出。 | 各次调用返回 `0`、`0`、`2`、`2` 和 `0`。每次调用的输出只有它自己的：`31\n`；`4\n`；标准错误上的 `wordcount: missing.txt: no such file\n`；标准错误上的 `wordcount: latin1.txt: not valid UTF-8\n`；以及 `31\n`。之后 `tmp_path` 中的文件和字节不变，工作目录和 `sys.argv` 也不变。 |
| F06-T21 | 单元 | `main` | 打印的计数就是 `count_chars` 统计的结果，是不带符号、填充或分隔符的十进制数。 | 五个文件：`windows.txt`；空文件 `empty.txt`；只有字节 `EF BB BF` 的 `bom.txt`；内容为 `one\rtwo\r\nthree\nfour` 的 `mixed.txt`；以及内容为 12,345 个 `a` 的 `many.txt`。对每个文件调用 `main(["--chars", <name>])`。 | 每次都返回 `0`，标准错误为空。标准输出恰好是 `33\n`、`0\n`、`0\n`、`19\n` 和 `12345\n`。 |
| F06-T22 | 单元 | `main` | 带 `--chars` 时，`FILE` 可以是设计允许的任何路径形式。在 `--` 之后，文字 `--chars` 是文件名，不是选项。 | `notes.txt`，以及它的副本 `sub/notes.txt`、`my notes.txt`、`日本語.txt`、`-notes.txt` 和 `--chars`。六次调用，除第一次外工作目录都是 `tmp_path`：在工作目录 `sub` 中 `main(["--chars", <notes.txt 的绝对路径>])`；`main(["--chars", "sub/notes.txt"])`；`main(["--chars", "my notes.txt"])`；`main(["--chars", "日本語.txt"])`；`main(["--chars", "--", "-notes.txt"])`；以及 `main(["--chars", "--", "--chars"])`。 | 每次调用都返回 `0`，向标准输出恰好写入 `31\n`，标准错误为空。 |
| F06-T23 | 功能 | `main` | 设计中带 `--chars` 的文件不存在的示例，以及“no such file”的其他各种情况，给出与 `wordcount FILE` 相同的一行，参数按输入的原样显示。 | `notes.txt` 存在。四次调用：`main(["--chars", "missing.txt"])`、`main(["--chars", ""])`、`main(["--chars", "missing-folder/notes.txt"])` 和 `main(["--chars", "notes.txt/inner.txt"])`。 | 每次都返回 `2`，标准输出为空。标准错误恰好是 `wordcount: missing.txt: no such file\n`、`wordcount: : no such file\n`、`wordcount: missing-folder/notes.txt: no such file\n` 和 `wordcount: notes.txt/inner.txt: no such file\n`。 |
| F06-T24 | 功能 | `main` | 带 `--chars` 时，不是有效 UTF-8 的文件给出原因 `not valid UTF-8`，即使无效字节出现在有效文本之后，而且不打印计数。 | `latin1.txt`；字节为 `6F 6B 20 FF FE` 的 `broken.txt`；以及内容为 100,000 个 `a` 后接字节 `FF` 的 `late.txt`。对每个文件调用 `main(["--chars", <name>])`。 | 每次都返回 `2`，标准输出为空。标准错误恰好是 `wordcount: latin1.txt: not valid UTF-8\n`、`wordcount: broken.txt: not valid UTF-8\n` 和 `wordcount: late.txt: not valid UTF-8\n`。 |
| F06-T25 | 功能 | `main` | 带 `--chars` 时，文件夹在两个系统上都给出原因 `is a folder`。 | `main(["--chars", "sub"])` 和 `main(["--chars", "."])`。在 Windows 和 Linux 上运行。 | 每次都返回 `2`，标准输出为空。标准错误恰好是 `wordcount: sub: is a folder\n` 和 `wordcount: .: is a folder\n`。 |
| F06-T26 | 功能 | `main` | 带 `--chars` 时，进程无权读取的文件给出原因 `permission denied`。 | 仅限 Linux：`secret.txt` 内容为 `one two`，权限设为 `0o000`。`main(["--chars", "secret.txt"])`。出于 F06-T12 中的原因，在 Windows 上和进程以 root 运行时测试跳过。测试结束后恢复权限。 | 返回 `2`。标准输出为空。标准错误恰好是 `wordcount: secret.txt: permission denied\n`。 |
| F06-T27 | 单元 | `main` | 带 `--chars` 时，打开文件时的其他任何错误给出原因 `cannot read file`。 | 一个由 300 个 `a` 后接 `.txt` 组成的名字，超过两个系统对单个名字的长度限制。仅在 Windows 上，再加上 Windows 不允许的名字 `a?b.txt`。对每个名字调用 `main(["--chars", <name>])`。 | 每次都返回 `2`，标准输出为空。标准错误恰好是 `wordcount: <name>: cannot read file\n`，其中 `<name>` 是给出的参数原样。 |
| F06-T28 | 功能 | `main` | 设计中 `--chars` 不带文件的示例，它显示新的用法行。 | `main(["--chars"])`。 | 用法错误。标准错误的第一行是 F06 用法行，第二行恰好是 `wordcount: error: the following arguments are required: FILE`。 |
| F06-T29 | 单元 | `main` | 带选项的其他错误命令行都是用法错误，而不是计数、文件错误或帮助文字：缩写的名字、短形式、带值、第二个文件、帮助，以及两个计数选项（设计提议 2，需求 Q10 和 Q13）。 | `notes.txt` 存在。九次调用：`main(["--char", "notes.txt"])`、`main(["--ch", "notes.txt"])`、`main(["--c", "notes.txt"])`、`main(["-c", "notes.txt"])`、`main(["--CHARS", "notes.txt"])`、`main(["--chars=5", "notes.txt"])`、`main(["--chars", "notes.txt", "notes.txt"])`、`main(["--chars", "-h"])` 和 `main(["--lines", "--chars", "notes.txt"])`。 | 每次都是用法错误。第一次调用时，标准错误的第二行恰好是 `wordcount: error: unrecognized arguments: --char`。第四次时恰好是 `wordcount: error: unrecognized arguments: -c`。没有一次调用写出计数、帮助文字或 `wordcount: <FILE>: <reason>` 这样的一行。 |
| F06-T30 | 单元 | `main` | 不论 `sys.argv[0]` 是什么，每条消息中的程序名都是 `wordcount`。 | `monkeypatch.setattr(sys, "argv", ["other-name.py"])`。先调用 `main(["--char", "notes.txt"])`，再调用 `main(["--chars", "missing.txt"])`。 | 第一次是用法错误，所以第一行以 `usage: wordcount ` 开头并含有 `--chars`。第二次返回 `2`，向标准错误恰好写入 `wordcount: missing.txt: no such file\n`。 |
| F06-T31 | 单元 | `main` | 不带参数时，`main` 像控制台脚本那样读取 `sys.argv[1:]`；`argv` 可以是任何 `str` 序列。 | `notes.txt`。`monkeypatch.setattr(sys, "argv", ["wordcount", "--chars", "notes.txt"])`，然后调用 `main()` 和 `main(None)`。再调用 `main(("--chars", "notes.txt"))`，参数是元组。 | 每次都返回 `0`，向标准输出恰好写入 `31\n`。 |
| F06-T32 | 集成 | `wordcount` | 已安装的程序统计字符，与 F06 原型一致；不带选项时仍统计词数。 | `notes.txt` 和 `hello.txt`。四次运行：`wordcount --chars notes.txt`、`wordcount notes.txt --chars`、`wordcount --chars hello.txt` 和 `wordcount notes.txt`。 | 每次都以退出码 0 退出，标准错误为空。标准输出恰好是 `31<NL>`、`31<NL>`、`4<NL>` 和 `4<NL>`。 |
| F06-T33 | 集成 | `wordcount` | 已安装的程序以退出码 2 报告带 `--chars` 的文件错误，与 F06 原型一致。 | 先是空的工作目录，然后是 `latin1.txt`。两次运行：`wordcount --chars missing.txt` 和 `wordcount --chars latin1.txt`。 | 每次都以退出码 2 退出，标准输出为空。标准错误先恰好是 `wordcount: missing.txt: no such file<NL>`，再恰好是 `wordcount: latin1.txt: not valid UTF-8<NL>`。 |
| F06-T34 | 集成 | `wordcount` | 带选项的错误命令行以退出码 2 退出，并显示新的用法行。 | `notes.txt`。三次运行：`wordcount --char notes.txt`、不带文件的 `wordcount --chars`，以及 `wordcount -c notes.txt`。 | 每次都是用法错误，退出码为 2。第一次运行时，标准错误恰好有两行，每行以 `<NL>` 结尾：先是 F06 用法行，然后是 `wordcount: error: unrecognized arguments: --char`，与设计第 2.1 节的示例相同。 |
| F06-T35 | 集成 | `wordcount` | 带 `--chars` 时，参数按 Troy 输入的样子到达程序。 | `notes.txt` 的副本 `my notes.txt`、`日本語.txt` 和 `-notes.txt`。三次运行：`wordcount --chars "my notes.txt"`，一个含空格的参数；`wordcount --chars 日本語.txt`；以及 `wordcount --chars -- -notes.txt`。 | 每次都以退出码 0 退出，向标准输出恰好写入 `31<NL>`，标准错误为空。 |

## 3. 性能用例

无。设计第 2.1、2.2 和 2.3 节没有设定性能指标，需求第 7.1 节也没有为项目设定任何性能指标（R14）。

## 4. 不测的内容

| 内容 | 原因 |
| --- | --- |
| 不带 `--chars` 的 `wordcount FILE` 和 `main`：词数、它的错误行，以及除用法行以外的用法错误。 | F04-T01 到 F04-T22 检查它们。F04 的方案 1.1 只放宽了其中的用法错误用例，它们现在检查用法行以 `usage: wordcount ` 开头。为它们新增 F06 用例会对着模拟实现通过，这是 R09 不允许的。F06-T20 和 F06-T32 仍在字符数旁边检查一次词数。 |
| 程序缺陷：文件错误以外的异常传到调用方，Python 写出回溯，程序以退出码 1 退出。 | 与 F04 的方案相同：通过外部接口的任何输入都不会让统计函数抛出其他异常，要引发这种异常就得替换 cli 内部的函数。 |
| `count_chars` 异常消息的文字，例如设计示例中的 `[Errno 2] No such file or directory: 'missing.txt'`。 | 消息由 Python 生成，设计只承诺异常类型（需求 Q4）。F06-T10 到 F06-T14 检查类型。 |
| Windows 上不可读文件的 `PermissionError`。 | 在 Windows 上去掉文件的读权限需要访问控制列表，可移植的测试无法可靠地设置和恢复。F06-T12 和 F06-T26 在 Linux 上检查同一行为。 |
| Windows 对文件夹抛出 `IsADirectoryError` 还是 `PermissionError`。 | 设计允许 Windows 抛出其中任一个。F06-T11 在 Windows 上接受任一个，在 Linux 上要求 `IsADirectoryError`。 |
| 逐字的用法行，以及 F05 加入 `--lines` 后 `--lines` 与 `--chars` 同用时的消息。 | 两个功能都落地后的用法行和这条消息由 F05 的设计确定（设计第 3 节）。F06-T28 和 F06-T34 用两种用法行都匹配的模式检查用法行，F06-T29 只检查 `--lines` 与 `--chars` 同用是用法错误。 |
| 不是 `str` 的 `argv` 元素。 | 设计第 2.2 节只允许 `str` 元素，其他类型不在约定范围内。 |
| 在 Windows 上 `wordcount` 写入管道时，标准错误中 ASCII 以外文件名的字节。 | 与 F04 的方案相同：Python 此时用系统代码页编码标准错误，所以字节取决于机器。F06-T35 检查这样的名字能到达程序并被统计。 |
| PowerShell 找到 `wordcount`、`$LASTEXITCODE`、PowerShell 去掉引号的方式，以及 F06 落地后需要重新安装项目。 | CI 在没有 PowerShell 的 Linux 上运行。v0.3 版本测试方案在 Troy 电脑的 Windows PowerShell 中运行这个命令。F06-T35 检查带引号的参数作为一个参数到达程序。 |
| 性能。 | 没有性能指标（R14）。 |

## 5. 与接口设计师的对齐记录

无。设计已回答本方案提出的所有用例问题。架构师在设计第 4 节的说明中请测试经理只修改 F04-T11、F04-T12、F04-T13 和 F04-T21 预期的第一行，并以二进制方式写入每个文件，使 `\r\n` 以两个字符到达 `count_chars`。本方案第 2 节要求了第二项。对于第一项，F04 的方案 1.1 把这一行放宽为只检查开头 `usage: wordcount `，而不是像设计第 3 节所说那样固定为 `usage: wordcount [--chars] FILE`。这是产品经理在第 2 轮中提出的：已验收功能的测试在每个 PR 中都必须通过（R10），所以预期 F06 用法行的 F04 测试会在 F06 的测试 PR 中失败。完整的用法行改由 F06-T28 和 F06-T34 检查。产品经理在第 3 轮中要求它们不依赖 F05 和 F06 谁先落地，所以它们用一个在 F05 落地前后都成立的模式检查用法行。设计的接口不变。

## 6. 修改记录

| 版本 | 日期 | 修改 |
| --- | --- | --- |
| 0.1 | 2026-11-23 | 初稿。 |
| 0.2 | 2026-11-23 | 用法错误的第一行现在以 `usage: wordcount ` 开头并含有 `--chars`。只有 F06-T28 和 F06-T34 检查完整的用法行。F04 的用法错误用例改为放宽而不是修改，使 F04 的测试在 F06 的任何 PR 中都不失败。补充说明了 F05 落地后的用法行。 |
| 0.3 | 2026-11-23 | F06-T28 和 F06-T34 用一个在 F05 落地前后都能匹配用法行的模式检查它，F05 落地时 F06 的用例都不需要修改。 |
| 1.0 | 2026-11-23 | Troy 批准。 |
