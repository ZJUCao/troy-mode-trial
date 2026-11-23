---
troy-doc: "F06-design"
lang: "zh-CN"
version: "1.0"
updated: "2026-11-23"
status: "Troy 已于 2026-11-23 批准"
mirror-of: "design.md"
---

# F06 字符数选项：接口设计

## 1. 功能

- 编号和名称：F06 Character count option（字符数选项）
- 需求：[docs/requirements.zh-CN.md](../../requirements.zh-CN.md#4-功能点)
- 硬依赖：F04
- 软依赖：无

## 2. 接口

F06 修改模块 cli 中 F04 的两个接口，并在模块 counting 中新增一个接口。2.1 节是 Troy 输入的命令，它新增选项 `--chars`。2.2 节是命令背后的函数。2.3 节是新的库函数 `count_chars`，它统计一个文件的字符数，`main` 在遇到 `--chars` 时调用它。

统计本身放在 counting 中，而不是 cli 中，理由有三。架构第 3 节说 cli 读取参数并调用 counting，而统计由 counting 负责。counting 已经实现了 `--chars` 必须与 `wordcount FILE` 一致的文件规则：跳过文件开头的一个字节顺序标记（需求 Q5、Q12），文件不存在或不是合法 UTF-8 时抛出 Python 自己的异常（Q4）。需求 Q6 也为行数解决过同一个问题：统计行数也是统计，放进 counting 不需要修改架构。统计字符同样是统计。

2.1 节中有三点是提议，由 Troy 接受或修改。每一点都在所在位置注明：用法行显示这个选项，缩写的选项名是错误的命令行，选项可以写在文件之后。

### 2.1 `wordcount`

- 模块：cli。`pyproject.toml` 中的控制台脚本 `wordcount = "troy_mode_trial.cli:main"` 保持 F04 声明的样子。
- 功能：像 F04 一样打印一个 UTF-8 文本文件的词数；加上 `--chars` 时，改为打印解码后文本的字符数（包括行尾），让 Troy 不写 Python 也能在 PowerShell 中统计字符数。

签名：

```text
usage: wordcount [--chars] FILE
```

参数：

| 名称 | 类型 | 含义 | 约束 |
| --- | --- | --- | --- |
| `--chars` | 选项，不带值的开关 | 打印 `FILE` 的字符数，而不是词数。不加它时，命令打印词数，与 F04 完全相同。 | 可选。只有全名 `--chars`，没有 `-c` 之类的短形式（需求 Q10）。缩写的名字，例如 `--char` 或 `--ch`，是错误的命令行（见下面的提议 2）。选项可以写在 `FILE` 之前或之后：`wordcount --chars notes.txt` 与 `wordcount notes.txt --chars` 效果相同（见下面的提议 3）。写两次，例如 `wordcount --chars --chars notes.txt`，与写一次相同，统计一次字符数。`--chars=VALUE` 是错误的命令行。 |
| `FILE` | 一个命令行参数 | 要统计的文件路径，可以是绝对路径，也可以是相对当前工作目录的路径。 | 与 F04 设计 2.1 节相同：恰好一个参数，指向一个存在、可读的普通文件，内容是合法的 UTF-8。以 `-` 开头的路径放在 `--` 之后，例如 `wordcount --chars -- -notes.txt`。`--` 之后的 `--chars` 是文件名，不是选项。 |

这个命令仍然没有 `-h` 或 `--help`；在 F05 加入 `--lines` 之前，除 `--chars` 外没有其他选项（需求第 8 节）。

**提议 1，用法行，由 Troy 接受或修改。** 用法行显示这个选项：`usage: wordcount [--chars] FILE`，取代 F04 的 `usage: wordcount FILE`。命令没有帮助，所以用法行是命令自己唯一说出其选项的地方。另一种做法是保留 F04 的用法行，这样选项在任何地方都不会显示。采用这个提议时，F04 中逐字检查用法行的测试要修改其期望的用法行，见第 3 节。

**提议 2，缩写的选项名，由 Troy 接受或修改。** 只有完整的 `--chars` 才是这个选项。`wordcount --char notes.txt` 和 `wordcount --ch notes.txt` 是错误的命令行：用法错误，第二行是 `wordcount: error: unrecognized arguments: --char`，退出码 2。没有这条规则时，argparse 会把选项名的任何唯一开头，例如 `--c`，当作这个选项。这个提议让命令行只表示 Troy 写下的意思，也让 `--lines` 和 `--chars` 不必依赖哪些缩写恰好唯一。

**提议 3，选项写在文件之后，由 Troy 接受或修改。** `wordcount notes.txt --chars` 统计字符数，与 `wordcount --chars notes.txt` 相同。argparse 就是这样读命令行的，很多命令也是这样。另一种做法是把它当作用法错误，这需要额外的代码，而且对一个意思很清楚的命令行报错。

- 返回值：成功时退出码 0。标准输出是十进制的计数，不带符号、填充或分隔符，后跟一个换行符；标准错误为空，与 F04 设计 2.1 节相同。
  - 不加 `--chars` 时，计数是 `count_words(FILE)` 的返回值，与 F04 相同。
  - 加 `--chars` 时，计数是 `count_chars(FILE)` 的返回值（2.3 节）：文件按 UTF-8 解码、去掉文件开头的一个字节顺序标记之后，文本中 Unicode 码位的个数。每个行尾都按文件中的样子计数：`\n` 是一个字符，`\r` 是一个，`\r\n` 是两个（需求 Q11）。所以 `你` 是一个字符，虽然它占三个字节；同一个文件在 Windows 和 Linux 上得到相同的计数。

错误：

每种错误都让标准输出保持为空，只写标准错误。加 `--chars` 时的文件错误，与 `wordcount FILE` 对同一个文件给出的消息和退出码完全相同（需求 F06 和 Q8）：一行 `wordcount: <FILE>: <reason>`，后跟一个换行符，退出码 2。`<FILE>` 和五个原因文本与 F04 设计 2.1 节相同，没有变化。

| 错误 | 何时发生 |
| --- | --- |
| 退出码 2，原因 `no such file` | 与 F04 设计 2.1 节相同：`FILE` 处没有文件或文件夹，`FILE` 是空字符串，或者路径中的某个文件夹不存在或是文件。 |
| 退出码 2，原因 `is a folder` | 与 F04 设计 2.1 节相同：`FILE` 指向文件夹。 |
| 退出码 2，原因 `permission denied` | 与 F04 设计 2.1 节相同：进程无权读取该文件。 |
| 退出码 2，原因 `not valid UTF-8` | 与 F04 设计 2.1 节相同：文件内容不是合法的 UTF-8。加 `--chars` 时，命令检查整个文件，所以非法字节出现在合法文本之后的文件也是这个错误，不打印计数。 |
| 退出码 2，原因 `cannot read file` | 与 F04 设计 2.1 节相同：打开或读取文件时出现的其他 `OSError`。 |
| 退出码 2，用法行 | 命令行没有 `FILE`、有多于一个参数、有 `--chars` 以外的选项、有 `--char` 这样的缩写、有 `-c`、`-h` 或 `--chars=VALUE`。argparse 先写提议 1 的用法行 `usage: wordcount [--chars] FILE`，再写一行 argparse 自己措辞的 `wordcount: error: <message>`，例如 `wordcount --chars` 得到 `wordcount: error: the following arguments are required: FILE`，`wordcount -c notes.txt` 得到 `wordcount: error: unrecognized arguments: -c`。 |

其他任何异常都是缺陷，与 F04 相同：Python 把回溯信息写到标准错误，并以退出码 1 退出（架构第 6 节）。

一个命令中有两个计数选项，例如 `wordcount --lines --chars FILE`，是用法错误，退出码 2（需求 Q13）。只有 F06 时没有第二个计数选项，所以在 F05 加入 `--lines` 之前，`--lines` 只是一个未知选项。为了让 Q13 成立而不必再改 `--chars`，`--chars` 是一组互斥计数选项的第一个成员：后来的功能加入这一组的选项，例如 F05 的 `--lines`，与 `--chars` 一起出现时就是用法错误。这种情况下的用法行和消息由 F05 的设计确定。

- 副作用：与 F04 设计 2.1 节相同：命令以只读方式打开 `FILE`，并在退出前关闭它；只写标准输出和标准错误；不写、不发送、不保存任何数据。F06 合入后，项目要重新安装一次，例如运行 `uv pip install -e . --no-deps`，这个选项才会存在。
- 性能指标：无

示例：

当前文件夹中的 `notes.txt` 是 UTF-8 文件，有两行 `Hello world` 和 `  troy-mode  trial`，每行以 `\n` 结尾。`hello.txt` 只有一行 `你好`，以 `\r\n` 结尾：8 个字节，但只有 4 个字符。`latin1.txt` 以 Latin-1 编码保存 `café au lait`。

```text
PS> wordcount --chars notes.txt
31
PS> wordcount notes.txt --chars
31
PS> wordcount notes.txt
4
PS> wordcount --chars hello.txt
4
PS> wordcount --chars missing.txt
wordcount: missing.txt: no such file
PS> $LASTEXITCODE
2
PS> wordcount --chars latin1.txt
wordcount: latin1.txt: not valid UTF-8
PS> $LASTEXITCODE
2
PS> wordcount --char notes.txt
usage: wordcount [--chars] FILE
wordcount: error: unrecognized arguments: --char
PS> $LASTEXITCODE
2
```

### 2.2 `main`

- 模块：cli，位于 `src/troy_mode_trial/cli.py`，与 F04 设计 2.2 节相同。测试以 `from troy_mode_trial.cli import main` 导入它。
- 功能：运行一次 2.1 节的 `wordcount` 命令：读取参数，通过 `count_words` 统计文件的词数，或者在参数中有 `--chars` 时通过 `count_chars` 统计字符数，写出结果或错误，并返回退出码。它从包 `troy_mode_trial` 导入这两个函数，从不从 `troy_mode_trial.counting` 导入（架构第 4 节）。

签名：

```python
def main(argv: Sequence[str] | None = None) -> int:
```

签名不变。`Sequence` 是 `collections.abc.Sequence`。

参数：

| 名称 | 类型 | 含义 | 约束 |
| --- | --- | --- | --- |
| `argv` | `Sequence[str] \| None` | 程序名之后的命令行参数，例如 `["--chars", "notes.txt"]` 或 `["notes.txt"]`。`None` 表示 `sys.argv[1:]`，控制台脚本传的就是它。 | 每一项都是 `str`。参数规则就是 2.1 节中 `--chars` 和 `FILE` 的规则。 |

- 返回值：`int`，退出码，与 F04 设计 2.2 节相同。向标准输出写出 2.1 节的计数和一个换行符后返回 `0`。向标准错误写出一行 `wordcount: <FILE>: <reason>` 后返回 `2`。不论 `sys.argv[0]` 是什么，每条消息中的程序名都是 `wordcount`。

错误：

| 错误 | 何时发生 |
| --- | --- |
| 代码为 2 的 `SystemExit` | 参数错误，见 2.1 节“错误”表的最后一行。argparse 把用法行和它的消息写到标准错误，并抛出 `SystemExit(2)`，所以 `main` 不返回。 |
| 其他任何异常 | 缺陷。`main` 只捕获 `count_words` 或 `count_chars` 抛出的 `OSError` 及其子类和 `UnicodeDecodeError`，其他异常都传给调用者。 |

- 副作用：与 F04 设计 2.2 节相同：用 `sys.stdout.write` 和 `sys.stderr.write` 写出，而不是 `print()`（架构第 8 节）；按 2.1 节的说明读取文件；不改变任何全局状态，所以测试可以在一个进程中多次调用它。
- 性能指标：无

示例：

`notes.txt` 和 `hello.txt` 是 2.1 节示例中的文件。

```python
>>> from troy_mode_trial.cli import main
>>> main(["--chars", "notes.txt"])
31
0
>>> main(["--chars", "hello.txt"])
4
0
>>> main(["notes.txt"])
4
0
>>> main(["--chars", "missing.txt"])  # writes to standard error
wordcount: missing.txt: no such file
2
>>> main(["--chars"])
usage: wordcount [--chars] FILE
wordcount: error: the following arguments are required: FILE
Traceback (most recent call last):
  ...
SystemExit: 2
```

### 2.3 `count_chars`

- 模块：counting。调用者从包 `troy_mode_trial` 导入它，该包由 `src/troy_mode_trial/__init__.py` 定义，与 `count_words` 和 `count_lines` 并列。本设计不在 `src/troy_mode_trial/` 下新增文件。
- 功能：读取一个 UTF-8 文本文件，返回解码后文本的字符数（包括行尾），一个字符就是一个 Unicode 码位。

签名：

```python
def count_chars(path: str | os.PathLike[str]) -> int:
```

参数：

| 名称 | 类型 | 含义 | 约束 |
| --- | --- | --- | --- |
| `path` | `str \| os.PathLike[str]` | 要统计的文件路径，可以是绝对路径，也可以是相对当前工作目录的路径。`pathlib.Path` 是 `os.PathLike[str]`，可以接受。 | 指向一个存在、可读的普通文件，内容是合法的 UTF-8。不接受 `bytes` 路径。 |

- 返回值：`int`，字符数，0 或更多。函数把整个文件按 UTF-8 解码，并去掉文件开头的一个字节顺序标记（U+FEFF）（需求 Q12）。结果是剩下文本的码位个数，也就是这段文本的 `len()`。

  字符的规则：

  - 行尾按文件中的样子计数，不做转换（需求 Q11）：`\n` 是一个字符，`\r` 是一个，`\r\n` 是两个。Python 默认的文本模式会把 `\r\n` 和 `\r` 转成 `\n`，所以函数读取时必须关闭行尾转换。
  - 每个码位都计一次，不论它是什么：字母、数字、空白、控制字符、U+3000 或表情符号。由几个码位组成的字符按码位分别计数，例如写成 `e` 加组合重音符 U+0301 的 `é` 计为 2，用 U+200D 把几个表情符号连成的表情计为多于 1。
  - 只去掉最开头的一个字节顺序标记。其他位置的 U+FEFF，包括紧跟在第一个之后的第二个，都计为一个字符。
  - 空文件，或只有字节顺序标记的文件，返回 0。

  | 文件字节（以文本表示） | 结果 |
  | --- | --- |
  | （空） | `0` |
  | `EF BB BF`（只有字节顺序标记） | `0` |
  | `Hello world\n  troy-mode  trial\n` | `31` |
  | `EF BB BF` 之后是 `Hello world\r\n  troy-mode  trial\r\n` | `33` |
  | `你好\r\n`（8 个字节） | `4` |
  | `one\rtwo\r\nthree\nfour` | `19` |
  | `EF BB BF EF BB BF` 之后是 `a` | `2` |
  | `e` 之后是 U+0301 | `2` |

错误：

函数不定义自己的异常（需求 Q4）。它让 Python 自己的异常传给调用者，错误表与 `count_words` 和 `count_lines` 相同。

| 错误 | 何时发生 |
| --- | --- |
| `FileNotFoundError` | `path` 处没有文件，或者 `path` 是空字符串。 |
| `IsADirectoryError` 或 `PermissionError` | `path` 指向文件夹。Linux 抛出 `IsADirectoryError`，Windows 抛出 `PermissionError`。 |
| `PermissionError` | 进程无权读取该文件。 |
| `UnicodeDecodeError` | 文件中任何一个字节不是合法的 UTF-8，不论它在什么位置。 |
| `TypeError` | `path` 既不是 `str` 也不是 `os.PathLike[str]`，例如 `bytes` 或 `int`。 |

- 副作用：函数以只读方式打开文件，并在返回或抛出异常之前关闭它。它不写、不发送、不保存任何数据。
- 性能指标：无

示例：

`notes.txt` 和 `hello.txt` 是 2.1 节示例中的文件。`windows.txt` 的字节是 `EF BB BF`，之后是 `Hello world\r\n  troy-mode  trial\r\n`，与记事本保存的一样。

```python
>>> from pathlib import Path
>>> from troy_mode_trial import count_chars
>>> count_chars("notes.txt")
31
>>> count_chars("hello.txt")
4
>>> count_chars(Path("windows.txt"))
33
>>> count_chars("missing.txt")
Traceback (most recent call last):
  ...
FileNotFoundError: [Errno 2] No such file or directory: 'missing.txt'
```

## 3. 对已有接口的修改

需求 6.0 把 F06 作为新功能加入，包括选项 `--chars` 和决定 Q10 到 Q13，见已经合并的 [docs] PR “[docs] Change the requirements: add the wordcount --chars option”（提交 `fc2bb26`）。F04 已经验收，所以 F06 只按下面的方式修改它的接口：

1. `wordcount`（F04 设计 2.1 节）新增选项 `--chars`。不加选项的 `wordcount FILE` 打印的计数、错误行和退出码都与以前相同。
2. 如果 Troy 接受 2.1 节的提议 1，用法行从 `usage: wordcount FILE` 改为 `usage: wordcount [--chars] FILE`。每个用法错误的其余部分不变：退出码 2，标准输出为空，第二行是 `wordcount: error: <message>`。F04 的测试计划用“第一行恰好是 `usage: wordcount FILE`”定义用法错误，用例 F04-T11、F04-T12、F04-T13 和 F04-T21 逐字检查这一行。这些用例把期望的第一行改为 `usage: wordcount [--chars] FILE`，其他不变。由测试经理在 F06 的测试计划 PR 中修改。如果 Troy 保留 F04 的用法行，F04 的测试用例都不变。
3. `main`（F04 设计 2.2 节）保持签名不变。它现在接受 `argv` 中的 `--chars`，此时调用 `count_chars`。
4. `src/troy_mode_trial/__init__.py` 在 `count_lines` 和 `count_words` 旁边导出 `count_chars`。这只新增一个名字，不改变已有的名字。`count_words` 和 `count_lines` 保持签名、行为和错误不变，`__init__.py` 仍然不导入 cli。

F05 同时给同一个命令加入 `--lines`，也会修改用法行。F05 和 F06 中后合入的那个保留另一个的选项，它的用法行同时显示两个选项。

## 4. 架构师审查

| 项目 | 结果 | 备注 |
| --- | --- | --- |
| 符合模块划分和数据模型 | 通过 | `wordcount` 和 `main` 仍在 cli 中，位于 `src/troy_mode_trial/cli.py`。`count_chars` 放在 counting 中，位于 `src/troy_mode_trial/counting.py`，并从 counting 的外部接口 `src/troy_mode_trial/__init__.py` 导出。这两个文件都已在 counting 的“拥有”列中，本设计不在 `src/troy_mode_trial/` 下新增文件。`main` 从包导入 `count_chars`，符合架构第 4 节。本设计不需要修改架构。架构 3.0 中 counting 已经有 `count_lines`，再加一个统计函数与需求 Q6 解决过的情况相同。模块表中“统计一段文字的词数”这句简短说明可以在下次修改架构时放宽，但 R07 的检查不依赖它。带 `allow_abbrev=False` 和互斥组的 `argparse` 仍是标准库（ADR-0001），所以本设计不增加依赖。架构没有定义数据模型。 |
| 遵守错误处理和命名约定 | 通过 | `count_chars` 不定义自己的异常。它与 `count_words` 和 `count_lines` 一样，让 Python 自己的异常传出（架构第 6 节，需求 Q4）。`main` 仍然只在两个统计调用周围捕获 `OSError` 及其子类和 `UnicodeDecodeError`；加 `--chars` 时写出同样的一行 `wordcount: <FILE>: <reason>`，退出码 2（ADR-0002）。错误的命令行以退出码 2 和用法行结束，退出码 1 仍然只表示缺陷，标准输出只有计数和一个换行符，用 `write` 写出（第 8 节）。`count_chars` 沿用 `count_<thing>(path)` 的命名和两个已有函数的路径类型。第 1 轮中我运行了 argparse（Python 3.14.3；这台机器上没有项目的 Python 3.13 环境），只有一个 `--chars` 开关，设置 `prog="wordcount"`、`add_help=False` 和 `allow_abbrev=False`，单独添加和放在互斥组中各试一次。两种都给出用法行 `usage: wordcount [--chars] FILE`，并且 `--chars FILE`、`FILE --chars`、`--char`、`--ch`、`--c`、`-c`、`-h`、不带文件的 `--chars`、`--chars=VALUE`、`--chars --chars`、`--chars -- -n.txt` 和 `-- --chars` 的结果都与设计所说相同。我还手工核对了 2.3 节表格的八行和示例中的计数。 |
| 不和已有接口重复 | 通过 | 没有已有接口统计字符数。`main` 通过 `count_chars` 统计，自己不统计任何东西。`count_chars` 与 `count_words`、`count_lines` 只共用读取规则，这是代码层面的事，不是第二个接口。 |
| 只依赖排序在前面的功能 | 通过 | F06 只依赖 F04，并经由它依赖 F03 和 F01。三者在顺序（F01、F03、F04、F06、F02、F05）中都排在 F06 之前，并且已在 Troy 的设备上可用。F06 不使用 F02 和 F05。`--lines` 只作为在 F05 加入之前的未知选项出现。 |
| 不在模块之间增加隐性耦合 | 通过 | cli 只依赖 `count_chars` 写明的内容：签名、`int` 结果和错误表中的异常，这些异常架构第 6 节已经列出。互斥的计数选项组在 cli 中，counting 不知道任何选项。包的 `__init__.py` 只新增名字 `count_chars`，仍然不导入 cli。`main` 不保存全局状态。 |
| 修改已实现的接口时走了变更流程 | 通过 | F04 已经验收，需求 6.0（提交 `fc2bb26`，Troy 已批准）给它的命令加入选项 `--chars`，所以修改走的是需求变更流程。第 3 节列出了每一处修改：新选项，Troy 接受提议 1 时的新用法行，`main` 不变的签名，以及新的导出。我核对了 F04 的测试计划和 `tests/test_cli.py`。F04-T11、F04-T12、F04-T13 和 F04-T21 正是依赖第一行 `usage: wordcount FILE` 的用例，要么通过测试计划对用法错误的定义，要么逐字检查。F04 的其他用例都不变。v0.2 中错误命令行的场景只检查标准错误以 `usage:` 开头，所以保持不变。`count_words` 和 `count_lines` 不变。 |
| 给 Troy 的摘要和设计说的一致，并列出了需要 Troy 决定的每一件事 | 通过 | 摘要与设计一致。它讲了新选项和它的计数：一个码位，`你好` 加 Windows 行尾是 4，Windows 行尾算 2，字节顺序标记不计。它还说词数、错误行和退出码 2 保持不变，提到新的库函数，并说要重新安装项目。它的三件事就是 2.1 节的提议 1、2、3，顺序相同，各带设计的推荐和理由。设计没有其他待定的选择。两条风险与 2.3 节（由几个码位组成的字符）和第 3 节（F05 也修改用法行）一致。每种语言都在 2,000 字符以内，中文约 800，英文约 1,997，不含内部编号。功能编号是允许的。 |

| 轮次 | 问题 | 解决方式 |
| --- | --- | --- |
| 1 | 没有阻塞问题。按界面设计师的请求确认：本设计不需要修改架构（第 1 项）。四条说明，不阻塞。给界面设计师：英文摘要约 1,997 字符，上限 2,000，所以以后各轮加入任何文字，都要在摘要其他地方相应缩短。第 3 节也可以在需求 PR 的标题和提交旁边写出它的编号 #63。给界面设计师和主会话：2.1 节说 `--lines` 与 `--chars` 同时出现时的消息由 F05 的设计确定。这只在 F05 后合入时成立。F05 修改同一个 `wordcount` 和 `main`，所以批次计划应在本设计合并（F06 1/6）之后再开始 F05。给开发者：在解析器中把计数选项建成互斥组，并设置 `allow_abbrev=False`。用 `encoding="utf-8-sig"` 和 `newline=""` 读取，返回文本的 `len()`，与已有函数共用路径检查。更新 `main` 文档注释中的用法行，并让 `main` 不超过 50 行（R04），例如用一个辅助函数选择统计函数。给测试经理：只修改 F04-T11、F04-T12、F04-T13 和 F04-T21 期望的第一行。每个文件都以二进制方式写入，让 `\r\n` 作为两个字符传给 `count_chars`。 | 第 1 轮批准。 |

## 5. 修改记录

| 版本 | 日期 | 修改 |
| --- | --- | --- |
| 0.1 | 2026-11-23 | 初稿。 |
| 1.0 | 2026-11-23 | Troy 批准。 |
