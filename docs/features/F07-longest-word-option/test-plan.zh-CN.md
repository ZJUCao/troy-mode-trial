---
troy-doc: "F07-test-plan"
lang: "zh-CN"
version: "1.1"
updated: "2026-11-26"
status: "Troy 已于 2026-11-25 批准。2026-11-26 为 F08 修改。"
mirror-of: "test-plan.md"
---

# F07 最长词选项：测试方案

## 1. 功能

- 编号和名称：F07 最长词选项
- 设计：[design.zh-CN.md](design.zh-CN.md)

## 2. 用例

F07 有三个外部接口，用例按各自调用方的方式调用它们。

- **`count_longest`。** F07-T01 到 F07-T19 像调用方一样导入它：`from troy_mode_trial import count_longest`。
- **`main`。** F07-T20 到 F07-T33 在测试自身的进程里调用它：`from troy_mode_trial.cli import main`。它们用 pytest 的 `capsys` 读取标准输出和标准错误，除非用例另有说明，用 `monkeypatch.chdir` 把测试的 `tmp_path` 设为工作目录。通过 `capsys`，换行符在两个系统上都是 `\n`。
- **`wordcount`。** F07-T34 到 F07-T37 以新进程启动已安装的程序，做法与 F04 的方案相同：不经过 shell，工作目录设为 `tmp_path`，以字节形式捕获标准输出和标准错误，用 `shutil.which("wordcount", path=sysconfig.get_path("scripts"))` 找到程序。找不到程序时测试失败，从不跳过。在这些用例中，`<NL>` 是字节形式的 `os.linesep`。

每个测试在 `tmp_path` 里自建文件，并以二进制方式写入用例给出的确切字节，这样 `\r\n` 原样到达程序。输入中的 `\xXX`、`\uXXXX` 和 `\UXXXXXXXX` 表示一个 Unicode 码位，测试把它编码为 UTF-8；`EF BB BF` 表示字节顺序标记的字节。除非用例另有说明，下列文件的内容如下：

- `notes.txt` 内容为 `Hello world\n  troy-mode  trial\n`，即设计中的示例：4 个词，最长的是 `troy-mode`，9 个字符。
- `windows.txt` 内容为 `EF BB BF` 后接 `Hello world\r\n  troy-mode  trial\r\n`，与记事本保存的一样：最长词为 9。
- `greeting.txt` 内容为 `你好 世界!\r\n`，即设计中的示例：2 个词，最长的是 `世界!`，3 个字符，7 个字节。
- `dashes.txt` 内容为 `-- ...\n`，即设计中的示例：没有词。
- `latin1.txt` 内容为 Latin-1 编码的 `café au lait\n`，其字节以 `63 61 66 E9 20` 开头。
- `sub` 是一个空文件夹。

文件名中 ASCII 以外的字符用 UTF-8。测试套件在 Windows 11 和 Linux 上运行，除非用例指明系统，每个用例在两个系统上预期相同的结果。

“恰好是”指完整的文字，与 F04 的方案相同。“F07 用法行”恰好是 `usage: wordcount [--lines | --chars | --longest] FILE`，即设计第 2.1 节中、Troy 随设计一起批准的那一行。“用法错误”指：`main` 抛出 `code` 为 `2` 的 `SystemExit`，或程序以退出码 2 退出，且标准输出为空，标准错误恰好有两行，第一行恰好是 `<USAGE>`，第二行以 `wordcount: error: ` 开头。F05 和 F06 已验收，代码已在 `main` 上，所以用法行不再取决于落地顺序，每个 F07 用例都逐字检查它。

**F08 落地后的用法行。** F08 把 `--again` 加入同一组选项，用法行变为 `usage: wordcount [--lines | --chars | --longest | --again] FILE`（F08 设计第 3.1 节方案 1）。F07 已验收，所以它的用例在每个 F08 PR 中、F08 的代码合入前后都必须通过（R10）。因此本方案中的 `<USAGE>` 在被测分支上没有 F08 的代码时是 F07 用法行，有 F08 的代码时是 F08 的那一行。检查用法行的用例先通过它所测的接口询问状态，并丢弃这次调用的输出。`main` 用例调用 `main(["--again", "notes.txt"])`：F08 的代码落地后，它不抛异常地返回 `0` 或 `2`；未落地时，它抛出 code 为 `2` 的 `SystemExit`，第二行为 `wordcount: error: unrecognized arguments: --again`。`wordcount` 用例运行 `wordcount --again notes.txt`：F08 的代码落地后，它以退出码 0 退出，或以退出码 2 退出且标准错误上只有一行、以 `wordcount: no saved options to run again: ` 开头；未落地时，它以退出码 2 退出，第二行即上面那一行。探测得到其他结果时用例失败。`--again` 不改变 F07 用例预期的任何第二行。这改变 F07-T30、F07-T31、F07-T32 和 F07-T36，它们保留原名。没有用例被废止。

