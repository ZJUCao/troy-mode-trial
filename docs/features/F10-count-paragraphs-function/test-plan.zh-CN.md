---
troy-doc: "F10-test-plan"
lang: "zh-CN"
version: "0.1"
updated: "2026-11-26"
status: "草稿，正在和接口设计师对齐。"
mirror-of: "test-plan.md"
---

# F10 统计段落数的函数：测试方案

## 1. 功能

- 编号和名称：F10 统计段落数的函数：返回调用方以 Python `str` 持有的一段文本中的段落数。段落是连续的非空白行。
- 设计：[design.zh-CN.md](design.zh-CN.md)

## 2. 用例

每个用例都像调用方一样调用函数：`from troy_mode_trial import count_paragraphs`。输入是 Python 字符串字面量，测试按原样写出。每个不可见或看起来像空格的字符都写成转义：`\xXX` 和 `\uXXXX` 各表示一个 Unicode 字符，例如 `\u3000`（全角空格）、`\u2029`（段落分隔符）和 `\ufeff`（字节顺序标记）。测试从不直接键入这些字符本身。一个用例列出多个输入时，测试逐个检查每个输入，并报告是哪一个失败。测试套件在 Windows 11 和 Linux 上运行，每个用例在两个平台上预期相同的结果。

| 编号 | 层级 | 接口 | 测什么 | 准备和输入 | 预期结果 |
| --- | --- | --- | --- | --- | --- |
| F10-T01 | 功能 | `count_paragraphs` | 设计和原型中的示例。 | 四次调用：`"First line\nstill the first paragraph\n\nSecond paragraph\n"`、`"One\r\n  \t\r\nTwo\r\n\r\n\r\nThree"`、`"\n\n   \n"` 和 `""`。 | 返回 `2`、`3`、`0` 和 `0`。每个结果的类型恰好是 `int`。 |
| F10-T02 | 单元 | `count_paragraphs` | 空文本，以及只有空白行的文本，没有段落。 | `""`、`"\n"`、`"\r"`、`"\r\n"`、`" "`、`"\t"`、`"\n\n   \n"`、`"\t\n\r\n\r \r"` 和 `"\u3000\n\u3000"`。 | 每个都返回 `0`。 |
| F10-T03 | 单元 | `count_paragraphs` | 一串连续的非空白行是一个段落，开头或末尾的空白行不计。 | `"One"`、`"One\n"`、`"a\nb\nc"`、`"\n\nOne\n\n"`、`"  \n\t\nOne\r\n \r\n"` 和 `"\r\rOne\r\r"`。 | 每个都返回 `1`。 |
| F10-T04 | 单元 | `count_paragraphs` | 两个段落之间不论有多少空白行，都只分隔一次。 | `"a\n\nb"`、`"a\n\n\n\nb"`、`"a\n \n\t\n\nb"` 和 `"a\nb\n\nc\nd\n\n\n\ne\n"`。 | 返回 `2`、`2`、`2` 和 `3`。 |
| F10-T05 | 单元 | `count_paragraphs` | 一行中每个字符都是 `str.isspace()` 定义的空白时，该行是空白行（Q27、Q1），包括空格和制表符以外的空白。 | 对下列每个 `c` 各取一段文本 `"a\n" + c + "\nb"`：`" "`、`"\t"`、`"\u3000"`、`"\xa0"`、`"\f"`、`"\v"`、`"\x1c"`、`"\x1d"`、`"\x1e"`、`"\x85"`、`"\u2028"`、`"\u2029"` 和 `" \t\u3000\f "`。 | 每个都返回 `2`。 |
| F10-T06 | 单元 | `count_paragraphs` | 一行只要含有一个非空白字符就不是空白行，即使该字符不可见。 | `"a\n\u200b\nb"`、`"a\n \u200b \nb"`、`"a\n\ufeff\nb"` 和 `"a\n\n\u200b\n\nb"`。 | 返回 `1`、`1`、`1` 和 `3`。 |
| F10-T07 | 单元 | `count_paragraphs` | 结束一行的恰好是 `\n`、`\r\n` 和单独的 `\r`（Q28）。紧跟 `\n` 的 `\r` 是一个行结束符。 | `"a\r\nb"`、`"a\rb"`、`"a\rb\r\rc"`、`"a\n\rb"`、`"a\r\rb"`、`"a\r\n\r\nb"`、`"a\r\n\rb"` 和 `"a\r\r\nb"`。 | 返回 `1`、`1`、`2`、`2`、`2`、`2`、`2` 和 `2`。 |
| F10-T08 | 单元 | `count_paragraphs` | `str.splitlines()` 视为换行的其他字符都是普通字符，与 F02 相同。 | 对 `"\v"`、`"\f"`、`"\x1c"`、`"\x1d"`、`"\x1e"`、`"\x85"`、`"\u2028"` 和 `"\u2029"` 中的每个 `c`：文本 `"a" + c + "b"`，以及文本 `"a" + c + c + "b"`。 | 16 段文本每个都返回 `1`。用 `str.splitlines()` 拆分时，每对中的第二段文本会得到 `2`。 |
| F10-T09 | 单元 | `count_paragraphs` | 同一段文本不论用哪种行结束符，包括混用时，计数都相同。 | `"alpha\nbeta\n\ngamma\n\n\ndelta\n"`、`"alpha\r\nbeta\r\n\r\ngamma\r\n\r\n\r\ndelta\r\n"`、`"alpha\rbeta\r\rgamma\r\r\rdelta\r"` 和 `"alpha\r\nbeta\r\rgamma\n\r\ndelta"`。 | 每个都返回 `3`。 |
| F10-T10 | 单元 | `count_paragraphs` | 文本开头的一个 U+FEFF 被忽略（Q29）。开头的第二个，或其他位置的 U+FEFF，是普通字符。 | `"\ufeffa\n\nb"`、`"\ufeff"`、`"\ufeff\n \n"`、`"\ufeff\r\n\r\nOne"`、`"\ufeff\ufeff"`、`"\ufeff\ufeff\n\nb"`、`"a\n\n\ufeff"` 和 `"a\n\ufeff\nb"`。 | 返回 `2`、`0`、`0`、`1`、`1`、`2`、`2` 和 `1`。 |
| F10-T11 | 功能 | `count_paragraphs` | 函数统计它拿到的文本，从不把它当作路径，即使存在同名文件。 | 在 `tmp_path` 中，`notes.txt` 的字节为 `Hello world\n\ntroy-mode trial\n`。用 `monkeypatch.chdir` 把 `tmp_path` 设为工作目录。先用 `"notes.txt"` 调用，再用 `str(tmp_path / "notes.txt")` 调用。 | 每个都返回 `1`，即路径文本本身的一行，而不是文件的 `2` 个段落。 |
| F10-T12 | 功能 | `count_paragraphs` | 接受 `str` 的子类，并像 `str` 一样统计。 | 测试类 `class Text(str)`。用 `Text("One\n\nTwo")` 和 `Text("")` 调用。 | 返回 `2` 和 `0`。每个结果的类型恰好是 `int`。 |
| F10-T13 | 功能 | `count_paragraphs` | 不是 `str` 的 `text` 引发 `TypeError`，其消息写出收到的类型。 | 用 `b"One\n\nTwo"`（`bytes`）、`None`、`3` 和 `pathlib.Path("notes.txt")` 调用，其中 `notes.txt` 像 F10-T11 一样存在于工作目录中。 | 每个都引发 `TypeError`。对 `bytes`，消息恰好是 `text must be str, not bytes`。对其他每个值 `x`，消息以 `text must be str, not ` 开头，并含有 `type(x).__name__`。 |
| F10-T14 | 功能 | `count_paragraphs` | 函数不保留状态、不写任何东西，也不改动 `text`。 | 把 `tmp_path` 设为工作目录，记录其中的条目。令 `t = "One\r\n\r\nTwo\n"`，并保留 `copy = "".join(list(t))`。调用 `count_paragraphs(t)` 三次，在第一次和第二次之间用 `"x\n\ny\n\nz"` 调用一次。 | 对 `t` 的每次调用返回 `2`，中间那次返回 `3`。`t == copy`。`tmp_path` 中的条目与之前相同。 |
| F10-T15 | 集成 | `count_paragraphs`、`count_lines` | 包导出 `count_paragraphs`，并保留之前导出的每个名字；设计中调用方先读文件再统计的示例可用。 | `from troy_mode_trial import count_chars, count_lines, count_longest, count_paragraphs, count_words`。在 `tmp_path` 中，`notes.txt` 的字节为 `Hello world\n\ntroy-mode trial`。对它调用 `count_paragraphs(pathlib.Path(...).read_text(encoding="utf-8"))`，并对它的路径调用 `count_lines`。 | `count_paragraphs` 返回 `2`，`count_lines` 返回 `3`。`troy_mode_trial.__all__` 含有 `"count_paragraphs"`、`"count_chars"`、`"count_lines"`、`"count_longest"` 和 `"count_words"`。 |

