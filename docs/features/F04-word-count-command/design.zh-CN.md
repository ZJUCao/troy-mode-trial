---
troy-doc: "F04-design"
lang: "zh-CN"
version: "1.0"
updated: "2026-11-14"
status: "Troy 已于 2026-11-14 批准"
mirror-of: "design.md"
---

# F04 词数统计命令：接口设计

## 1. 功能

- 编号和名称：F04 Word count command（词数统计命令）
- 需求：[docs/requirements.zh-CN.md](../../requirements.zh-CN.md#4-功能点)
- 硬依赖：F03
- 软依赖：无

## 2. 接口

F04 新增两个接口，都属于模块 cli。该模块拥有新文件 `src/troy_mode_trial/cli.py`（架构第 3 节，ADR-0001）。2.1 节是 Troy 输入的命令。2.2 节是命令背后的函数，由控制台脚本调用，测试也可以在进程内调用它。

### 2.1 `wordcount`

- 模块：cli。`pyproject.toml` 在表 `[project.scripts]` 中以 `wordcount = "troy_mode_trial.cli:main"` 声明这个命令。安装器（uv 或 pip）在环境的脚本目录中生成程序 `wordcount`，在 Windows 上是 `wordcount.exe`。
- 功能：打印一个 UTF-8 文本文件的词数，按 F03 的方式统计，让 Troy 不写 Python 也能在 PowerShell 或其他 shell 中统计词数。

签名：

```text
usage: wordcount FILE
```

参数：

| 名称 | 类型 | 含义 | 约束 |
| --- | --- | --- | --- |
| `FILE` | 一个命令行参数 | 要统计的文件路径，可以是绝对路径，也可以是相对当前工作目录的路径。 | 恰好一个参数。它指向一个存在、可读的普通文件，内容是合法的 UTF-8。含空格的路径按 shell 的要求加引号，例如在 PowerShell 中写 `wordcount 'my notes.txt'`。以 `-` 开头的路径放在 `--` 之后，例如 `wordcount -- -notes.txt`，否则 argparse 会把这样的参数当作选项。 |

这个命令没有选项（需求第 8 节），也没有 `-h` 或 `--help`：`wordcount -h` 是错误的命令行，见“错误”表。

- 返回值：退出码 0，标准输出是十进制的词数，不带符号、填充或分隔符，后跟一个换行符。词数就是 `count_words(FILE)` 的返回值（F01 设计 2.1 节，经 F03 设计 3.1 节修改）。标准错误为空。Python 在 Linux 上把换行符写成 `\n`，在 Windows 上写成 `\r\n`。

错误：

每种错误都让标准输出保持为空，只写标准错误。文件错误时，命令恰好写一行 `wordcount: <FILE>: <reason>`，后跟一个换行符，并以退出码 2 退出。退出码 2 是 Troy 在 PR #39 中定的，因为他的脚本把 2 当作错误；原型显示的是退出码 1。`<FILE>` 是程序收到的参数，也就是 shell 去掉引号之后的样子，不是绝对路径。`<reason>` 是下表中的固定文本之一，在 Windows 和 Linux 上相同。文件错误和错误的命令行都以退出码 2 退出，只有标准错误中的文字能区分二者。原型只给出了 `no such file`。其他四个原因文本，以及在 Windows 上对文件夹报 `is a folder` 而不是 `permission denied`，是本设计的提议，由 Troy 接受或修改。

| 错误 | 何时发生 |
| --- | --- |
| 退出码 2，原因 `no such file` | `FILE` 处没有文件或文件夹，`FILE` 是空字符串，或者路径中的某个文件夹不存在或是文件。在 Python 中是 `FileNotFoundError` 或 `NotADirectoryError`。 |
| 退出码 2，原因 `is a folder` | `FILE` 指向文件夹。在 Python 中，Linux 上是 `IsADirectoryError`，Windows 上是路径指向已有文件夹时的 `PermissionError`。 |
| 退出码 2，原因 `permission denied` | 进程无权读取该文件。在 Python 中是路径不指向文件夹时的 `PermissionError`。 |
| 退出码 2，原因 `not valid UTF-8` | 文件内容不是合法的 UTF-8。在 Python 中是 `UnicodeDecodeError`。 |
| 退出码 2，原因 `cannot read file` | 打开或读取文件时出现的其他 `OSError`，例如 Windows 不允许的文件名 `a?b.txt`。 |
| 退出码 2，用法行 | 命令行没有 `FILE`、有多于一个参数，或者有 argparse 当作选项的参数，例如 `-h`。argparse 先写用法行 `usage: wordcount FILE`，再写一行 `wordcount: error: <message>`，例如 `wordcount: error: the following arguments are required: FILE` 或 `wordcount: error: unrecognized arguments: notes.txt`。消息文本由 argparse 自己给出。 |

其他任何异常都是缺陷（架构第 6 节）。命令不捕获它：Python 把回溯信息写到标准错误，并以退出码 1 退出。所以退出码 1 表示缺陷，绝不表示文件错误或错误的命令行。Ctrl+C 也不捕获。

- 副作用：命令以只读方式打开 `FILE`，并在退出前关闭它。它只写标准输出和标准错误，不写任何文件，也不发送或保存任何数据（需求第 7 节）。F04 合入后，项目要重新安装一次，例如运行 `uv pip install -e . --no-deps`，命令才会存在；只有在环境 `troy-mode-trial` 激活时，或者它的脚本目录在 `PATH` 中时，PowerShell 才能找到它（ADR-0001，后果）。
- 性能指标：无

示例：

当前文件夹中的 `notes.txt` 是 UTF-8 文件，含两行 `Hello world` 和 `  troy-mode  trial`。`latin1.txt` 以 Latin-1 编码保存 `café au lait`。

```text
PS> wordcount notes.txt
4
PS> wordcount missing.txt
wordcount: missing.txt: no such file
PS> $LASTEXITCODE
2
PS> wordcount latin1.txt
wordcount: latin1.txt: not valid UTF-8
PS> $LASTEXITCODE
2
PS> wordcount
usage: wordcount FILE
wordcount: error: the following arguments are required: FILE
PS> $LASTEXITCODE
2
```

### 2.2 `main`

- 模块：cli，位于 `src/troy_mode_trial/cli.py`。在产品中，2.1 节的控制台脚本是它唯一的调用方。没有模块导入 cli，`src/troy_mode_trial/__init__.py` 也不导入它（架构第 4 节）。测试用 `from troy_mode_trial.cli import main` 导入它。
- 功能：运行一次 2.1 节的 `wordcount` 命令：读取参数，通过从包 `troy_mode_trial` 导入的 `count_words` 统计文件的词数，写出结果或错误，并返回退出码。

签名：

```python
def main(argv: Sequence[str] | None = None) -> int:
```

`Sequence` 是 `collections.abc.Sequence`。

参数：

| 名称 | 类型 | 含义 | 约束 |
| --- | --- | --- | --- |
| `argv` | `Sequence[str] \| None` | 程序名之后的命令行参数，例如 `["notes.txt"]`。`None` 表示 `sys.argv[1:]`，控制台脚本传的就是它。 | 每一项都是 `str`。参数规则与 2.1 节的 `FILE` 相同。 |

- 返回值：`int`，退出码。向标准输出写出词数和一个换行符之后返回 `0`。向标准错误写出一行 `wordcount: <FILE>: <reason>` 之后返回 `2`，原因文本见 2.1 节。控制台脚本把返回的退出码传给 `sys.exit`。无论 `sys.argv[0]` 是什么，每条消息中的程序名都是 `wordcount`。

错误：

| 错误 | 何时发生 |
| --- | --- |
| 退出码为 2 的 `SystemExit` | 参数错误，见 2.1 节“错误”表的最后一行。argparse 把用法行和它的消息写到标准错误，并抛出 `SystemExit(2)`，所以 `main` 不返回。 |
| 其他任何异常 | 缺陷。`main` 只捕获 counting 抛出的 `OSError` 及其子类和 `UnicodeDecodeError`，其他异常都传给调用方。 |

- 副作用：用 `sys.stdout` 和 `sys.stderr` 的 `write` 方法写输出，不用 `print()`（架构第 8 节），并按 2.1 节读取文件。它不改变全局状态，所以测试可以在同一个进程中多次调用它。
- 性能指标：无

示例：

`notes.txt` 是 2.1 节示例中的文件。

```python
>>> from troy_mode_trial.cli import main
>>> main(["notes.txt"])
4
0
>>> main(["missing.txt"])  # writes to standard error
wordcount: missing.txt: no such file
2
>>> main([])
usage: wordcount FILE
wordcount: error: the following arguments are required: FILE
Traceback (most recent call last):
  ...
SystemExit: 2
```

## 3. 对已有接口的修改

无。需求 4.0 在已合并的 [docs] PR [#36](https://github.com/ZJUCao/troy-mode-trial/pull/36) 中把 F04 作为新功能加入，架构 2.0 在 [#37](https://github.com/ZJUCao/troy-mode-trial/pull/37) 中加入了模块 cli。`count_words` 的签名、行为和错误都不变，`src/troy_mode_trial/__init__.py` 的导出不变，也不导入 cli。没有已有测试用例被修改或退役。

## 4. 架构师审查

| 项目 | 结果 | 备注 |
| --- | --- | --- |
| 符合模块划分和数据模型 | 通过 | 两个接口都属于模块 cli，该模块拥有 `src/troy_mode_trial/cli.py`（架构第 3 节，ADR-0001）。设计没有在 `src/troy_mode_trial/` 下新增其他文件。`main` 只通过包 `troy_mode_trial` 使用 counting，符合架构第 4 节，也没有模块导入 cli。控制台脚本条目 `wordcount = "troy_mode_trial.cli:main"` 与技术栈中的一致，hatchling 已经是构建后端。架构没有定义数据模型，命令也不保存数据。 |
| 遵守错误处理和命名约定 | 通过 | `main` 只在调用 counting 的地方捕获 `OSError` 及其子类和 `UnicodeDecodeError`。文件错误时，它向标准错误写一行 `wordcount: <FILE>: <reason>` 并返回 2，符合架构 3.0 第 6 节和 ADR-0002 的要求。它让 argparse 以退出码 2 和用法行退出，成功时返回 0，其他异常都放行，由 Python 以退出码 1 退出。这些正是 ADR-0002 列出的退出码：0 表示得到词数，2 表示文件错误或错误的命令行，1 只表示缺陷。2.1 节也写明只有标准错误能区分文件错误和错误的命令行，与第 6 节一致。标准输出只有词数和一个换行符，输出用 `write` 而不是 `print()`（第 8 节）。设计确定了原因文本和 `main` 的签名，这正是第 6 节留给它的。`main` 和 `argv` 符合 Python 的命名习惯。第 1 轮中我用 argparse 试了没有文件、两个文件、`-h` 和 `-- -n.txt`：每种情况的用法行、消息和退出码都和设计说的一致。 |
| 不和已有接口重复 | 通过 | 项目还没有命令行接口。`main` 通过已有的 `count_words` 计数，自己不统计词数。 |
| 只依赖排序在前面的功能 | 通过 | F04 只依赖 F03，并通过 F03 依赖 F01。两者在顺序（F01、F03、F04、F02）中都排在 F04 前面，并且已经可以在 Troy 的设备上使用。F04 不使用 F02。 |
| 不在模块之间增加隐性耦合 | 通过 | cli 只依赖 `count_words` 写明的内容：签名、`int` 结果和异常。`NotADirectoryError` 和其他 `OSError` 情况都是架构已经提到的子类。在 Windows 上遇到 `PermissionError` 时判断路径是否为文件夹，这一步留在 cli 中。`main` 不保存全局状态，包的 `__init__.py` 也不导入 cli。 |
| 修改已实现的接口时走了变更流程 | 通过 | 没有修改已实现的接口。`count_words` 和 `src/troy_mode_trial/__init__.py` 的导出都不变，没有测试用例被修改。新的 `[project.scripts]` 表来自架构 2.0，Troy 已在 [docs] PR #37 中批准。文件错误的退出码只在本设计的草稿中改变，没有改动已实现的接口，而且架构先改了：Troy 已在 [docs] PR #40 中批准架构 3.0 和 ADR-0002。 |
| 给 Troy 的摘要和设计说的一致，并列出了需要 Troy 决定的每一件事 | 通过 | 摘要与第 2 节一致：输出、每种文件错误的错误行和退出码 2 且提示不变、用法行同样是退出码 2、退出码 1 只表示缺陷、`-h`、`--`、按输入显示的文件名、计数函数不变，以及需要重新安装。风险也一致：脚本目录在 `PATH` 中、共用的退出码 2 只能靠提示文字区分，以及原型中的退出码 1（2.1 节记下了这个差别）。需要 Troy 决定的唯一一件事是五个原因文本（包括 Windows 上的 `is a folder`），正是设计标为提议的内容，并附有推荐。设计没有其他未定的选择。两种语言都少于 2,000 个字符，英文约 1,740 个，中文约 890 个，也没有内部编号；功能编号 F04 是允许的。 |

| 轮次 | 问题 | 解决方式 |
| --- | --- | --- |
| 1 | 没有阻塞性问题。有三条不阻塞的备注。给接口设计师，如果设计因其他原因要修改：摘要的风险可以补充一句，环境的脚本目录在 `PATH` 中时也能找到命令，和 2.1 节一致。给开发者：在 `main` 内部用 `prog="wordcount"` 和 `add_help=False` 构建解析器，并让 `main` 不超过 50 行（R04），例如用一个私有辅助函数把异常映射到原因文本。在 Windows 上，只有遇到 `PermissionError` 之后才判断路径是否为文件夹。给测试经理：`is a folder` 和 `permission denied` 两种情况在 Windows 和 Linux 上表现不同，测试计划需要为每个系统各写一个用例，或者写明跳过的理由。 | 第 1 轮批准。 |
| 2 | 没有阻塞性问题。0.2 版按 Troy 在 PR #39 中的要求，让每种文件错误都以退出码 2 而不是 1 退出，提示行不变。这与 #40 中合入的架构 3.0 和 ADR-0002 一致。我重写了第 2、6、7 项的备注，它们原先还写着退出码 1。有两条不阻塞的备注。给接口设计师，如果设计因其他原因要修改：2.1 节或第 3 节可以在 PR #39 旁边引用 ADR-0002 和架构 3.0（#40），就像第 3 节引用 #36 和 #37 那样。给测试经理：F04 的测试计划对每种文件错误都期望退出码 2，测试只能靠标准错误区分文件错误和错误的命令行。 | 第 2 轮批准。 |

## 5. 修改记录

| 版本 | 日期 | 修改 |
| --- | --- | --- |
| 0.1 | 2026-11-14 | 初稿。 |
| 0.2 | 2026-11-14 | Troy 在 PR #39 中的修改：每种文件错误都以退出码 2 而不是 1 退出，提示行不变。写明退出码 1 现在只表示缺陷，并且由标准错误中的文字区分文件错误和错误的命令行。 |
| 1.0 | 2026-11-14 | Troy 批准。 |