**F05 的用法行用例。** F05-T13、F05-T14、F05-T15 和 F05-T23 逐字检查用法错误的第一行为 `usage: wordcount [--lines | --chars] FILE`。F07 改变了这一行（设计第 3 节第 2 项）。F05 已验收，所以这四个用例在 F07 的每个 PR 中、F07 的代码合入前后都必须通过（R10），而实现 PR 不得修改测试（R08）。因此本 PR 把 F05 的方案改为 0.2 版：它的 `<USAGE>` 增加第三种状态，即 F07 的代码已在被测分支上时为 `usage: wordcount [--lines | --chars | --longest] FILE`。这四个用例像现在判断 F06 的状态一样，通过各自测试的接口判断这一状态：F07 的代码落地后 `main(["--longest", "notes.txt"])` 返回 `0`，未落地时抛出 code 为 `2` 的 `SystemExit`；`wordcount --longest notes.txt` 同样以退出码 0 或 2 区分。探测得到其他结果时用例失败。它们的第二行不变，因为 `--longest` 不改变其中任何一条消息。F07 的测试 PR 在 `tests/test_cli_lines.py` 中做这项修改，例如在 `USAGE_BOTH` 旁边加第二个常量和第二个探测，而不是替换 `USAGE_BOTH`。四个用例保留原名。F06-T28 和 F06-T34 用一个 F07 用法行也匹配的模式检查用法行，F06 的其他用法错误只检查第一行含有 `--chars`，F04 的用例只检查它以 `usage: wordcount ` 开头，所以它们的方案不变。

对着模拟实现运行时，每个用例都因为选项尚未实现而失败。这假定模拟 PR 添加了在查看 `path` 之前就抛出 `NotImplementedError` 的 `count_longest`，从 `troy_mode_trial` 导出它，并让 `main` 及其用法行与 `main` 分支上的完全一样。这样每个 `count_longest` 用例得到 `NotImplementedError`，而不是它的结果或它的异常；每个 `main` 用例得到一个不认识 `--longest` 的用法错误，或得到旧用法行 `usage: wordcount [--lines | --chars] FILE` 而不是 F07 用法行；每个 `wordcount` 用例得到退出码 2 和这个用法错误，而不是它的输出（R09）。F05 的四个用例对着模拟实现通过，因为它们的探测发现 F07 的代码尚未落地。如果模拟实现的 `main` 已经接受 `--longest`，F05 用例的探测就会得到 `NotImplementedError`，F05 的测试会失败，这是 R10 不允许的，所以测试工程师要在测试 PR 之前报告。