## 3. 性能用例

无。设计没有为 `count_paragraphs` 设定性能指标（R14）。

## 4. 不测的内容

| 内容 | 原因 |
| --- | --- |
| `wordcount` 和 `main` 的输出、写入和返回与之前完全相同，且没有段落选项。 | F10 不改这两个接口（设计第 3 节）。F04 到 F09 的现有测试用例已经检查它们的输出，并继续运行。针对未改变行为的新测试在模拟实现上会通过，而 R09 不允许这样。 |
| `bytes` 以外类型的 `TypeError` 消息的确切文字。 | 设计只给出 `bytes` 的确切文字，其余只给出 `text must be str, not <type>` 的格式。F10-T13 对 `bytes` 检查确切文字，对其他类型检查格式和类型名。 |
| 性能，以及比上述用例更大的文本。 | 没有性能指标（R14）。设计对大小没有任何承诺。 |

## 5. 与接口设计师的对齐记录

无。设计回答了本方案提出的所有问题。按照架构师在设计第 1 轮评审中的备注，本方案把设计第 2.1 节表格中 U+3000、U+2029 和 U+FEFF 的输入写成转义（`\u3000`、`\u2029`、`\ufeff`）。我按码位读取了这些行：它们是 `"a\n\u3000\nb"`、`"a\u2029b"`、`"\ufeffa\n\nb"`、`"\ufeff"`、`"\ufeff\ufeff"` 和 `"a\n\ufeff\nb"`，F10-T05、F10-T08 和 F10-T10 覆盖了每一行。

## 6. 修改记录

| 版本 | 日期 | 修改 |
| --- | --- | --- |
| 0.1 | 2026-11-26 | 初稿。 |
