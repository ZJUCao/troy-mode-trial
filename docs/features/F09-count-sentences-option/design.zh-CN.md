---
troy-doc: "F09-design"
lang: "zh-CN"
version: "0.1"
updated: "2026-11-26"
status: "草稿，架构师审查中。"
mirror-of: "design.md"
---

# F09 统计句子数的选项：接口设计

## 1. 功能

- 编号和名称：F09 Count sentences option（统计句子数的选项）
- 需求：[docs/requirements.zh-CN.md](../../requirements.zh-CN.md#4-功能点)
- 硬依赖：F04
- 软依赖：无

## 2. 接口

F09 新增一个接口：模块 counting 中的库函数 `count_sentences`（2.1 节）。它统计一个文件的句子数，`main` 在 `--sentences` 时调用它。第 3 节列出对已有接口的修改：模块 cli 中的 `wordcount` 和 `main` 新增选项 `--sentences`；F08 的模块 settings 的接口新增可保存的值 `sentences`；包的导出新增一个名字。

句子规则放在 counting 中，而不是 cli 中，理由与 F06 设计第 2 节对 `count_chars`、F07 设计第 2 节对 `count_longest` 给出的相同。`--sentences` 必须与 `wordcount FILE` 共用的规则都已在 counting 中：跳过开头的一个字节顺序标记（需求 Q5）；文件不存在或不是合法 UTF-8 时抛出 Python 自己的异常（Q4）；一个词至少含一个字母或数字（F03），一个句子也必须如此（Q24）。需求 Q6 已确定统计行数属于 counting，无需修改架构。统计句子数同样属于它，本设计也不在 `src/troy_mode_trial/` 下新增文件。

F09 在顺序中排在 F08 之后，F08 的设计已批准并合并（F08 设计 1.0）。F09 以它为基础：`--sentences` 加入互斥的选项组，与 `--lines`、`--chars`、`--longest` 和 `--again` 并列；在 `--sentences` 之后运行 `--again` 统计句子数（需求第 5 节，Troy 于 2026-11-26 的选择）。F08 的代码还不在 `main` 上，所以第 3 节把这些记为对 F08 已设计接口的修改，由 F09 的代码在 F08 的代码合入之后完成。

本设计中有一点是提议，由 Troy 接受或修改，并在所在位置注明：新的用法行（3.1 节，提议 1）。

### 2.1 `count_sentences`

- 模块：counting。调用方从包 `troy_mode_trial` 导入它，该包由 `src/troy_mode_trial/__init__.py` 定义，与 `count_chars`、`count_lines`、`count_longest` 和 `count_words` 并列（3.4 节）。
- 功能：读取一个 UTF-8 文本文件，返回它的句子数。句子是以 `.`、`!` 或 `?` 结尾、并且至少含一个字母或数字的一段文本（需求 F09）。

签名：

```python
def count_sentences(path: str | os.PathLike[str]) -> int:
```

名字以 `count_` 开头，与命令背后的另外四个函数一致。

参数：

| 名称 | 类型 | 含义 | 约束 |
| --- | --- | --- | --- |
| `path` | `str \| os.PathLike[str]` | 要读取的文件的路径，可以是绝对路径，也可以是相对当前工作目录的路径。`pathlib.Path` 是 `os.PathLike[str]`，可以接受。 | 指向一个存在、可读、内容为合法 UTF-8 的普通文件。不接受 `bytes` 路径。 |

- 返回值：`int`，0 或更大。函数把整个文件按 UTF-8 解码，并去掉文件开头的一个字节顺序标记（U+FEFF）（需求 Q5）。在 counting 内部，它与 `count_words` 使用同一套文件读取和同一个“字母或数字”判断，而不是再写一份。

  句子的规则：

  - 标点是 `.`（U+002E）、`!`（U+0021）和 `?`（U+003F）这三个字符。其他字符都不是标点：中文的 `。`、`！`、`？` 不是，全角的 `．` 不是，省略号字符 `…` 也不是（需求 Q26）。
  - 一串标点是中间没有其他字符的一个或多个标点，例如 `.`、`...`、`!!` 或 `?!`。每串标点结束一段文本：从上一串标点之后，或从文件开头，到这串标点为止，包括这串标点（需求 Q23）。
  - 一段文本至少含一个 `str.isalnum()` 为真的字符时，才是句子，这与 F03 判断词的方法相同（需求 Q24）。只由标点、空白和其他字符组成的一段，例如 `Hi. .` 的第二段，不是句子。
  - 最后一串标点之后的文本，不论含什么，都不是句子（需求 Q25）。
  - 标点无论在哪里都结束一段，在数字、缩写或网址中也是如此，所以 `3.14.` 是两段（需求 F09，第 8 节）。
  - 换行和其他空白不结束句子。一个句子可以跨多行；没有标点的一行属于下一个句子，或属于最后一串标点之后的文本。所以同一个文件在 Windows 上保存和在 Linux 上保存，得到的数相同。
  - 只去掉最开头的一个字节顺序标记。其他位置的 U+FEFF 是普通字符，既不是字母也不是数字。

  结果从不超过标点串的个数。`count_words(path)` 为 0 时，`count_sentences(path)` 也为 0，因为字母或数字从不是空白，所以总在某个词里。

  | 文件的字节，按文本写 | 结果 | 原因 |
  | --- | --- | --- |
  | （空） | `0` | 没有标点。 |
  | `EF BB BF`（只有字节顺序标记） | `0` | 没有标点。 |
  | `-- ...\n` | `0` | 唯一的一段不含字母或数字。 |
  | `It rains. Does it stop? Yes!!\nWait...\n` | `4` | `!!` 和 `...` 各结束一个句子。 |
  | `Done. Not yet\r\n` | `1` | `Not yet` 不以标点结尾。 |
  | `Pi is 3.14.\n` | `2` | `Pi is 3.` 和 `14.`。 |
  | `Wait?!` | `1` | 只有一串标点。 |
  | `Hi . . . there.` | `2` | 两段 ` .` 不含字母或数字。 |
  | `1. 2. 3.` | `3` | 有数字就够了。 |
  | `_.` | `0` | `_` 既不是字母也不是数字。 |
  | `Line one\nline two.` | `1` | 换行不结束句子。 |
  | `"Stop!" he said.` | `2` | 后面的 `"` 是第二段的开头。 |
  | `你好。世界。` | `0` | `。` 不是标点。 |
  | `你好。He left.` | `1` | 只有一段，由 `.` 结束。 |
  | `EF BB BF` 后跟 `Hi.` | `1` | 字节顺序标记被去掉。 |

错误：

函数不定义自己的异常（需求 Q4）。它让 Python 自己的异常传给调用方，错误表与 `count_words`、`count_lines`、`count_chars` 和 `count_longest` 相同。

| 错误 | 何时发生 |
| --- | --- |
| `FileNotFoundError` | `path` 处没有文件，或者 `path` 是空字符串。 |
| `IsADirectoryError` 或 `PermissionError` | `path` 指向一个文件夹。Linux 抛出 `IsADirectoryError`，Windows 抛出 `PermissionError`。 |
| `PermissionError` | 进程无权读取这个文件。 |
| `UnicodeDecodeError` | 文件中任何一个字节不是合法的 UTF-8，不论它在哪里。 |
| `TypeError` | `path` 既不是 `str` 也不是 `os.PathLike[str]`，例如 `bytes` 或 `int`。 |

- 副作用：函数以只读方式打开文件，并在返回或抛出异常之前关闭它。它不写、不发送、也不保存任何东西。它不碰设置文件。
- 性能指标：无

示例：

`story.txt`、`draft.txt`、`pi.txt` 和 `dashes.txt` 是 F09 原型中的文件：`story.txt` 有 `It rains. Does it stop? Yes!!` 和 `Wait...` 两行，`draft.txt` 有 `Done. Not yet`，`pi.txt` 有 `Pi is 3.14.`，`dashes.txt` 有 `-- ...`。

```python
>>> from pathlib import Path
>>> from troy_mode_trial import count_sentences
>>> count_sentences("story.txt")
4
>>> count_sentences(Path("draft.txt"))
1
>>> count_sentences("pi.txt")
2
>>> count_sentences("dashes.txt")
0
>>> count_sentences("missing.txt")
Traceback (most recent call last):
  ...
FileNotFoundError: [Errno 2] No such file or directory: 'missing.txt'
```

## 3. 对已有接口的修改

需求 8.0 把 F09 作为新功能加入，带有选项 `--sentences` 和 Troy 的决定 Q23 到 Q26，见已合并的 [docs] PR “[docs] Change the requirements: remember the last options and count sentences”（提交 `1c21dd6`）。需求第 5 节记录了 Troy 的选择：F09 排在 F08 之后，并且 `--again` 记住 `--sentences`。架构 4.0 和 ADR-0003 已在 [docs] PR “[docs] Change the architecture for F08”（提交 `ac1a71c`）中合并，它们在第 5 节和 ADR-0003 的“后果”中说明 F09 的设计会把 `sentences` 加入可保存的值。F04 到 F07 都已验收。F08 设计 1.0 已批准并合并，它的代码在 F09 的代码之前合入。F09 按 3.1 到 3.4 节修改这些接口，3.5 节列出随之修改的测试。

不变的部分：计数函数 `count_words`、`count_lines`、`count_chars` 和 `count_longest` 的签名、行为和错误都不变。`wordcount FILE`、`--lines`、`--chars`、`--longest`，以及已保存的选项不是 `sentences` 时的 `--again`，打印的数、文件错误行、设置错误和警告行以及退出码都与以前相同。设置文件的位置、它的键、其他值的原样字节，以及 F08 关于无法读取的文件的规则都不变。`settings_path`、`settings_name` 以及 `load_option` 和 `save_option` 的签名都不变。`src/troy_mode_trial/__init__.py` 仍然既不导入 cli，也不导入 settings。`pyproject.toml` 中的控制台脚本不变。这个选项的短形式不在范围之内。

### 3.1 `wordcount`

这修改 F04 设计 2.1 节，即 F07 设计 2.1 节和 F08 设计 3.1 节留下的样子。

1. **新选项 `--sentences`。** `wordcount --sentences FILE` 打印 `FILE` 的句子数，而不是词数：正是 `count_sentences(FILE)` 的返回值（2.1 节），在标准输出上写一个十进制数和一个换行符，退出码 0，与其他选项相同。

   | 名称 | 类型 | 含义 | 约束 |
   | --- | --- | --- | --- |
   | `--sentences` | 选项，不带值的开关 | 打印 `FILE` 的句子数，而不是词数。 | 可选。只有全名 `--sentences`。没有短形式；`--sent` 或 `--s` 这样的缩写是错误的命令行，与其他选项相同。它可以写在 `FILE` 之前或之后。写两次与写一次相同。`--sentences=VALUE` 是错误的命令行。它不能与 `--lines`、`--chars`、`--longest` 或 `--again` 一起出现，不论顺序如何（需求 F09、Q13 和 Q21）。在 `--` 之后，文本 `--sentences` 是文件名，不是选项。 |

   这个命令仍然没有 `-h` 或 `--help`，除 `--lines`、`--chars`、`--longest`、`--sentences` 和 `--again` 外没有其他选项（需求第 8 节）。

2. **提议 1，用法行，由 Troy 接受或修改。** 用法行从 F08 的 `usage: wordcount [--lines | --chars | --longest | --again] FILE` 改为：

   ```text
   usage: wordcount [--lines | --chars | --longest | --sentences | --again] FILE
   ```

   `--sentences` 加入这一组互斥的选项，因为一个命令最多取其中一个。这是 Troy 为 F05、F07 和 F08 批准的形式，也正是 argparse 为这组选项写出的行，所以不需要额外的代码。`--sentences` 排在其他计数选项之后、`--again` 之前，与需求中的顺序一致，这样计数选项放在一起，重复其中某一个的 `--again` 仍在最后。另一种做法是把 `--sentences` 加在末尾：`usage: wordcount [--lines | --chars | --longest | --again | --sentences] FILE`，这会让 `--again` 夹在两个计数选项之间。

   这一行长 77 个字符。argparse 在设置了环境变量 `COLUMNS` 时以它为宽度，否则取标准输出所在终端的宽度，再否则用 80 列。宽度至少 79 列时，它把这一行写成一行。窗口更窄时，它把这一行拆成两行；F08 的 63 个字符的用法行在窄于 65 列的窗口中已经如此。用法错误的退出码和第二行不随宽度改变。

3. **新的用法错误。** `--sentences` 与 `--lines`、`--chars`、`--longest` 或 `--again` 一起出现是错误的命令行，退出码 2（需求 F09、Q13 和 Q21）。argparse 先写提议 1 的用法行，再写一行 argparse 自己措辞的消息，先说后出现的选项，与两个计数选项的情况相同（F05 设计 2.1 节，已批准）。例如 `wordcount --lines --sentences notes.txt` 得到 `wordcount: error: argument --sentences: not allowed with argument --lines`，`wordcount --sentences notes.txt --again` 得到 `wordcount: error: argument --again: not allowed with argument --sentences`，`wordcount --again --sentences notes.txt` 得到 `wordcount: error: argument --sentences: not allowed with argument --again`。这个错误先于缺少 `FILE` 的检查。其他用法错误的消息不变，第一行变为提议 1 的用法行。用法错误既不读也不写设置文件，与 F08 相同。

4. **文件错误。** 带 `--sentences` 的文件错误，给出的消息和退出码与 `wordcount FILE` 对同一文件给出的完全相同（需求 F09）：标准错误上一行 `wordcount: <FILE>: <reason>`，退出码 2，标准输出为空；`<FILE>` 和五条原因文本与 F04 设计 2.1 节相同。命令解码整个文件，所以无效字节出现在合法文本之后的文件仍然是 `not valid UTF-8`，不打印任何数。

5. **设置。** 带 `--sentences` 并打印出计数的运行，在计数和换行符写到标准输出之后，把 `"sentences"` 保存到设置文件，与 F08 设计 3.1 节第 6 项对其他选项的说法相同。之后，`wordcount --again FILE` 统计 `FILE` 的句子数，并再次保存 `"sentences"`。带 `--sentences` 但失败的运行，即用法错误或文件错误，不写任何东西，设置保持原样（需求 Q19）。设置文件无法写入时，计数照样打印，带 F08 的警告，退出码 0（需求 Q22）。F08 设计 3.1 节提议 2 中设置错误和警告的文本不变。

6. **安装。** F09 的代码安装后，例如运行 `uv pip install -e . --no-deps`，已安装的 `wordcount` 才有这个选项，与之前的选项相同。

示例，在 Windows 上，用户文件夹是 `C:\Users\me`，使用 2.1 节的文件，以及有 `Hello world` 和 `  troy-mode  trial` 两行的 `notes.txt`：

```text
PS> wordcount --sentences story.txt
4
PS> wordcount story.txt
7
PS> wordcount --sentences draft.txt
1
PS> wordcount --sentences pi.txt
2
PS> wordcount --sentences dashes.txt
0
PS> wordcount --again story.txt
4
PS> Get-Content $env:APPDATA\wordcount\settings.json
{"option": "sentences"}
PS> wordcount --again draft.txt
1
PS> wordcount --sentences missing.txt
wordcount: missing.txt: no such file
PS> $LASTEXITCODE
2
PS> wordcount --lines --sentences notes.txt
usage: wordcount [--lines | --chars | --longest | --sentences | --again] FILE
wordcount: error: argument --sentences: not allowed with argument --lines
PS> $LASTEXITCODE
2
PS> wordcount --sent notes.txt
usage: wordcount [--lines | --chars | --longest | --sentences | --again] FILE
wordcount: error: unrecognized arguments: --sent
PS> $LASTEXITCODE
2
```

`wordcount --again story.txt` 打印 `4`，即 `story.txt` 的句子数，因为它前面的运行 `wordcount --sentences dashes.txt` 打印了计数并保存了 `sentences`。

### 3.2 `main`

这修改 F04 设计 2.2 节，即 F07 设计 2.2 节和 F08 设计 3.2 节留下的样子。

1. **签名。** 不变：`def main(argv: Sequence[str] | None = None) -> int:`。`argv` 现在可以包含 `--sentences`，规则见 3.1 节。
2. **功能。** 在 `--sentences` 时，以及在 `--again` 且已保存的选项是 `"sentences"` 时，它现在还通过 `count_sentences` 得到这个数。它从包 `troy_mode_trial` 导入 `count_sentences`，与另外四个计数函数并列，从不从 `troy_mode_trial.counting` 导入（架构第 4 节）。它从 `troy_mode_trial.settings` 导入的四个名字与 F08 相同。
3. **返回值。** 与 F08 设计 3.2 节相同：把计数和一个换行符写到标准输出之后返回 `0`，之后又写了设置警告时也是如此；把一行文件错误或两条设置错误之一写到标准错误之后返回 `2`。
4. **错误。** 错误的命令行引发退出码为 2 的 `SystemExit`，现在也包括 `--sentences` 与这一组中另一个选项一起出现的情况，这发生在任何 settings 调用和任何计数之前。在调用计数函数的地方，它仍然只捕获 `OSError` 和 `UnicodeDecodeError`，现在也包括来自 `count_sentences` 的。在调用 settings 的地方，它仍然只捕获 `OSError` 和 `ValueError`。只有解析出的参数包含 `--sentences`，或者 `load_option` 返回了 `"sentences"` 时，它才把 `"sentences"` 传给 `save_option`，所以警告永远不会掩盖 F08 设计 2.6 节称为 cli 缺陷的 `ValueError`。其他任何异常都是缺陷，会传给调用方，于是 Python 以退出码 1 退出。
5. **副作用。** 与 F08 设计 3.2 节相同，只是多了一个它会保存的值 `"sentences"`。

示例，`APPDATA` 或 `XDG_DATA_HOME` 设为一个空文件夹，`story.txt` 是 2.1 节的文件：

```python
>>> from troy_mode_trial.cli import main
>>> main(["--sentences", "story.txt"])
4
0
>>> main(["--again", "story.txt"])
4
0
>>> main(["--sentences", "--chars", "story.txt"])
usage: wordcount [--lines | --chars | --longest | --sentences | --again] FILE
wordcount: error: argument --chars: not allowed with argument --sentences
Traceback (most recent call last):
  ...
SystemExit: 2
```

### 3.3 F08 的设置接口

这修改 F08 设计 2.1、2.2、2.5 和 2.6 节，正如 F08 设计第 2 节预见的：F09 在 `OPTION_NAMES` 中加一个名字，`load_option` 和 `save_option` 无需对 settings 做其他修改就接受它。

1. **`OPTION_NAMES`**（F08 设计 2.2 节）在末尾加入 `"sentences"`，顺序与用法行中的计数选项相同：

   ```python
   OPTION_NAMES: Final[tuple[str, ...]] = ("lines", "chars", "longest", "sentences")
   ```

2. **设置文件**（F08 设计 2.1 节）。`"option"` 的值现在可以是 `"sentences"`，对应带 `--sentences` 的运行。`save_option` 按下面的字节原样写入，不带字节顺序标记，在所有系统上都以 `\n` 结尾：

   | 上一次运行 | 文件的字节 |
   | --- | --- |
   | `wordcount --sentences FILE` | `{"option": "sentences"}` 后跟 `\n` |

   键、其他值的字节，以及 F08 错误表的其他各行都不变。只有最后一行中“F09 之前的 `"sentences"`”这个例子不再适用。`"Sentences"`、`"sentence"` 和 `"--sentences"` 仍然无法读取，因为名字是小写，必须完全一致。

3. **`load_option`**（F08 设计 2.5 节）的签名和错误不变。对含 `"sentences"` 的文件，它现在返回 `'sentences'`，而 F08 的代码会抛出 `ValueError`。

4. **`save_option`**（F08 设计 2.6 节）的签名、步骤顺序和错误不变。它现在接受 `"sentences"` 作为 `option`，而 F08 的代码会在碰任何文件夹或文件之前抛出 `ValueError`。

5. **兼容性**（架构第 5 节）。F09 的程序能读取 F08 的程序写出的每个文件，因为 F09 只是加了一个名字。F08 的程序，或任何带 `--again` 的更早的 `wordcount`，把含 `"sentences"` 的文件当作无法读取的文件，正如 F08 设计 2.1 节和 ADR-0003 的“后果”所说。这时它的 `wordcount --again` 给出 F08 的设置错误 `wordcount: cannot read the settings file: <settings file>`，退出码 2；它下一次打印出计数的运行会按 F08 的格式重新写入这个文件。没有 F08 的程序根本不读这个文件。

示例，设置文件在一个临时文件夹中：

```python
>>> from troy_mode_trial.settings import OPTION_NAMES, load_option, save_option, settings_path
>>> OPTION_NAMES
('lines', 'chars', 'longest', 'sentences')
>>> save_option(settings_path(), "sentences")
>>> settings_path().read_bytes()
b'{"option": "sentences"}\n'
>>> load_option(settings_path())
'sentences'
```

### 3.4 包的导出

`src/troy_mode_trial/__init__.py` 导出 `count_sentences`，与 `count_chars`、`count_lines`、`count_longest` 和 `count_words` 并列，并把它加入 `__all__`。这只是加一个名字，不改变已有的名字。`__init__.py` 仍然既不导入 cli，也不导入 settings，也不从它们导出任何东西（架构第 4 节）。

### 3.5 随 F09 修改的测试

下面这些已有测试在 F09 的测试计划中修改，它们属于测试经理。F04 到 F07 已验收，F08 到那时也可能已验收，所以已验收功能的用例在每个 F09 PR 中都必须通过，无论 F09 的代码合入之前还是之后（R10）。`--sentences` 可用之后，它们期望的用法行变为提议 1 的用法行；在此之前仍是 F08 的用法行，与 F08 的测试计划处理 F08 的修改的方式相同。

1. **F05 的用法行。** `tests/test_cli_lines.py` 中的 `USAGE_ALL`（即 F08 的测试计划留下的样子），以及逐字比较第一行的用例。它们的第二行不变。
2. **F07 的用法行。** `tests/test_cli_longest.py` 中的 `USAGE`（即 F08 的测试计划留下的样子），按同样的方式修改。
3. **F08 的用法行。** F08 的测试计划中逐字比较用法行的用例，按同样的方式修改。它们的第二行，例如 `argument --again: not allowed with argument --lines`，不变。
4. **F08 中关于 `sentences` 的用例。** F08 的测试计划中凡是期望 `"sentences"` 为未知名字的用例都要修改：含 `"sentences"` 的设置文件现在读出 `'sentences'`，`save_option(path, "sentences")` 现在写出 3.3 节的字节，`OPTION_NAMES` 是 3.3 节的元组。使用其他未知名字的用例，例如 `"Lines"` 或 `"--lines"`，不变。
5. **不变的用法行。** `tests/test_cli_chars.py` 中 F06 的模式接受 ` FILE` 之前任何含 `--chars` 的方括号，新的用法行写成一行时仍然符合。`tests/test_cli.py` 和版本测试只检查这一行是否以 `usage: wordcount ` 或 `usage:` 开头。
6. **设置文件夹。** F09 不新增夹具。它调用 `main` 或运行已安装的 `wordcount` 的测试，使用 F08 在 `tests/conftest.py` 和 `version-tests/conftest.py` 中的自动夹具，它们为每个测试把 `APPDATA` 和 `XDG_DATA_HOME` 设为一个新的空文件夹（架构第 10 节，ADR-0003），所以 F09 的测试都不会读写真实的设置文件。
7. **用法行的宽度。** 逐字比较用法行的用例期望提议 1 的单行形式；argparse 在 3.1 节第 2 项所说的宽度至少 79 列时写出这一形式：`COLUMNS` 未设置或至少 79，并且标准输出不是更窄的终端。

## 4. 架构师审查

| 项目 | 结果 | 备注 |
| --- | --- | --- |
| 符合模块划分和数据模型 | 通过 | `count_sentences` 位于 counting，经 `src/troy_mode_trial/__init__.py` 导出，而 `__init__.py` 仍然既不导入 cli 也不导入 settings（架构第 3、4 节）。本设计不在 `src/troy_mode_trial/` 下新增文件。新的可保存值 `sentences` 正是架构第 5 节和 ADR-0003 已预见的，设置文件的位置、键和其他字节都不变。3.3 节第 5 项按架构第 5 节的要求说明了更早的版本如何对待 F09 写出的文件。 |
| 遵守错误处理和命名约定 | 通过 | `count_sentences` 不定义异常，让 Python 自己的异常传出，错误表与另外四个计数函数相同（架构第 6 节）。cli 在计数处仍只捕获 `OSError` 和 `UnicodeDecodeError`，在 settings 处仍只捕获 `OSError` 和 `ValueError`，并且只把已知名字传给 `save_option`。名字沿用 `count_` 前缀。标准输出仍只有计数。 |
| 不和已有接口重复 | 通过 | 没有已有接口统计句子。2.1 节要求在 counting 内部与 `count_words` 共用同一套文件读取和同一个“字母或数字”判断，而不是再写一份。可保存的名字仍只在元组 `OPTION_NAMES` 一处。 |
| 只依赖排序在前面的功能 | 通过 | 硬依赖 F04 已验收。F09 还以 F08 已设计的接口为基础，而 F08 在顺序中排在 F09 之前（F01、F03、F04、F07、F06、F02、F05、F08、F09），设计已合并，需求第 5 节记录了 Troy 的这一选择。第 2 节说明 F09 的代码在 F08 的代码之后合入。 |
| 不在模块之间增加隐性耦合 | 通过 | cli 把选项对应到计数函数和要保存的名字。settings 只在 `OPTION_NAMES` 中多知道一个名字，对 counting 一无所知。counting 不碰设置文件（2.1 节，副作用）。 |
| 修改已实现的接口时走了变更流程 | 通过 | 对已验收的 `wordcount`、`main`、用法行以及已验收测试的修改，来自 Troy 经变更流程批准的需求 8.0。第 3 节列出改什么、不改什么，3.5 节把已验收功能中要改的测试交给 F09 的测试计划，使它们在 F09 的代码合入前后都能通过，与 F08 相同。F08 的设置接口已设计但尚未实现。 |
| 给 Troy 的摘要和设计说的一致，并列出了需要 Troy 决定的每一件事 | 通过 | 摘要用设计自己的例子给出句子规则，并说明 `--again` 与 `--sentences`、文件错误和用法错误。它列出唯一的提议——用法行——及其两个选项和推荐，也列出两条风险：更早的 `wordcount` 读不了含 `sentences` 的设置文件；77 个字符的用法行在窄于 79 列时拆成两行。已用设计中的解析器在 Python 3.14.3 上运行 argparse 核对：这一行长 77 个字符，`COLUMNS=79` 时保持一行，78 时在 `FILE` 之前换行；三条“not allowed with”消息与 3.1 节第 3 项逐字相同；`--sent` 给出 `unrecognized arguments: --sent`，退出码 2。2.1 节表中每一行按所述规则也都得到所述结果。 |

| 轮次 | 问题 | 解决方式 |
| --- | --- | --- |
| 1 | 无。七项全部通过。有风险：Troy 保留的设置文件现在可能含 `sentences`，更早的 `wordcount` 读不了它。 | 批准。 |

## 5. 修改记录

| 版本 | 日期 | 修改 |
| --- | --- | --- |
| 0.1 | 2026-11-26 | 初稿。 |