| 编号 | 层级 | 接口 | 测什么 | 准备和输入 | 预期结果 |
| --- | --- | --- | --- | --- | --- |
| F07-T01 | 功能 | `count_longest` | 设计中的示例：最长词的长度，以字符计。 | `notes.txt`。以 `str` 形式传入其路径调用 `count_longest`。 | 返回 `9`，且结果的类型恰好是 `int`。 |
| F07-T02 | 单元 | `count_longest` | F03 计数的整段就是词，包括标点（需求 Q15）。 | 六个文件：`don't, he said.`；`----a ......`；`x--y`；`see https://example.com/a now`；`3.14`；以及 `____ b`。分别以 `pathlib.Path` 传入路径调用。 | 返回 `6`、`5`、`4`、`21`、`4` 和 `1`。 |
| F07-T03 | 单元 | `count_longest` | 不含字母或数字的一段不是词，不论多长，其长度都不计入。 | 四个文件：`dashes.txt`；`ab ------------`；`!!!!!!!!!! a`；以及 `\U0001F600\U0001F600 !!`。 | 返回 `0`、`2`、`1` 和 `0`。 |
| F07-T04 | 单元 | `count_longest` | 每个 `str.isspace()` 为真的字符都分隔词，且从不属于词。不是空白的字符，即使看不见，也属于它所在的一段。 | 四个文件：`a\tbb\rccc\r\ndd`；`x　yy`；`a\x0bbb\x0cccc\x85dddd\xa0e`；以及 `a​b`（U+200B 不是空白）。 | 返回 `3`、`2`、`4` 和 `3`。 |
| F07-T05 | 单元 | `count_longest` | Windows 和 Linux 的行尾得到相同的结果。 | `notes.txt` 和 `windows.txt`。 | 每个都返回 `9`。 |
| F07-T06 | 单元 | `count_longest` | 长度按码位计，而不是按字节计；由多个码位组成的字符，每个码位各算一次。 | 六个文件：`greeting.txt`；`日本語`；`\U0001F600a`；`é`（`e` 加组合重音符组成的 `é`）；`\xe9`（单个码位的 `é`）；以及 `\U0001F468‍\U0001F469‍\U0001F467 a`（用 U+200D 连接的一个家庭表情符号，不含字母或数字）。 | 返回 `3`、`3`、`2`、`2`、`1` 和 `1`。 |
| F07-T07 | 单元 | `count_longest` | 没有词的文件返回 0。 | 三个文件：一个空文件，一个只有字节 `EF BB BF` 的文件，以及 `  \r\n\t\n`。 | 每个都返回 `0`。 |
| F07-T08 | 单元 | `count_longest` | 只去掉文件最开头的一个字节顺序标记（需求 Q5）。其他位置的 U+FEFF 属于它所在的一段。 | 五个文件：`EF BB BF` 后接 `abc`；`EF BB BF EF BB BF` 后接 `abc`；`EF BB BF` 后接 `-- abcd`；`ab﻿c`；以及只有 `EF BB BF EF BB BF`。 | 返回 `3`、`4`、`4`、`4` 和 `0`。 |
| F07-T09 | 单元 | `count_longest` | 最长词不论在哪个位置都能找到；几个词同为最长时，结果就是那个长度。 | 四个文件：`abc xyz`；末尾没有换行的 `a bb ccc`；`cccc bb a`；以及 `word`。 | 返回 `3`、`3`、`4` 和 `4`。 |
| F07-T10 | 单元 | `count_longest` | 在大文件中结果仍然正确，其中一个词、一个 `\r\n` 或一个多字节字符可能被任意一个内部读取边界切开。 | 一个文件：`EF BB BF`，然后是 150,000 个 `你好世 ab\r\n`（每个 14 字节），然后是 70,000 个 `x`，然后是 `\n`，然后是 100,000 个 `-`。文件共 2,270,004 字节，超过 2 MiB。 | 返回 `70000`。 |
| F07-T11 | 功能 | `count_longest` | `path` 的每种可接受形式得到相同的结果。 | `notes.txt`。分别以 `str` 形式的绝对路径、`pathlib.Path`，以及一个实现了 `__fspath__` 并返回 `str` 的测试类对象调用。 | 每个都返回 `9`。 |
| F07-T12 | 功能 | `count_longest` | 相对路径相对于当前工作目录解析。 | `tmp_path` 中的 `greeting.txt`，用 `monkeypatch.chdir` 把 `tmp_path` 设为工作目录。分别以 `"greeting.txt"` 和 `pathlib.Path("greeting.txt")` 调用。 | 每个都返回 `3`。 |
| F07-T13 | 功能 | `count_longest` | 文件不存在，或 `path` 为空字符串时，抛出 Python 自己的异常（需求 Q4）。 | `tmp_path` 中一个不存在任何东西的路径，分别以 `str` 和 `pathlib.Path` 传入。然后是空字符串 `""`。 | 每个都抛出 `FileNotFoundError`。 |
| F07-T14 | 功能 | `count_longest` | 指向文件夹的路径抛出 Python 自己的异常。 | `tmp_path` 本身，分别以 `str` 和 `pathlib.Path` 传入。 | 每个都抛出 `IsADirectoryError` 或 `PermissionError`。在 Linux 上抛出 `IsADirectoryError`。 |
| F07-T15 | 功能 | `count_longest` | 进程无权读取的文件抛出 `PermissionError`。 | 仅限 Linux：一个内容为 `one two` 的文件，权限设为 `0o000`。在 Windows 上测试跳过，因为测试无法可移植地去掉自己的读权限；进程以 root 运行时也跳过，因为 root 仍能读取该文件。测试结束后恢复权限。 | 抛出 `PermissionError`。 |
| F07-T16 | 功能 | `count_longest` | 不是有效 UTF-8 的内容抛出 Python 自己的异常，不论无效字节在哪里，即使它在一个很长的有效词之后。 | 四个文件：`latin1.txt`；100,000 个 `a` 后接字节 `FF`；`ok fine\n` 后接被截断的序列 `E6 97`；以及带字节顺序标记的 UTF-16 编码的 `hello\n`。 | 每个都抛出 `UnicodeDecodeError`。 |
| F07-T17 | 功能 | `count_longest` | 其他类型的 `path` 抛出 `TypeError`。 | 分别以 `b"notes.txt"`（`bytes`）、一个内容为 `one two` 的已打开文件的整数文件描述符、`None`、`3.5`，以及一个 `__fspath__` 返回 `bytes` 的对象调用。测试结束后关闭该描述符。 | 每个都抛出 `TypeError`。 |
| F07-T18 | 功能 | `count_longest` | 函数在返回和抛出异常之前关闭文件，且不写入也不保存任何东西。 | 用 `warnings.catch_warnings(record=True)` 和 `simplefilter("always", ResourceWarning)` 记录警告。记录 `windows.txt` 的字节和以纳秒计的修改时间，以及 `tmp_path` 中的条目。对 `windows.txt` 调用 `count_longest` 两次，再对会抛出 `UnicodeDecodeError` 的 `latin1.txt` 调用一次。然后运行 `gc.collect()`，并把每个文件改名为 `tmp_path` 中的新名字。 | 对 `windows.txt` 的两次调用都返回 `9`。改名之前，`windows.txt` 的字节和修改时间不变，`tmp_path` 中的条目与之前相同。没有记录到 `ResourceWarning`，两次改名都成功。在 Windows 上，改名能发现仍打开的文件，因为 Windows 无法给打开的文件改名。 |
| F07-T19 | 集成 | `count_longest`、`count_words`、`count_chars`、`count_lines` | 包在另外三个函数旁边导出 `count_longest`，且 `count_longest` 与 `count_words` 对什么是词的判断一致（需求 Q15）。 | `from troy_mode_trial import count_chars, count_lines, count_longest, count_words`。对 `notes.txt` 分别调用。然后对七个文件调用 `count_words` 和 `count_longest`：一个空文件；只有 `EF BB BF`；`dashes.txt`；`\U0001F600 !!`；`x`；`don't, he said.`；以及 `greeting.txt`。 | 对 `notes.txt`，`count_longest` 返回 `9`，`count_words` 返回 `4`，`count_chars` 返回 `31`，`count_lines` 返回 `2`。对七个文件，`count_longest` 返回 `0`、`0`、`0`、`0`、`1`、`6` 和 `3`，`count_words` 恰好对前四个返回 `0`。`"count_chars"`、`"count_lines"`、`"count_longest"` 和 `"count_words"` 都在 `troy_mode_trial.__all__` 中。 |
| F07-T20 | 功能 | `main` | 设计中的示例：带 `--longest` 时，标准输出是长度和一个换行符，返回 0。 | `notes.txt`、`greeting.txt` 和 `dashes.txt`。对每个文件调用 `main(["--longest", <name>])`。 | 每次都返回 `0`，且结果的类型恰好是 `int`。标准输出恰好是 `9\n`、`3\n` 和 `0\n`。标准错误保持为空。 |
| F07-T21 | 功能 | `main` | 选项可以放在文件之后，给两次与给一次效果相同。 | `notes.txt`。三次调用：`main(["notes.txt", "--longest"])`、`main(["--longest", "--longest", "notes.txt"])` 和 `main(["notes.txt", "--longest", "--longest"])`。 | 每次都返回 `0`，向标准输出恰好写入 `9\n`，标准错误为空。 |
| F07-T22 | 单元 | `main` | 打印的数字就是 `count_longest` 返回的结果，是不带符号、填充或分隔符的十进制数。 | 五个文件：`windows.txt`；空文件 `empty.txt`；只有字节 `EF BB BF` 的 `bom.txt`；内容为 `don't, he said.` 的 `said.txt`；以及内容为一个由 12,345 个 `a` 组成的词后接 `\n` 的 `many.txt`。对每个文件调用 `main(["--longest", <name>])`。 | 每次都返回 `0`，标准错误为空。标准输出恰好是 `9\n`、`0\n`、`0\n`、`6\n` 和 `12345\n`。 |
| F07-T23 | 单元 | `main` | 选项只改变打印的内容。`main` 在调用之间不保留状态，也不写任何文件。 | `notes.txt` 和 `latin1.txt`。记录 `tmp_path` 中每个文件的名字和字节、工作目录和 `sys.argv`。在一个进程里依次以 `["--longest", "notes.txt"]`、`["notes.txt"]`、`["--longest", "missing.txt"]`、`["--longest", "latin1.txt"]`、`["--chars", "notes.txt"]`、`["--lines", "notes.txt"]` 和 `["--longest", "notes.txt"]` 调用 `main`，每次调用后读取输出。 | 各次调用返回 `0`、`0`、`2`、`2`、`0`、`0` 和 `0`。每次调用的输出只有它自己的：`9\n`；`4\n`；标准错误上的 `wordcount: missing.txt: no such file\n`；标准错误上的 `wordcount: latin1.txt: not valid UTF-8\n`；`31\n`；`2\n`；以及 `9\n`。之后 `tmp_path` 中的文件和字节不变，工作目录和 `sys.argv` 也不变。 |
| F07-T24 | 单元 | `main` | 带 `--longest` 时，`FILE` 可以是设计允许的任何路径形式。在 `--` 之后，文字 `--longest` 是文件名，不是选项。 | `notes.txt`，以及它的副本 `sub/notes.txt`、`my notes.txt`、`日本語.txt`、`-notes.txt` 和 `--longest`。六次调用，除第一次外工作目录都是 `tmp_path`：在工作目录 `sub` 中 `main(["--longest", <notes.txt 的绝对路径>])`；`main(["--longest", "sub/notes.txt"])`；`main(["--longest", "my notes.txt"])`；`main(["--longest", "日本語.txt"])`；`main(["--longest", "--", "-notes.txt"])`；以及 `main(["--longest", "--", "--longest"])`。然后第七次调用 `main(["--", "--longest"])`。 | 前六次调用都返回 `0`，向标准输出恰好写入 `9\n`，标准错误为空。第七次返回 `0` 并恰好写入 `4\n`：它统计名为 `--longest` 的文件的词数。 |
| F07-T25 | 功能 | `main` | 设计中带 `--longest` 的文件不存在的示例，以及“no such file”的其他各种情况，给出与 `wordcount FILE` 相同的一行，参数按输入的原样显示。 | `notes.txt` 存在。七次调用：`main(["--longest", "missing.txt"])`、`main(["missing.txt"])`、`main(["--longest", ""])`、`main(["--longest", "missing-folder/notes.txt"])`、`main(["--longest", "notes.txt/inner.txt"])`、`main(["--longest", "缺失.txt"])` 和 `main(["missing.txt", "--longest"])`。 | 每次都返回 `2`，标准输出为空。标准错误前两次都恰好是 `wordcount: missing.txt: no such file\n`，然后是 `wordcount: : no such file\n`、`wordcount: missing-folder/notes.txt: no such file\n`、`wordcount: notes.txt/inner.txt: no such file\n`、`wordcount: 缺失.txt: no such file\n` 和 `wordcount: missing.txt: no such file\n`。 |
| F07-T26 | 功能 | `main` | 带 `--longest` 时，不是有效 UTF-8 的文件给出原因 `not valid UTF-8`，即使无效字节出现在有效的词之后，而且不打印数字。 | `latin1.txt`；字节为 `6F 6B 20 FF FE` 的 `broken.txt`；以及内容为 100,000 个 `a longword\n` 后接字节 `FF` 的 `late.txt`。对每个文件调用 `main(["--longest", <name>])`。 | 每次都返回 `2`，标准输出为空。标准错误恰好是 `wordcount: latin1.txt: not valid UTF-8\n`、`wordcount: broken.txt: not valid UTF-8\n` 和 `wordcount: late.txt: not valid UTF-8\n`。 |
| F07-T27 | 功能 | `main` | 带 `--longest` 时，文件夹在两个系统上都给出原因 `is a folder`。 | `main(["--longest", "sub"])` 和 `main(["--longest", "."])`。在 Windows 和 Linux 上运行。 | 每次都返回 `2`，标准输出为空。标准错误恰好是 `wordcount: sub: is a folder\n` 和 `wordcount: .: is a folder\n`。 |
| F07-T28 | 功能 | `main` | 带 `--longest` 时，进程无权读取的文件给出原因 `permission denied`。 | 仅限 Linux：`secret.txt` 内容为 `one two`，权限设为 `0o000`。`main(["--longest", "secret.txt"])`。出于 F07-T15 中的原因，在 Windows 上和进程以 root 运行时测试跳过。测试结束后恢复权限。 | 返回 `2`。标准输出为空。标准错误恰好是 `wordcount: secret.txt: permission denied\n`。 |
| F07-T29 | 单元 | `main` | 带 `--longest` 时，打开文件时的其他任何错误给出原因 `cannot read file`。 | 一个由 300 个 `a` 后接 `.txt` 组成的名字，超过两个系统对单个名字的长度限制。仅在 Windows 上，再加上 Windows 不允许的名字 `a?b.txt`。对每个名字调用 `main(["--longest", <name>])`。 | 每次都返回 `2`，标准输出为空。标准错误恰好是 `wordcount: <name>: cannot read file\n`，其中 `<name>` 是给出的参数原样。 |
| F07-T30 | 功能 | `main` | `--longest` 与 `--lines` 或 `--chars` 同用是用法错误，不论顺序和位置，且先于缺少 `FILE` 的检查，消息用 argparse 自己的话，先说后出现的选项（需求 Q16）。`--lines` 与 `--chars` 同用的消息不变。 | `notes.txt` 存在。按第 2 节的方式确定状态。七次调用：(a) `main(["--lines", "--longest", "notes.txt"])`，(b) `main(["--longest", "notes.txt", "--chars"])`，(c) `main(["--longest", "--chars", "notes.txt"])`，(d) `main(["--chars", "--longest", "notes.txt"])`，(e) `main(["--longest", "--lines", "notes.txt"])`，(f) `main(["--longest", "--lines"])`，以及 (g) `main(["--lines", "--chars", "notes.txt"])`。 | 每次都是用法错误，标准输出不含数字。标准错误的第二行恰好是 `wordcount: error: ` 后接：(a) `argument --longest: not allowed with argument --lines`；(b) 和 (c) `argument --chars: not allowed with argument --longest`；(d) `argument --longest: not allowed with argument --chars`；(e) 和 (f) `argument --lines: not allowed with argument --longest`；(g) `argument --chars: not allowed with argument --lines`。 |
| F07-T31 | 单元 | `main` | 带选项的其他错误命令行都是用法错误，而不是数字、文件错误或帮助文字：没有文件、短形式、缩写的名字、大小写不同、帮助、第二个文件，以及带值（需求 Q14）。 | `notes.txt` 存在。按第 2 节的方式确定状态。八次调用：`main(["--longest"])`、`main(["-L", "notes.txt"])`、`main(["--long", "notes.txt"])`、`main(["--lo", "notes.txt"])`、`main(["--LONGEST", "notes.txt"])`、`main(["--longest", "-h", "notes.txt"])`、`main(["--longest", "notes.txt", "notes.txt"])` 和 `main(["--longest=5", "notes.txt"])`。 | 每次都是用法错误。前七次调用时，标准错误的第二行恰好是：`wordcount: error: the following arguments are required: FILE`、`wordcount: error: unrecognized arguments: -L`、`wordcount: error: unrecognized arguments: --long`、`wordcount: error: unrecognized arguments: --lo`、`wordcount: error: unrecognized arguments: --LONGEST`、`wordcount: error: unrecognized arguments: -h` 和 `wordcount: error: unrecognized arguments: notes.txt`。对 `--longest=5`，只检查它以 `wordcount: error: ` 开头。没有一次调用写出数字、帮助文字或 `wordcount: notes.txt: <reason>` 这样的一行。 |
| F07-T32 | 单元 | `main` | 不论是否带 `--longest`，每个用法错误都显示 `<USAGE>`；不论 `sys.argv[0]` 是什么，每条消息中的程序名都是 `wordcount`。 | `notes.txt` 存在。`monkeypatch.setattr(sys, "argv", ["other-name.py"])`。按第 2 节的方式确定状态。先调用 `main([])`，再调用 `main(["--long", "notes.txt"])`，然后调用 `main(["--longest", "missing.txt"])`。 | 前两次是用法错误，第二行恰好是 `wordcount: error: the following arguments are required: FILE` 和 `wordcount: error: unrecognized arguments: --long`。第三次返回 `2`，向标准错误恰好写入 `wordcount: missing.txt: no such file\n`。 |
| F07-T33 | 单元 | `main` | 不带参数时，`main` 像控制台脚本那样读取 `sys.argv[1:]`；`argv` 可以是任何 `str` 序列。 | `notes.txt`。`monkeypatch.setattr(sys, "argv", ["wordcount", "--longest", "notes.txt"])`，然后调用 `main()` 和 `main(None)`。再调用 `main(("--longest", "notes.txt"))`，参数是元组。 | 每次都返回 `0`，向标准输出恰好写入 `9\n`。 |
| F07-T34 | 集成 | `wordcount` | 已安装的程序找出最长词，与 F07 原型一致；不带选项时仍统计词数。 | `notes.txt`、`greeting.txt` 和 `dashes.txt`。五次运行：`wordcount --longest notes.txt`、`wordcount notes.txt --longest`、`wordcount --longest greeting.txt`、`wordcount --longest dashes.txt` 和 `wordcount notes.txt`。 | 每次都以退出码 0 退出，标准错误为空。标准输出恰好是 `9<NL>`、`9<NL>`、`3<NL>`、`0<NL>` 和 `4<NL>`。 |
| F07-T35 | 集成 | `wordcount` | 已安装的程序以退出码 2 报告带 `--longest` 的文件错误，与 F07 原型和设计中的示例一致。 | 先是空的工作目录，然后是 `latin1.txt`。两次运行：`wordcount --longest missing.txt` 和 `wordcount --longest latin1.txt`。 | 每次都以退出码 2 退出，标准输出为空。标准错误先恰好是 `wordcount: missing.txt: no such file<NL>`，再恰好是 `wordcount: latin1.txt: not valid UTF-8<NL>`。 |
| F07-T36 | 集成 | `wordcount` | 带选项的错误命令行以退出码 2 退出，并显示 `<USAGE>`，与设计中的示例一致。 | `notes.txt`。按第 2 节的方式确定状态。四次运行：`wordcount --lines --longest notes.txt`、`wordcount --long notes.txt`、`wordcount -L notes.txt`，以及不带文件的 `wordcount --longest`。 | 每次都以退出码 2 退出，标准输出为空。标准错误恰好有两行，每行后接 `<NL>`：先是 `<USAGE>`，然后四次运行分别是 `wordcount: error: argument --longest: not allowed with argument --lines`、`wordcount: error: unrecognized arguments: --long`、`wordcount: error: unrecognized arguments: -L` 和 `wordcount: error: the following arguments are required: FILE`。 |
| F07-T37 | 集成 | `wordcount` | 带 `--longest` 时，参数按 Troy 输入的样子到达程序。 | `notes.txt` 的副本 `my notes.txt`、`日本語.txt` 和 `-notes.txt`。四次运行：在工作目录 `sub` 中 `wordcount --longest <notes.txt 的绝对路径>`；`wordcount --longest "my notes.txt"`，一个含空格的参数；`wordcount --longest 日本語.txt`；以及 `wordcount --longest -- -notes.txt`。 | 每次都以退出码 0 退出，向标准输出恰好写入 `9<NL>`，标准错误为空。 |

