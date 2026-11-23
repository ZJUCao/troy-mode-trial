---
troy-doc: "F05-design"
lang: "zh-CN"
version: "1.0"
updated: "2026-11-23"
status: "Troy 已于 2026-11-23 批准"
mirror-of: "design.md"
---

# F05 行数选项：接口设计

## 1. 功能

- 编号和名称：F05 Line count option（行数选项）
- 需求：[docs/requirements.zh-CN.md](../../requirements.zh-CN.md#4-功能点)
- 硬依赖：F02、F04
- 软依赖：无

## 2. 接口

F05 修改模块 cli 中 F04 的两个接口，F06 也修改这两个接口。2.1 节是 Troy 输入的命令，它新增选项 `--lines`。2.2 节是命令背后的函数。F05 不新增库函数：`main` 通过 F02 的 `count_lines` 统计行数，包 `troy_mode_trial` 已经导出了它（F02 设计 2.1 节）。

本设计建立在 F06 设计 1.0 之上，Troy 已按全部推荐批准了它。其中三条规则适用于整个命令行，所以对 `--lines` 和对 `--chars` 一样成立：用法行列出选项，缩写的选项名是错误的命令行，选项可以写在文件之后。F06 的设计让 `--chars` 成为一组互斥计数选项的第一个成员，并把 `--lines` 与 `--chars` 同时出现时的用法行和消息留给本设计（需求 Q13）。`--lines` 是这一组的第二个成员。

2.1 节中有两点是提议，由 Troy 接受或修改，每一点都在所在位置注明：同时显示两个选项的用法行，以及一个命令中有两个选项时的消息。

### 2.1 `wordcount`

- 模块：cli。`pyproject.toml` 中的控制台脚本 `wordcount = "troy_mode_trial.cli:main"` 保持 F04 声明的样子。
- 功能：像 F04 一样打印一个 UTF-8 文本文件的词数；加上 `--lines` 时，改为按 F02 的方式打印它的行数；加上 `--chars` 时，像 F06 一样打印它的字符数。这样 Troy 不写 Python 也能在 PowerShell 中统计行数。

签名：

```text
usage: wordcount [--lines | --chars] FILE
```

参数：

| 名称 | 类型 | 含义 | 约束 |
| --- | --- | --- | --- |
| `--lines` | 选项，不带值的开关 | 打印 `FILE` 的行数，而不是词数。不加计数选项时，命令打印词数，与 F04 完全相同。 | 可选。只有全名 `--lines`，没有 `-l` 之类的短形式（需求 Q7）。缩写的名字，例如 `--line` 或 `--li`，是错误的命令行，与 `--chars` 相同（F06 设计 2.1 节提议 2，已批准）。选项可以写在 `FILE` 之前或之后：`wordcount --lines notes.txt` 与 `wordcount notes.txt --lines` 效果相同（F06 设计 2.1 节提议 3，已批准）。写两次，例如 `wordcount --lines --lines notes.txt`，与写一次相同，统计一次行数。`--lines=VALUE` 是错误的命令行。它不能与 `--chars` 同时出现，不论顺序（需求 Q13，见下面的提议 2）。 |
| `--chars` | 选项，不带值的开关 | 打印 `FILE` 的字符数，与 F06 设计 2.1 节所说完全相同。 | 与 F06 设计 2.1 节相同。它不能与 `--lines` 同时出现，不论顺序。 |
| `FILE` | 一个命令行参数 | 要统计的文件路径，可以是绝对路径，也可以是相对当前工作目录的路径。 | 与 F04 设计 2.1 节相同：恰好一个参数，指向一个存在、可读的普通文件，内容是合法的 UTF-8。以 `-` 开头的路径放在 `--` 之后，例如 `wordcount --lines -- -notes.txt`。`--` 之后的 `--lines` 是文件名，不是选项。 |

这个命令仍然没有 `-h` 或 `--help`，除 `--lines` 和 `--chars` 外没有其他选项（需求第 8 节）。

**提议 1，用法行，由 Troy 接受或修改。** 用法行把两个选项显示为二选一：`usage: wordcount [--lines | --chars] FILE`。方括号表示计数选项可以不写，`|` 表示一个命令最多写其中一个。argparse 对一组互斥选项写的就是这一行，所以不需要额外的代码。另一种做法是 `usage: wordcount [--lines] [--chars] FILE`，读起来像两个选项可以同时写，而那其实是用法错误。`--lines` 排在前面，因为需求先提到它。

**提议 2，一个命令中有两个选项，由 Troy 接受或修改。** `wordcount --lines --chars notes.txt` 是用法错误，退出码 2，这是 Troy 已经决定的（需求 Q13）。标准错误先是提议 1 的用法行，再是一行 argparse 自己措辞的消息，消息先说出后写的那个选项：

```text
usage: wordcount [--lines | --chars] FILE
wordcount: error: argument --chars: not allowed with argument --lines
```

`wordcount --chars --lines notes.txt` 得到 `wordcount: error: argument --lines: not allowed with argument --chars`。两个选项不论写在什么位置都给出这个错误，例如 `wordcount --lines notes.txt --chars`；它也先于缺少 `FILE` 的检查。另一种做法是项目自己的消息，例如 `wordcount: error: give only one of --lines and --chars`。它读起来更直白，但需要额外的代码，而命令的其他用法错误都用 argparse 自己的措辞。

- 返回值：成功时退出码 0。标准输出是十进制的计数，不带符号、填充或分隔符，后跟一个换行符；标准错误为空，与 F04 设计 2.1 节相同。
  - 不加计数选项时，计数是 `count_words(FILE)` 的返回值，与 F04 相同。
  - 加 `--lines` 时，计数是 `count_lines(FILE)` 的返回值（F02 设计 2.1 节）：`\n`、`\r\n` 和 `\r` 各结束一行，没有换行符的最后一行也算一行，忽略文件开头的一个字节顺序标记，空文件是 0 行（需求 Q2、Q3、Q5）。所以在 Windows 上保存的文件与在 Linux 上保存的同一个文件得到相同的计数。
  - 加 `--chars` 时，计数是 `count_chars(FILE)` 的返回值，与 F06 设计 2.1 节相同。

错误：

每种错误都让标准输出保持为空，只写标准错误。加 `--lines` 时的文件错误，与 `wordcount FILE` 对同一个文件给出的消息和退出码完全相同（需求 Q8）：一行 `wordcount: <FILE>: <reason>`，后跟一个换行符，退出码 2。`<FILE>` 和五个原因文本与 F04 设计 2.1 节相同，没有变化。

| 错误 | 何时发生 |
| --- | --- |
| 退出码 2，原因 `no such file` | 与 F04 设计 2.1 节相同：`FILE` 处没有文件或文件夹，`FILE` 是空字符串，或者路径中的某个文件夹不存在或是文件。 |
| 退出码 2，原因 `is a folder` | 与 F04 设计 2.1 节相同：`FILE` 指向文件夹。 |
| 退出码 2，原因 `permission denied` | 与 F04 设计 2.1 节相同：进程无权读取该文件。 |
| 退出码 2，原因 `not valid UTF-8` | 与 F04 设计 2.1 节相同：文件内容不是合法的 UTF-8。加 `--lines` 时，命令解码整个文件，所以非法字节出现在合法文本之后的文件也是这个错误，不打印计数。 |
| 退出码 2，原因 `cannot read file` | 与 F04 设计 2.1 节相同：打开或读取文件时出现的其他 `OSError`。 |
| 退出码 2，用法行，两个选项 | 命令行同时有 `--lines` 和 `--chars`，不论顺序和位置。标准错误是提议 2 的用法行和消息。 |
| 退出码 2，用法行，其他情况 | 命令行没有 `FILE`、有多于一个参数、有 `--lines` 和 `--chars` 以外的选项、有 `--line` 这样的缩写、有 `-l`、`-h` 或 `--lines=VALUE`。argparse 先写提议 1 的用法行，再写一行 argparse 自己措辞的 `wordcount: error: <message>`，例如 `wordcount --lines` 得到 `wordcount: error: the following arguments are required: FILE`，`wordcount -l notes.txt` 得到 `wordcount: error: unrecognized arguments: -l`。 |

其他任何异常都是缺陷，与 F04 相同：Python 把回溯信息写到标准错误，并以退出码 1 退出（架构第 6 节）。

**合入顺序。** F06 的代码同时在开发，还没有合入。F05 和 F06 中后合入的那个保留另一个的选项。本设计描述的是两者都合入后的命令。如果 F05 的代码先合入，那么在 F06 的代码合入之前，计数选项组只有 `--lines`，`--chars` 是未知选项，argparse 写出的用法行是 `usage: wordcount [--lines] FILE`。之后 F06 的代码把 `--chars` 加入这一组，用法行变成提议 1 的那一行。如果 F06 的代码先合入，F05 的代码把 `--lines` 加入 F06 的选项组，排在 `--chars` 之前。

- 副作用：与 F04 设计 2.1 节相同：命令以只读方式打开 `FILE`，并在退出前关闭它；只写标准输出和标准错误；不写、不发送、不保存任何数据。F05 合入后，项目要重新安装一次，例如运行 `uv pip install -e . --no-deps`，这个选项才会存在。
- 性能指标：无

示例：

当前文件夹中的 `notes.txt` 是 UTF-8 文件，有两行 `Hello world` 和 `  troy-mode  trial`，每行以 `\n` 结尾。`windows.txt` 有相同的两行，每行以 `\r\n` 结尾。`latin1.txt` 以 Latin-1 编码保存 `café au lait`。

```text
PS> wordcount --lines notes.txt
2
PS> wordcount notes.txt --lines
2
PS> wordcount --lines windows.txt
2
PS> wordcount notes.txt
4
PS> wordcount --lines missing.txt
wordcount: missing.txt: no such file
PS> $LASTEXITCODE
2
PS> wordcount --lines latin1.txt
wordcount: latin1.txt: not valid UTF-8
PS> $LASTEXITCODE
2
PS> wordcount --lines --chars notes.txt
usage: wordcount [--lines | --chars] FILE
wordcount: error: argument --chars: not allowed with argument --lines
PS> $LASTEXITCODE
2
PS> wordcount -l notes.txt
usage: wordcount [--lines | --chars] FILE
wordcount: error: unrecognized arguments: -l
PS> $LASTEXITCODE
2
```

### 2.2 `main`

- 模块：cli，位于 `src/troy_mode_trial/cli.py`，与 F04 设计 2.2 节相同。测试以 `from troy_mode_trial.cli import main` 导入它。
- 功能：运行一次 2.1 节的 `wordcount` 命令：读取参数，通过 `count_words` 统计文件；参数中有 `--lines` 时通过 `count_lines` 统计，有 `--chars` 时通过 `count_chars` 统计；写出结果或错误，并返回退出码。它从包 `troy_mode_trial` 导入这三个函数，从不从 `troy_mode_trial.counting` 导入（架构第 4 节）。

签名：

```python
def main(argv: Sequence[str] | None = None) -> int:
```

签名不变。`Sequence` 是 `collections.abc.Sequence`。

参数：

| 名称 | 类型 | 含义 | 约束 |
| --- | --- | --- | --- |
| `argv` | `Sequence[str] \| None` | 程序名之后的命令行参数，例如 `["--lines", "notes.txt"]` 或 `["notes.txt"]`。`None` 表示 `sys.argv[1:]`，控制台脚本传的就是它。 | 每一项都是 `str`。参数规则就是 2.1 节中 `--lines`、`--chars` 和 `FILE` 的规则。 |

- 返回值：`int`，退出码，与 F04 设计 2.2 节相同。向标准输出写出 2.1 节的计数和一个换行符后返回 `0`。向标准错误写出一行 `wordcount: <FILE>: <reason>` 后返回 `2`。不论 `sys.argv[0]` 是什么，每条消息中的程序名都是 `wordcount`。

错误：

| 错误 | 何时发生 |
| --- | --- |
| 代码为 2 的 `SystemExit` | 参数错误，见 2.1 节“错误”表中两行用法错误，包括 `--lines` 与 `--chars` 同时出现。argparse 把用法行和它的消息写到标准错误，并抛出 `SystemExit(2)`，所以 `main` 不返回。 |
| 其他任何异常 | 缺陷。`main` 只捕获 `count_words`、`count_lines` 或 `count_chars` 抛出的 `OSError` 及其子类和 `UnicodeDecodeError`，其他异常都传给调用者。 |

- 副作用：与 F04 设计 2.2 节相同：用 `sys.stdout.write` 和 `sys.stderr.write` 写出，而不是 `print()`（架构第 8 节）；按 2.1 节的说明读取文件；不改变任何全局状态，所以测试可以在一个进程中多次调用它。
- 性能指标：无

示例：

`notes.txt` 是 2.1 节示例中的文件。

```python
>>> from troy_mode_trial.cli import main
>>> main(["--lines", "notes.txt"])
2
0
>>> main(["notes.txt"])
4
0
>>> main(["--lines", "missing.txt"])  # writes to standard error
wordcount: missing.txt: no such file
2
>>> main(["--chars", "--lines", "notes.txt"])
usage: wordcount [--lines | --chars] FILE
wordcount: error: argument --lines: not allowed with argument --chars
Traceback (most recent call last):
  ...
SystemExit: 2
```

## 3. 对已有接口的修改

需求 5.0 把 F05 作为新功能加入，包括选项 `--lines` 和决定 Q7 到 Q9，见已经合并的 [docs] PR “[docs] Change the requirements: add the wordcount --lines option”（提交 `eb369e0`）。需求 6.0 加入决定 Q13，即一个命令中有两个计数选项是用法错误，见已经合并的 [docs] PR “[docs] Change the requirements: add the wordcount --chars option”（#63，提交 `fc2bb26`）。F04 已经验收，所以 F05 只按下面的方式修改它的接口：

1. `wordcount`（F04 设计 2.1 节）新增选项 `--lines`。不加选项的 `wordcount FILE` 打印的计数、错误行和退出码都与以前相同，`wordcount --chars FILE` 的行为与 F06 的设计相同。
2. 如果 Troy 接受 2.1 节的提议 1，用法行变为 `usage: wordcount [--lines | --chars] FILE`，取代 F04 的 `usage: wordcount FILE` 和 F06 的 `usage: wordcount [--chars] FILE`。每个用法错误的其余部分不变：退出码 2，标准输出为空，第二行是 `wordcount: error: <message>`。F05 和 F06 都合入后，下面这些期望的用法行改为 `usage: wordcount [--lines | --chars] FILE`，其他不变：
   - F04 的测试计划：用法错误的定义，其第一行恰好是 `usage: wordcount FILE`，以及因此依赖它的用例 F04-T11、F04-T12、F04-T13 和 F04-T21。F04-T13 还逐字检查这一行。在 `tests/test_cli.py` 中，它们是辅助函数 `_assert_usage`，以及 `test_f04_t13_program_name` 和 `test_f04_t21_program_usage` 中的检查。F06 的测试计划 PR 会先把同一行改为 `usage: wordcount [--chars] FILE`（F06 设计第 3 节）。不论这些用例当时期望的是哪一行，都改为新的一行。
   - F06 的测试计划（还没有合入）：每个期望第一行是 `usage: wordcount [--chars] FILE` 的用例，例如设计中 `--char` 和不带文件的 `--chars` 这两个示例。
   - F06 的设计在 2.1 节和 2.2 节中显示 `usage: wordcount [--chars] FILE`，这是 `--chars` 还是唯一选项时命令的用法行。它的第 3 节已经说明后合入的功能同时显示两个选项，所以本设计不修改 F06 的设计。
   - v0.2 和 v0.3 的版本测试计划只检查标准错误以 `usage:` 开头，所以不变。
3. `--lines` 与 `--chars` 同时出现时的用法错误，取代只有 F06 时会给出的 `unrecognized arguments: --lines`。它的消息是 2.1 节提议 2 的消息。F06 测试计划中期望 `unrecognized arguments: --lines` 的用例，在两个功能都合入后，把期望的第二行改为这条消息。
4. `main`（F04 设计 2.2 节）保持签名不变。它现在接受 `argv` 中的 `--lines`，此时调用 `count_lines`。
5. `src/troy_mode_trial/__init__.py` 不变。它已经导出 `count_lines`（F02 设计 2.1 节）。`count_words`、`count_lines` 和 `count_chars` 保持签名、行为和错误不变。

## 4. 架构师审查

| 项目 | 结果 | 备注 |
| --- | --- | --- |
| 符合模块划分和数据模型 | 通过 | `wordcount` 和 `main` 仍在 cli 中，位于 `src/troy_mode_trial/cli.py`。F05 不新增库函数，也不在 `src/troy_mode_trial/` 下新增文件：`main` 调用 F02 的 `count_lines`，counting 的外部接口 `src/troy_mode_trial/__init__.py` 已经导出了它。`main` 从包导入三个计数函数，符合架构第 4 节。互斥的计数选项组是 argparse 的互斥组，仍属于标准库（ADR-0001），所以本设计不新增依赖，也不需要修改架构。架构没有定义数据模型。 |
| 遵守错误处理和命名约定 | 通过 | `main` 仍然只捕获 `OSError` 及其子类和 `UnicodeDecodeError`，现在也包括 `count_lines` 抛出的；加 `--lines` 时写出同样的一行 `wordcount: <FILE>: <reason>`，退出码 2（架构第 6 节、ADR-0002、需求 Q8）。错误的命令行，包括 `--lines` 与 `--chars` 同时出现，以退出码 2 退出并写出用法行（需求 Q13）；退出码 1 仍然只表示缺陷；标准输出只有计数和一个换行符，用 `write` 写出（第 8 节）。选项名与 `--chars` 一致。第 1 轮中我运行了 argparse（Python 3.14.3；这台机器上没有项目的 Python 3.13 环境），设置为 `prog="wordcount"`、`add_help=False`、`allow_abbrev=False`，互斥组中先 `--lines` 后 `--chars`，再加 `FILE`。它给出用法行 `usage: wordcount [--lines \| --chars] FILE`；`--lines --chars notes.txt`、`--lines notes.txt --chars` 和不带文件的 `--lines --chars` 都得到消息 `argument --chars: not allowed with argument --lines`，`--chars --lines notes.txt` 得到 `argument --lines: not allowed with argument --chars`，退出码都是 2，与提议 1 和提议 2 所说相同。`--lines FILE`、`FILE --lines`、`--lines --lines`、`--lines -- -n.txt`、`-- --lines`、`-l`、`--line`、`--li`、`-h`、`--lines=x`、不带文件的 `--lines` 和两个文件，结果也都与设计所说相同。互斥组中只有 `--lines` 时，用法行是 `usage: wordcount [--lines] FILE`，`--chars` 是无法识别的参数，与合入顺序一段所说相同。按 F02 的规则，示例中的行数正确。 |
| 不和已有接口重复 | 通过 | F05 不新增计数函数。`main` 只通过 `count_lines` 统计行数，自己不做统计，所以行的规则只在一处。 |
| 只依赖排序在前面的功能 | 通过 | F05 依赖 F02 和 F04，并建立在已批准的 F06 设计之上。三者在顺序中都排在 F05 之前（F01、F03、F04、F06、F02、F05）。F02 和 F04 已经可以在 Troy 的设备上使用。F06 的代码还没有合入，合入顺序一段涵盖了两种顺序，所以 F05 不必等 F06 的代码。 |
| 不在模块之间增加隐性耦合 | 通过 | cli 只依赖 `count_lines` 文档中写明的内容：签名、`int` 结果，以及 F02 表中的异常，架构第 6 节已经列出这些异常。互斥选项组在 cli 中，counting 对选项一无所知。`src/troy_mode_trial/__init__.py` 不变，仍然不导入 cli。`main` 不保存全局状态。 |
| 修改已实现的接口时走了变更流程 | 通过 | F04 和 F02 已经验收。需求 5.0（提交 `eb369e0`）为 F04 的命令加入 `--lines`，需求 6.0（#63，提交 `fc2bb26`）加入 Q13，两者都经 Troy 批准，所以修改走的是需求变更流程。第 3 节列出了每一项修改：选项、Troy 接受提议 1 时的新用法行、两个选项同时出现时的消息、`main` 不变的签名，以及不变的 `__init__.py` 和计数函数。我检查了 F04 的测试计划和 `tests/test_cli.py`。含有 `usage: wordcount FILE` 的只有辅助函数 `_assert_usage`，以及 `test_f04_t13_program_name` 和 `test_f04_t21_program_usage` 中的检查。v0.2 和 v0.3 的版本测试计划只检查标准错误以 `usage:` 开头。F06 的设计还没有实现，也不修改。 |
| 给 Troy 的摘要和设计说的一致，并列出了需要 Troy 决定的每一件事 | 通过 | 摘要与设计一致：行数及其规则，包括 Windows 和 Linux 的行尾、没有换行符的最后一行、空文件；词数和 `--chars` 不变；文件错误的错误行和退出码 2 相同；只认全名，可写在文件之前或之后；两个选项同时写是用法错误；需要重新安装。它的两件事就是 2.1 节的提议 1 和提议 2，顺序相同，各自带有设计的推荐和理由；两条风险分别对应合入顺序一段和第 3 节，以及提议 2。设计没有其他待定的选择。我用 troy-check 的 R22 函数检查了任务简报中的摘要：没有发现问题，中文约 960 个字符，英文约 1,930 个字符，没有内部编号。 |

| 轮次 | 问题 | 解决方式 |
| --- | --- | --- |
| 1 | 没有阻塞性问题。接口设计师请我运行 argparse 确认用法行和消息：两者都已确认，见检查表第二行。以下说明不阻塞。给接口设计师：摘要没有提到忽略文件开头的一个字节顺序标记，而 2.1 节说了。它与词数的规则相同，所以摘要不需要修改，而且英文部分只剩约 70 个字符。给开发者：把 `--lines` 加入互斥组，排在 `--chars` 之前，并在解析器上设置 `allow_abbrev=False`，这样不论哪个功能后合入，用法行都是提议 1 的那一行。更新 `_build_parser` 和 `main` 文档注释中的用法行，并让 `main` 保持在 50 行以内（R04），例如用一个辅助函数选出计数函数。给测试经理：F04-T12 也依赖用法错误的定义，所以它与 F04-T11、F04-T13 和 F04-T21 一起通过 `_assert_usage` 修改。F05 和 F06 中后合入测试 PR 的那个，把期望的用法行改为提议 1 的那一行。 | 第 1 轮批准。 |

## 5. 修改记录

| 版本 | 日期 | 修改 |
| --- | --- | --- |
| 0.1 | 2026-11-23 | 初稿。 |
| 1.0 | 2026-11-23 | Troy 批准。 |
