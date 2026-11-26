---
troy-doc: "F10-design"
lang: "zh-CN"
version: "0.1"
updated: "2026-11-26"
status: "草稿，架构师审查中。"
mirror-of: "design.md"
---

# F10 统计段落数的函数：接口设计

## 1. 功能

- 编号和名称：F10 Count paragraphs function（统计段落数的函数）
- 需求：[docs/requirements.zh-CN.md](../../requirements.zh-CN.md#4-功能点)
- 硬依赖：F04
- 软依赖：无

## 2. 接口

F10 新增一个接口，即模块 counting 中的库函数 `count_paragraphs`。它不新增文件：函数位于 `src/troy_mode_trial/counting.py`，这个文件已经属于 counting（架构第 3 节）。F10 不给 `wordcount` 新增选项、消息或文件（需求 F10 和第 8 节）。

### 2.1 `count_paragraphs`

- 模块：counting，位于 `src/troy_mode_trial/counting.py`。调用方从包 `troy_mode_trial` 导入它：`src/troy_mode_trial/__init__.py` 在 `count_chars`、`count_lines`、`count_longest` 和 `count_words` 旁边导入它，并把 `"count_paragraphs"` 加入 `__all__`。
- 功能：返回调用方手里一段 `str` 文本的段落数。段落是一串连续的非空白行。和其他计数函数不同，它接收的是文本本身，而不是文件路径，也不读取任何文件。

签名：

```python
def count_paragraphs(text: str) -> int:
```

参数：

| 名称 | 类型 | 含义 | 约束 |
| --- | --- | --- | --- |
| `text` | `str` | 要统计段落的文本，例如调用方读出的某个文件的内容。 | 任何 `str`，包括空字符串和 `str` 的子类。其他类型，例如 `bytes`、`None` 或 `pathlib.Path`，抛出 `TypeError`。函数从不把 `text` 当作路径，所以 `count_paragraphs("notes.txt")` 统计的是一行文字 `notes.txt`，返回 1。 |

- 返回值：`int`，`text` 中的段落数，大于或等于 0。函数分四步算出结果。

  1. **字节顺序标记。** 如果 `text` 以 U+FEFF 开头，函数忽略这一个字符（Q29）。其他位置的 U+FEFF，包括开头的第二个，都是普通字符。
  2. **行。** 函数把余下的文本分成行。结束一行的序列恰好有三种：`\n`、`\r\n` 和 `\r`（Q28）。紧跟 `\n` 的 `\r` 合起来是一个行尾 `\r\n`，不是两个，所以 `a\r\nb` 是两行，中间没有空行。其他字符都不结束一行：Python 的 `str.splitlines()` 视为换行的其他字符，`\v`（U+000B）、`\f`（U+000C）、U+001C、U+001D、U+001E、U+0085、U+2028 和 U+2029，都是普通字符，和 F02 相同。因此函数不得用 `str.splitlines()` 分行。以行尾结束的文本，后面不再多出一个空行；这不影响结果，因为这样的行本来就是空白行。
  3. **空白行。** 一行为空，或者其中每个字符都使 `str.isspace()` 为真，这一行就是空白行（Q27、Q1）。所以只含空格、制表符、U+3000、`\f` 或 U+2028 的行是空白行。含有其他任何字符的行都不是空白行，即使那个字符看不见，例如 U+200B 或 U+FEFF，因为它们的 `str.isspace()` 为假。
  4. **段落。** 段落是一串尽可能长的连续非空白行。结果就是这样的串的个数：每个非空白行，如果是第一行或者紧跟在空白行之后，就开始一个段落。两个段落之间不管有多少空白行，都只分隔一次；开头和结尾的空白行不计。空文本或只有空白行的文本返回 0。

  | `text`（Python 字面量） | 结果 | 原因 |
  | --- | --- | --- |
  | `""` | `0` | 空文本。 |
  | `"\n\n   \n"` | `0` | 只有空白行。 |
  | `"\r\n"` | `0` | 一个空行。 |
  | `"One"` | `1` | 一行，没有行尾。 |
  | `"\n\nOne\n\n"` | `1` | 开头和结尾的空白行不计。 |
  | `"First line\nstill the first paragraph\n\nSecond paragraph\n"` | `2` | 原型的第一个例子。 |
  | `"One\r\n  \t\r\nTwo\r\n\r\n\r\nThree"` | `3` | 只含空格和制表符的行是空白行，三个空白行只分隔一次。 |
  | `"a\r\nb"` | `1` | `\r\n` 是一个行尾，所以中间没有空行。 |
  | `"a\rb\r\rc"` | `2` | 单独的 `\r` 结束一行：各行是 `a`、`b`、一个空行和 `c`。 |
  | `"a\n\rb"` | `2` | 先 `\n` 后 `\r` 是两个行尾，中间有一个空行。 |
  | `"a\n　\nb"` | `2` | U+3000 是空白字符，所以它所在的行是空白行。 |
  | `"a\n\f\nb"` | `2` | `\f` 是空白字符，所以它所在的行是空白行。 |
  | `"a\fb"` | `1` | `\f` 不结束一行。 |
  | `"a b"` | `1` | U+2029 不结束一行。 |
  | `"﻿a\n\nb"` | `2` | 开头的字节顺序标记被忽略。 |
  | `"﻿"` | `0` | 只有字节顺序标记。 |
  | `"﻿﻿"` | `1` | 只忽略第一个 U+FEFF，第二个不是空白字符。 |
  | `"a\n﻿\nb"` | `1` | 只含 U+FEFF 的行不是空白行，所以这三行是一个段落。 |

错误：

函数不读取文件，所以不抛出文件错误（需求第 3 节）。它不定义自己的异常（架构第 6 节）。

| 错误 | 何时发生 |
| --- | --- |
| `TypeError` | `text` 不是 `str`，例如 `bytes`、`None`、`int` 或 `pathlib.Path`。消息说出收到的类型，例如 `text must be str, not bytes`。按照 P01，代码先在变量里构造消息，再抛出异常。 |

- 副作用：无。函数不读文件、不写任何东西、不保存状态，也不改变 `text`。同一个 `text` 在 Windows 和 Linux 上总是得到同样的结果。
- 性能指标：无

示例：

`notes.txt` 是 UTF-8 文件，含三行：`Hello world`、一个空行和 `troy-mode trial`。

```python
>>> from pathlib import Path
>>> from troy_mode_trial import count_paragraphs
>>> count_paragraphs("First line\nstill the first paragraph\n\nSecond paragraph\n")
2
>>> count_paragraphs("One\r\n  \t\r\nTwo\r\n\r\n\r\nThree")
3
>>> count_paragraphs("\n\n   \n")
0
>>> count_paragraphs("")
0
>>> count_paragraphs(Path("notes.txt").read_text(encoding="utf-8"))
2
>>> count_paragraphs(b"One\n\nTwo")
Traceback (most recent call last):
  ...
TypeError: text must be str, not bytes
```

## 3. 对已有接口的修改

无。F10 是新功能，Troy 已在需求 9.0 中批准（提交 `ae27a27`）。`src/troy_mode_trial/__init__.py` 在导入和 `__all__` 中加入名称 `count_paragraphs`，现在导出的每个名称都保留。`count_chars`、`count_lines`、`count_longest` 和 `count_words` 的签名、行为和错误都不变。F10 不使用也不修改 F04 的任何接口：`wordcount` 和 `main` 打印、写出和返回的内容与以前完全相同。没有已有的测试用例被修改或停用。

## 4. 架构师审查

| 项目 | 结果 | 备注 |
| --- | --- | --- |
| 符合模块划分和数据模型 | 通过 | 函数放在 `src/troy_mode_trial/counting.py`，由 counting 的对外接口 `src/troy_mode_trial/__init__.py` 导出；这两个文件都归 counting，所以模块表不用改。它不读也不写文件，不保存状态，所以不给第 5 节的数据模型增加任何内容，也符合第 8 节"counting 不写文件"的规则。F09 可能也会往 `__init__.py` 加一个名称；两处修改改的是同一个文件，但不是同一个接口。 |
| 遵守错误处理和命名约定 | 通过 | 它不定义自己的异常，只抛出 Python 的 `TypeError`，符合第 6 节对 counting 的要求。消息 `text must be str, not <type>` 和已有的 `path must be str or os.PathLike, not <type>` 形式一致，设计也按 P01 先把消息放进变量。名称沿用 `count_` 加所数对象的 snake_case 形式。 |
| 不和已有接口重复 | 通过 | 没有已有函数数段落，也没有已有函数直接接收文本。行尾沿用 `count_lines`（`\n`、`\r\n`、单独的 `\r`，绝不用 `str.splitlines()`），空白行沿用 Q1 的空白字符，所以设计复用已有定义，没有另立新定义。 |
| 只依赖排序在前面的功能 | 通过 | 它唯一的硬依赖 F04 在排序中排在 F10 前面，F10 排在最后。设计不使用 F04 的任何接口。 |
| 不在模块之间增加隐性耦合 | 通过 | 只有 counting 改变。cli 和 settings 不变，函数也不导入它们。 |
| 修改已实现的接口时走了变更流程 | 通过 | 没有已实现的接口改变。`__init__.py` 只在导入和 `__all__` 中加一个名称，现在导出的每个名称都保留。 |
| 给 Troy 的摘要和设计说的一致，并列出了需要 Troy 决定的每一件事 | 通过 | 摘要写了调用方式、传文本而不是路径、空白行和段落的规则、行尾、字节顺序标记、`TypeError`，以及 `wordcount` 不变，都和设计一致。风险和设计中 U+200B、不在开头的 U+FEFF、U+2029 和 `bytes` 这几行一致。Q27 到 Q29 已有决定，没有留给 Troy 决定的事。 |

| 轮次 | 问题 | 解决方式 |
| --- | --- | --- |
| 1 | 没有阻塞问题。给接口设计师一条不阻塞的建议：第 2.1 节第 4 步的表中，U+3000、U+2029 和 U+FEFF 那几行直接写入了这些字符，所以"只有字节顺序标记"和"只忽略第一个 U+FEFF"两行看起来像空文本，U+2029 那行看起来像普通空格。以后的版本改写成 `"\ufeff"`、`"a\u2029b"`、`"a\n\u3000\nb"` 这样的转义，能帮测试经理准确照抄。 | 第 1 轮批准。 |

## 5. 修改记录

| 版本 | 日期 | 修改 |
| --- | --- | --- |
| 0.1 | 2026-11-26 | 初稿。 |
