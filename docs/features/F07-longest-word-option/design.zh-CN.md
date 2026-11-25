---
troy-doc: "F07-design"
lang: "zh-CN"
version: "1.0"
updated: "2026-11-25"
status: "Troy 已于 2026-11-25 批准"
mirror-of: "design.md"
---

# F07 最长词选项：接口设计

## 1. 功能

- 编号和名称：F07 Longest word option（最长词选项）
- 需求：[docs/requirements.zh-CN.md](../../requirements.zh-CN.md#4-功能点)
- 硬依赖：F04
- 软依赖：无

## 2. 接口

F07 修改模块 cli 中 F04 的两个接口，并在模块 counting 中新增一个接口，做法与 F06 相同。2.1 节是 Troy 输入的命令，它新增选项 `--longest`。2.2 节是命令背后的函数。2.3 节是新的库函数 `longest_word_length`，它找出一个文件中最长词的长度，`main` 在遇到 `--longest` 时调用它。

找最长词的工作放在 counting 中，而不是 cli 中，理由与 F06 设计第 2 节为 `count_chars` 给出的理由相同。架构第 3 节说 cli 读取参数并调用 counting。counting 已经实现了 `--longest` 必须与 `wordcount FILE` 一致的规则：什么是词（F03），跳过文件开头的一个字节顺序标记（需求 Q5），文件不存在或不是合法 UTF-8 时抛出 Python 自己的异常（Q4）。把词的规则放在一个模块里，`wordcount FILE` 和 `wordcount --longest FILE` 对“什么是词”就不会有分歧（Q15）。需求 Q6 已经确定统计行数放进 counting 不需要修改架构，度量词的长度同样如此。

F05 和 F06 的代码已经在 `main` 上，所以命令中已有 `--lines` 和 `--chars`，它们属于一组互斥的计数选项。`--longest` 是这一组的第三个成员，需求 Q16 由此成立。除此之外，F07 不使用 F05 或 F06 的任何东西。Troy 为 F06 和 F05 批准的三条规则适用于整个命令行，所以也适用于 `--longest`：缩写的选项名是错误的命令行；选项可以写在文件之后；一个命令中有两个计数选项时，给出 argparse 自己措辞的用法错误。

2.1 节中有一点是提议，由 Troy 接受或修改，并在所在位置注明：显示新选项的用法行。

### 2.1 `wordcount`

- 模块：cli。`pyproject.toml` 中的控制台脚本 `wordcount = "troy_mode_trial.cli:main"` 保持 F04 声明的样子。
- 功能：像 F04 一样打印一个 UTF-8 文本文件的词数；加上 `--longest` 时，改为打印其中最长词的长度（以字符计），让 Troy 不写 Python 也能在 PowerShell 中得到最长词的长度。`--lines` 和 `--chars` 按 F05 和 F06 的说明工作。

签名：

```text
usage: wordcount [--lines | --chars | --longest] FILE
```

参数：

| 名称 | 类型 | 含义 | 约束 |
| --- | --- | --- | --- |
| `--longest` | 选项，不带值的开关 | 打印 `FILE` 中最长词的长度（以字符计），而不是词数。不加计数选项时，命令打印词数，与 F04 完全相同。 | 可选。只有全名 `--longest`，没有 `-L` 之类的短形式（需求 Q14）。缩写的名字，例如 `--long` 或 `--lo`，是错误的命令行，与 `--chars` 和 `--lines` 相同。选项可以写在 `FILE` 之前或之后：`wordcount --longest notes.txt` 与 `wordcount notes.txt --longest` 效果相同。写两次，例如 `wordcount --longest --longest notes.txt`，与写一次相同。`--longest=VALUE` 是错误的命令行。它不能与 `--lines` 或 `--chars` 一起出现，不论顺序如何（需求 Q16）。 |
| `--lines` | 选项，不带值的开关 | 打印 `FILE` 的行数，完全按 F05 设计 2.1 节的说明。 | 与 F05 设计 2.1 节相同。它不能与 `--chars` 或 `--longest` 一起出现。 |
| `--chars` | 选项，不带值的开关 | 打印 `FILE` 的字符数，完全按 F06 设计 2.1 节的说明。 | 与 F06 设计 2.1 节相同。它不能与 `--lines` 或 `--longest` 一起出现。 |
| `FILE` | 一个命令行参数 | 要读取的文件路径，可以是绝对路径，也可以是相对当前工作目录的路径。 | 与 F04 设计 2.1 节相同：恰好一个参数，指向一个存在、可读的普通文件，内容是合法的 UTF-8。以 `-` 开头的路径放在 `--` 之后，例如 `wordcount --longest -- -notes.txt`。`--` 之后的 `--longest` 是文件名，不是选项。 |

这个命令仍然没有 `-h` 或 `--help`，除 `--lines`、`--chars` 和 `--longest` 外没有其他选项（需求第 8 节）。它从不打印最长的词本身（需求第 8 节）。

**提议 1，用法行，由 Troy 接受或修改。** 用法行把三个选项显示为互选：`usage: wordcount [--lines | --chars | --longest] FILE`，取代 F05 的 `usage: wordcount [--lines | --chars] FILE`。这沿用了 Troy 为 F05 批准的形式：方括号表示计数选项可选，每个 `|` 表示一个命令最多取其中一个。这正是 argparse 为这组选项写出的行，所以不需要额外的代码。`--longest` 排在最后，与需求中的顺序一致。另一种做法是保留 F05 的用法行，这样命令没有帮助，就在任何地方都不会提到 `--longest`。

- 返回值：成功时退出码 0。标准输出是一个十进制数，不带符号、填充或分隔符，后跟一个换行符；标准错误为空，与 F04 设计 2.1 节相同。
  - 不加计数选项时，这个数是 `count_words(FILE)` 的返回值，与 F04 相同。
  - 加 `--longest` 时，这个数是 `longest_word_length(FILE)` 的返回值（2.3 节）：按 F03 的方式划分词，最长词的长度，以 Unicode 码位计；文件中没有词时为 0。词是整段非空白字符，包括标点，所以 `don't,` 是 6（需求 Q15）。`世界!` 是 3，虽然它占 7 个字节。网址或 `x--y` 这样的一段都是一个词，所以这样的一段常常就是最长的。行尾是空白，所以同一个文件在 Windows 和 Linux 上保存，得到的数相同。
  - 加 `--lines` 或 `--chars` 时，这个数按 F05 或 F06 的设计。

错误：

每种错误都让标准输出保持为空，只写标准错误。加 `--longest` 时的文件错误，与 `wordcount FILE` 对同一个文件给出的消息和退出码完全相同（需求 F07）：一行 `wordcount: <FILE>: <reason>`，后跟一个换行符，退出码 2。`<FILE>` 和五个原因文本与 F04 设计 2.1 节相同，没有变化。

| 错误 | 何时发生 |
| --- | --- |
| 退出码 2，原因 `no such file` | 与 F04 设计 2.1 节相同：`FILE` 处没有文件或文件夹，`FILE` 是空字符串，或者路径中的某个文件夹不存在或是文件。 |
| 退出码 2，原因 `is a folder` | 与 F04 设计 2.1 节相同：`FILE` 指向文件夹。 |
| 退出码 2，原因 `permission denied` | 与 F04 设计 2.1 节相同：进程无权读取该文件。 |
| 退出码 2，原因 `not valid UTF-8` | 与 F04 设计 2.1 节相同：文件内容不是合法的 UTF-8。加 `--longest` 时，命令解码整个文件，所以非法字节出现在合法文本之后的文件也是这个错误，不打印任何数。 |
| 退出码 2，原因 `cannot read file` | 与 F04 设计 2.1 节相同：打开或读取文件时出现的其他 `OSError`。 |
| 退出码 2，用法行，两个计数选项 | 命令行中 `--longest` 与 `--lines` 或 `--chars` 同时出现，不论顺序和位置。标准错误先是提议 1 的用法行，再是一行 argparse 自己措辞的消息，先说后出现的选项，与 `--lines` 加 `--chars` 相同（F05 设计 2.1 节提议 2，已批准）。例如 `wordcount --lines --longest notes.txt` 得到 `wordcount: error: argument --longest: not allowed with argument --lines`，`wordcount --longest notes.txt --chars` 得到 `wordcount: error: argument --chars: not allowed with argument --longest`。这个错误在检查缺少 `FILE` 之前给出。`--lines` 加 `--chars` 仍是 F05 设计中的消息。 |
| 退出码 2，用法行，其他情况 | 命令行没有 `FILE`、有多于一个参数、有这三个以外的选项、有 `--long` 这样的缩写、有 `-L`、`-h` 或 `--longest=VALUE`。argparse 先写提议 1 的用法行，再写一行 argparse 自己措辞的 `wordcount: error: <message>`，例如 `wordcount --longest` 得到 `wordcount: error: the following arguments are required: FILE`，`wordcount -L notes.txt` 得到 `wordcount: error: unrecognized arguments: -L`。 |

其他任何异常都是缺陷，与 F04 相同：Python 把回溯信息写到标准错误，并以退出码 1 退出（架构第 6 节）。

- 副作用：与 F04 设计 2.1 节相同：命令以只读方式打开 `FILE`，并在退出前关闭它；只写标准输出和标准错误；不写、不发送、不保存任何数据。F07 合入后，项目要重新安装一次，例如运行 `uv pip install -e . --no-deps`，这个选项才会存在。
- 性能指标：无

示例：

当前文件夹中的 `notes.txt` 是 UTF-8 文件，有两行 `Hello world` 和 `  troy-mode  trial`，每行以 `\n` 结尾。`greeting.txt` 只有一行 `你好 世界!`，以 `\r\n` 结尾。`dashes.txt` 只有一行 `-- ...`。`latin1.txt` 以 Latin-1 编码保存 `café au lait`。

```text
PS> wordcount --longest notes.txt
9
PS> wordcount notes.txt --longest
9
PS> wordcount notes.txt
4
PS> wordcount --longest greeting.txt
3
PS> wordcount --longest dashes.txt
0
PS> wordcount --longest missing.txt
wordcount: missing.txt: no such file
PS> $LASTEXITCODE
2
PS> wordcount --longest latin1.txt
wordcount: latin1.txt: not valid UTF-8
PS> $LASTEXITCODE
2
PS> wordcount --lines --longest notes.txt
usage: wordcount [--lines | --chars | --longest] FILE
wordcount: error: argument --longest: not allowed with argument --lines
PS> $LASTEXITCODE
2
PS> wordcount --long notes.txt
usage: wordcount [--lines | --chars | --longest] FILE
wordcount: error: unrecognized arguments: --long
PS> $LASTEXITCODE
2
```

### 2.2 `main`

- 模块：cli，位于 `src/troy_mode_trial/cli.py`，与 F04 设计 2.2 节相同。测试以 `from troy_mode_trial.cli import main` 导入它。
- 功能：运行一次 2.1 节的 `wordcount` 命令：读取参数，通过 `count_words` 得到这个数，加 `--lines` 时通过 `count_lines`，加 `--chars` 时通过 `count_chars`，加 `--longest` 时通过 `longest_word_length`；写出结果或错误，并返回退出码。它从包 `troy_mode_trial` 导入这四个函数，从不从 `troy_mode_trial.counting` 导入（架构第 4 节）。

签名：

```python
def main(argv: Sequence[str] | None = None) -> int:
```

签名不变。`Sequence` 是 `collections.abc.Sequence`。

参数：

| 名称 | 类型 | 含义 | 约束 |
| --- | --- | --- | --- |
| `argv` | `Sequence[str] \| None` | 程序名之后的命令行参数，例如 `["--longest", "notes.txt"]` 或 `["notes.txt"]`。`None` 表示 `sys.argv[1:]`，控制台脚本传的就是它。 | 每一项都是 `str`。参数规则就是 2.1 节中 `--lines`、`--chars`、`--longest` 和 `FILE` 的规则。 |

- 返回值：`int`，退出码，与 F04 设计 2.2 节相同。向标准输出写出 2.1 节的数和一个换行符后返回 `0`。向标准错误写出一行 `wordcount: <FILE>: <reason>` 后返回 `2`。不论 `sys.argv[0]` 是什么，每条消息中的程序名都是 `wordcount`。

错误：

| 错误 | 何时发生 |
| --- | --- |
| 代码为 2 的 `SystemExit` | 参数错误，见 2.1 节“错误”表中的两个用法行，包括 `--longest` 与 `--lines` 或 `--chars` 同时出现。argparse 把用法行和它的消息写到标准错误，并抛出 `SystemExit(2)`，所以 `main` 不返回。 |
| 其他任何异常 | 缺陷。`main` 只捕获 `count_words`、`count_lines`、`count_chars` 或 `longest_word_length` 抛出的 `OSError` 及其子类和 `UnicodeDecodeError`，其他异常都传给调用者。 |

- 副作用：与 F04 设计 2.2 节相同：用 `sys.stdout.write` 和 `sys.stderr.write` 写出，而不是 `print()`（架构第 8 节）；按 2.1 节的说明读取文件；不改变任何全局状态，所以测试可以在一个进程中多次调用它。
- 性能指标：无

示例：

`notes.txt` 和 `greeting.txt` 是 2.1 节示例中的文件。

```python
>>> from troy_mode_trial.cli import main
>>> main(["--longest", "notes.txt"])
9
0
>>> main(["--longest", "greeting.txt"])
3
0
>>> main(["--longest", "missing.txt"])  # writes to standard error
wordcount: missing.txt: no such file
2
>>> main(["--longest", "--chars", "notes.txt"])
usage: wordcount [--lines | --chars | --longest] FILE
wordcount: error: argument --chars: not allowed with argument --longest
Traceback (most recent call last):
  ...
SystemExit: 2
```

### 2.3 `longest_word_length`

- 模块：counting。调用者从包 `troy_mode_trial` 导入它，该包由 `src/troy_mode_trial/__init__.py` 定义，与 `count_chars`、`count_lines` 和 `count_words` 并列。本设计不在 `src/troy_mode_trial/` 下新增文件。
- 功能：读取一个 UTF-8 文本文件，按 `count_words` 的方式找出词，返回最长词的长度（以 Unicode 码位计）；文件中没有词时返回 0。

签名：

```python
def longest_word_length(path: str | os.PathLike[str]) -> int:
```

函数名说明了它返回什么。它不以 `count_` 开头，因为它返回的是一个长度，而不是若干东西的个数。

参数：

| 名称 | 类型 | 含义 | 约束 |
| --- | --- | --- | --- |
| `path` | `str \| os.PathLike[str]` | 要读取的文件路径，可以是绝对路径，也可以是相对当前工作目录的路径。`pathlib.Path` 是 `os.PathLike[str]`，可以接受。 | 指向一个存在、可读的普通文件，内容是合法的 UTF-8。不接受 `bytes` 路径。 |

- 返回值：`int`，0 或更多。函数把整个文件按 UTF-8 解码，并去掉文件开头的一个字节顺序标记（U+FEFF）（需求 Q5）。它完全按 `count_words` 的方式把文本分成词（F03 设计），返回词的 `len()` 中的最大值；没有词时返回 0。所以 `count_words(path)` 为 0 时，`longest_word_length(path)` 也为 0，反之亦然。

  词和长度的规则：

  - 词是一段一个或多个 `str.isspace()` 为假的字符，其中至少有一个字符的 `str.isalnum()` 为真。整段就是这个词，包括标点（需求 Q15）。没有字母或数字的一段，例如 `--` 或 `...`，不是词，不论多长，它的长度都不计入。
  - 每个 `str.isspace()` 为真的字符都分隔词，包括行尾 `\n`、`\r` 和 `\r\n`、制表符和 U+3000。空白从不属于词，所以行尾转换不影响结果。
  - 长度按码位计，与 `--chars` 相同。`你` 是 1，虽然它占三个字节。由几个码位组成的字符按码位分别计数：写成 `e` 加组合重音符 U+0301 的 `é` 是 2。
  - 只去掉最开头的一个字节顺序标记。其他位置的 U+FEFF 不是空白，所以它属于所在的那一段，并让那一段的长度加 1，与 `count_words` 相同。
  - 几个词同为最长时，结果就是这个长度。是哪个词无关紧要，因为函数只返回长度。

  | 文件字节（以文本表示） | 结果 |
  | --- | --- |
  | （空） | `0` |
  | `EF BB BF`（只有字节顺序标记） | `0` |
  | `-- ...\n` | `0` |
  | `Hello world\n  troy-mode  trial\n` | `9` |
  | `don't, he said.` | `6` |
  | `你好 世界!\r\n` | `3` |
  | `----a ......` | `5` |
  | `a\tbb\rccc\r\ndd` | `3` |
  | `x` 之后是 U+3000，再之后是 `yy` | `2` |
  | `EF BB BF` 之后是 `abc` | `3` |
  | `EF BB BF EF BB BF` 之后是 `abc` | `4` |
  | `e` 之后是 U+0301 | `2` |

错误：

函数不定义自己的异常（需求 Q4）。它让 Python 自己的异常传给调用者，错误表与 `count_words`、`count_lines` 和 `count_chars` 相同。

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

`notes.txt`、`greeting.txt` 和 `dashes.txt` 是 2.1 节示例中的文件。

```python
>>> from pathlib import Path
>>> from troy_mode_trial import longest_word_length
>>> longest_word_length("notes.txt")
9
>>> longest_word_length(Path("greeting.txt"))
3
>>> longest_word_length("dashes.txt")
0
>>> longest_word_length("missing.txt")
Traceback (most recent call last):
  ...
FileNotFoundError: [Errno 2] No such file or directory: 'missing.txt'
```

## 3. 对已有接口的修改

需求 7.0 把 F07 作为新功能加入，包括选项 `--longest` 和决定 Q14 到 Q16，见已经合并的 [docs] PR “[docs] Change the requirements: add the wordcount --longest option”（提交 `3cc6e1b`）。F04 已经验收；给同一个命令加入 `--lines` 和 `--chars` 的 F05 和 F06 也已验收。F07 只按下面的方式修改它们的接口：

1. `wordcount`（F04 设计 2.1 节）新增选项 `--longest`。`wordcount FILE`、`wordcount --lines FILE` 和 `wordcount --chars FILE` 打印的数、错误行和退出码都与以前相同。
2. 如果 Troy 接受 2.1 节的提议 1，用法行从 `usage: wordcount [--lines | --chars] FILE` 改为 `usage: wordcount [--lines | --chars | --longest] FILE`。每个用法错误的其余部分不变：退出码 2，标准输出为空，第二行是 `wordcount: error: <message>`；不含 `--longest` 的命令行得到的消息与以前相同。期望的用法行按下面的方式修改，用例的其他部分不变：
   - F05 的测试计划：逐字检查第一行 `usage: wordcount [--lines | --chars] FILE` 的用例 F05-T13、F05-T14、F05-T15 和 F05-T23。在 `tests/test_cli_lines.py` 中，它们从常量 `USAGE_BOTH` 取得这一行。它们期望的第一行改为提议 1 的用法行。它们的第二行，包括 `argument --chars: not allowed with argument --lines`，不变。
   - F06 的测试计划：F06-T28 和 F06-T34 检查用法行在 ` FILE` 之前的一对方括号中含有 `--chars`，新的用法行仍然如此，所以它们不变。
   - F04 的测试计划 1.1 只检查用法行以 `usage: wordcount ` 开头，v0.3 的版本测试计划只检查标准错误以 `usage:` 开头，所以它们不变。
   - F05 和 F06 的设计在示例中显示的是当时的用法行。本设计不修改它们，就像 F05 的设计没有修改 F06 的设计一样。
3. 带 `--longest` 的命令行以前是用法错误，消息为 `unrecognized arguments: --longest`。现在它得到 2.1 节的数；与 `--lines` 或 `--chars` 同时出现时，得到 2.1 节的用法错误。
4. `main`（F04 设计 2.2 节）保持签名不变。它现在接受 `argv` 中的 `--longest`，此时调用 `longest_word_length`。
5. `src/troy_mode_trial/__init__.py` 在 `count_chars`、`count_lines` 和 `count_words` 旁边导出 `longest_word_length`。这只新增一个名字，不改变已有的名字。三个统计函数保持签名、行为和错误不变，`__init__.py` 仍然不导入 cli。

## 4. 架构师审查

| 项目 | 结果 | 备注 |
| --- | --- | --- |
| 符合模块划分和数据模型 | 通过 | `wordcount` 和 `main` 仍在 cli 中，位于 `src/troy_mode_trial/cli.py`。`longest_word_length` 放在 counting 中，并从 counting 的外部接口 `src/troy_mode_trial/__init__.py` 导出。这两个文件都已在 counting 的“拥有”列中，本设计不在 `src/troy_mode_trial/` 下新增文件。`main` 从包导入四个函数，符合架构第 4 节。量词长与需求 Q6 为行数解决过的情况相同，所以本设计不需要修改架构。argparse 互斥组的第三个成员仍是标准库（ADR-0001），所以本设计不增加依赖。架构没有定义数据模型。 |
| 遵守错误处理和命名约定 | 通过 | `longest_word_length` 不定义自己的异常，错误表与三个统计函数相同（架构第 6 节，需求 Q4）。`main` 仍然只捕获 `OSError` 及其子类和 `UnicodeDecodeError`；加 `--longest` 时写出同样的一行 `wordcount: <FILE>: <reason>`，退出码 2（ADR-0002）。错误的命令行以退出码 2 和用法行结束（需求 Q16），退出码 1 仍然只表示缺陷，标准输出只有数和一个换行符，用 `write` 写出（第 8 节）。架构没有函数命名规则。这个名字不遵循 `count_` 的模式，理由已写明：函数返回的是长度。我同意。按接口设计师的请求，我运行了 argparse（Python 3.14.3；这台机器上没有项目的 Python 3.13 环境），设置 `prog="wordcount"`、`add_help=False`、`allow_abbrev=False`，互斥组依次为 `--lines`、`--chars`、`--longest`，再加 `FILE`。它给出用法行 `usage: wordcount [--lines \| --chars \| --longest] FILE`，以及与 2.1 节错误表完全相同的两条消息；`--chars --longest` 给出 `argument --longest: not allowed with argument --chars`；不带文件的 `--longest --lines` 给出 `argument --lines: not allowed with argument --longest`，所以两个选项的错误先于缺少 `FILE` 的错误。`--lines --chars` 仍给出 `argument --chars: not allowed with argument --lines`。`--longest FILE`、`FILE --longest`、`--longest --longest`、`--longest -- -n.txt`、`-- --longest`、`-L`、`--long`、`--lo`、`-h`、`--longest=x`、不带文件的 `--longest` 和两个文件的结果也都与设计所说相同。我还按 F03 的词规则手工核对了 2.3 节表格的十二行和示例中的数。 |
| 不和已有接口重复 | 通过 | 没有已有接口量词长。`main` 只通过 `longest_word_length` 得到长度，自己不量任何东西。`longest_word_length` 与 `count_words` 共用词规则和读取规则，这是 counting 内部代码层面的事，不是第二个接口。 |
| 只依赖排序在前面的功能 | 通过 | F07 只依赖 F04，并经由它依赖 F03 和 F01。三者在顺序（F01、F03、F04、F07、F06、F02、F05）中都排在 F07 之前，并且已在 Troy 的设备上可用。F05 和 F06 在顺序中排在 F07 之后，但它们已验收，代码已在 `main` 上，所以 F07 只是给它们建好的互斥组加第三个成员，不需要等待任何功能。它不调用它们的函数。 |
| 不在模块之间增加隐性耦合 | 通过 | cli 只依赖 `longest_word_length` 写明的内容：签名、`int` 结果和错误表中的异常，架构第 6 节已经列出这些异常。互斥的选项集合在 cli 中，counting 对选项一无所知。`wordcount` 和 `wordcount --longest` 对“词”的理解一致，这条规则留在 counting 内部。`src/troy_mode_trial/__init__.py` 只新增名字 `longest_word_length`，仍然不导入 cli。`main` 不保留全局状态。 |
| 修改已实现的接口时走了变更流程 | 通过 | F04、F05 和 F06 已验收。需求 7.0（提交 `3cc6e1b`，Troy 已批准）给 F04 的命令加入 `--longest`，并带有 Q14 到 Q16，所以修改走了需求变更流程。F05 定下的用法行只有在 Troy 接受提议 1 时才改变。第 3 节列出了每处修改：选项、用法行、以前的 `unrecognized arguments: --longest` 错误、`main` 不变的签名和新的导出。我检查了 `tests/test_cli_lines.py`、`tests/test_cli_chars.py`、`tests/test_cli.py` 和各测试计划。使用 `USAGE_BOTH` 的正好是 F05-T13、F05-T14、F05-T15 和 F05-T23。F06 的模式 `^usage: wordcount \[[^\]]*--chars[^\]]*\] FILE$` 能匹配新的用法行。F04 的计划 1.1 和 v0.3 的版本测试计划只检查这一行的开头。 |
| 给 Troy 的摘要和设计说的一致，并列出了需要 Troy 决定的每一件事 | 通过 | 摘要与设计一致：以字符计的长度，包括标点，`don't,` 是 6，`世界!` 是 3；没有词的文件为 0；Windows 和 Linux 行尾结果相同；只认全名，可写在文件之前或之后；与 `--lines` 或 `--chars` 同用是用法错误；文件错误和退出码 2 相同；其他命令不变；新的库函数；需要重新安装。它的一件决定事项就是 2.1 节的提议 1，带有设计的推荐和理由。设计没有其他待定的选择。它的两条风险与 2.3 节（由几个码位组成的字符）和 2.1 节（不含空格的长串）一致。我量得中文约 790 个字符，英文约 1,690 个，都少于 2,000。两部分都没有 troy-check 的 R22 模式能找到的内部编号。功能编号是允许的。 |

| 轮次 | 问题 | 解决方式 |
| --- | --- | --- |
| 1 | 没有阻塞问题。用法行和两个选项同用时的消息已通过运行 argparse 确认，见检查表第二行。以下说明不阻塞。给接口设计师：摘要说 `wordcount FILE`、`--lines` 和 `--chars` 的输出和现在一样。它们的数和文件错误确实不变，但如果 Troy 接受决定事项，它们用法错误的第一行会变；摘要也说了这一点，所以不需要修改。给开发者：把 `--longest` 加到现有互斥组中 `--chars` 之后。在 `longest_word_length` 中用与 `count_words` 相同的 `_checked_path`、空路径检查、`encoding="utf-8-sig"` 读取、`str.split()` 和 `_has_letter_or_digit` 找词，使两者不会不一致。更新 `_build_parser` 和 `main` 文档注释中的用法行，并让 `main` 不超过 50 行（R04），例如扩展 `_count_function`。给测试经理：F05-T13、F05-T14、F05-T15 和 F05-T23 测的是已验收的功能，所以在 F07 的每个 PR 中、在 F07 的代码之前和之后都必须通过（R10）。像 F05 用合入检查应对 F06 那样，让它们期望的第一行取决于分支上是否已有 `--longest`，或用模式检查，而不是直接替换 `USAGE_BOTH`。给产品经理：F07 的原型说 `世界!` 是 3 个字符，“不是 9 个字节”。它是 7 个字节，与设计 2.1 节所说相同。 | 第 1 轮通过。 |

## 5. 修改记录

| 版本 | 日期 | 修改 |
| --- | --- | --- |
| 0.1 | 2026-11-25 | 初稿。 |
| 1.0 | 2026-11-25 | Troy 批准。 |