## 3. 性能用例

无。设计第 2.1、2.2 和 2.3 节没有设定性能指标，需求第 7.1 节也没有为项目设定任何性能指标（R14）。

## 4. 不测的内容

| 内容 | 原因 |
| --- | --- |
| 完整的 `wordcount FILE`、`--lines` 和 `--chars`：它们的数字、文件错误和用法错误。 | F04、F05 和 F06 的用例检查它们，并且在每个 PR 中都必须通过（R10）。为它们新增 F07 用例会对着模拟实现通过，这是 R09 不允许的。F07-T19、F07-T23、F07-T24 和 F07-T34 仍在 `--longest` 旁边检查它们，F07-T30 在 F07 用法行下检查 `--lines` 与 `--chars` 同用的消息。 |
| 哪个词是最长的。 | 设计只返回长度，命令也从不打印这个词（需求第 8 节）。F07-T09 检查同为最长时得到该长度。 |
| argparse 对 `--longest=VALUE` 以及一条命令中三个计数选项写出的消息。 | 设计把两者都交给 argparse 自己的话，只规定 `--longest=VALUE` 是用法错误。F07-T31 检查这一点。 |
| 程序缺陷：文件错误以外的异常传到调用方，Python 写出回溯，程序以退出码 1 退出。 | 与 F04 的方案相同：通过外部接口的任何输入都不会让统计函数抛出其他异常，要引发这种异常就得替换 cli 内部的函数。 |
| `count_longest` 异常消息的文字，例如设计示例中的 `[Errno 2] No such file or directory: 'missing.txt'`。 | 消息由 Python 生成，设计只承诺异常类型（需求 Q4）。F07-T13 到 F07-T17 检查类型。 |
| Windows 上不可读文件的 `PermissionError`。 | 在 Windows 上去掉文件的读权限需要访问控制列表，可移植的测试无法可靠地设置和恢复。F07-T15 和 F07-T28 在 Linux 上检查同一行为。 |
| Windows 对文件夹抛出 `IsADirectoryError` 还是 `PermissionError`。 | 设计允许 Windows 抛出其中任一个。F07-T14 在 Windows 上接受任一个，在 Linux 上要求 `IsADirectoryError`。 |
| `count_longest` 和 `count_words` 在 counting 内部共用同一份词规则和文件读取。 | 这是代码的构造方式，不是调用方看得到的行为。F07-T19 检查调用方看得到的部分：两者对哪些文件没有词的判断一致；F07-T02 到 F07-T08 检查词规则本身。 |
| `main` 从包导入统计函数，以及输出用 `write` 而不是 `print()`。 | 调用方都无法区分。前者由依赖检查器保证（R07），后者由 ruff 的 T20 规则保证（架构第 8 节）。 |
| 不是 `str` 的 `argv` 元素。 | 设计第 2.2 节只允许 `str` 元素，其他类型不在约定范围内。 |
| 在 Windows 上 `wordcount` 写入管道时，标准错误中 ASCII 以外文件名的字节。 | 与 F04 的方案相同：Python 此时用系统代码页编码标准错误，所以字节取决于机器。F07-T25 通过 `main` 检查这种消息的文字，F07-T37 检查这样的名字能到达程序。 |
| PowerShell 找到 `wordcount`、`$LASTEXITCODE`、PowerShell 去掉引号的方式，以及 F07 落地后需要重新安装项目。 | CI 在没有 PowerShell 的 Linux 上运行。v0.3 版本测试方案在 Troy 电脑的 Windows PowerShell 中运行这个命令。F07-T37 检查带引号的参数作为一个参数到达程序。 |
| 性能。 | 没有性能指标（R14）。 |

## 5. 与接口设计师的对齐记录

无。设计已回答本方案提出的所有用例问题：设计第 4 节中架构师实际运行 argparse 的结果，确认了 F07-T30、F07-T31 和 F07-T36 预期的用法行和每条消息；设计第 2.3 节的表格确定了 F07-T02 到 F07-T09 所依据的结果。架构师在设计第 4 节的说明中请测试经理让 F05-T13、F05-T14、F05-T15 和 F05-T23 在 F07 的代码合入前后都能通过。本方案第 2 节通过 F05 方案的 0.2 版做到这一点：它为用法行增加第三种状态，用 `--longest` 探测得到，方式与 F05 的方案现在判断 F06 的状态相同。设计的接口不变。F08 再次改变用法行。F08 设计第 4 节中架构师的说明 c 要求 F07 的用法行用例在每个 F08 PR 中都通过，且不同时接受两种用法行，所以 1.1 版在第 2 节加入 F08 的状态，用 `--again` 探测得到。F08 的测试 PR 为 F07-T30、F07-T31、F07-T32 和 F07-T36 加上这一探测，它们保留原名，其他内容不变。

## 6. 修改记录

| 版本 | 日期 | 修改 |
| --- | --- | --- |
| 0.1 | 2026-11-25 | 初稿。 |
| 1.0 | 2026-11-25 | Troy 批准。 |
| 1.1 | 2026-11-26 | F08 把 `--again` 加入用法行。用法错误的第一行现在是 `<USAGE>`：分支上没有 F08 的代码时为 F07 用法行，有时为 `usage: wordcount [--lines \| --chars \| --longest \| --again] FILE`，用 `--again` 探测得到。这只改变 F07-T30、F07-T31、F07-T32 和 F07-T36 预期的第一行，其他不变，所以它们在 F08 的代码合入前后都能通过（R10）。没有用例被废止。 |
