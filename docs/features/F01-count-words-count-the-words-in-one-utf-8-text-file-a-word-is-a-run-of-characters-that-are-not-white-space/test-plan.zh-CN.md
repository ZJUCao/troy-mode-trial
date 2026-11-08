---
troy-doc: "F01-test-plan"
lang: "zh-CN"
version: "2.0"
updated: "2026-11-07"
status: "Troy 已于 2026-11-07 批准"
mirror-of: "test-plan.md"
---

# F01 统计词数：测试方案

## 1. 功能

- 编号和名称：F01 统计词数：统计一个 UTF-8 文本文件里的词数。一个词是一串连续的非空白字符。
- 设计：[design.zh-CN.md](design.zh-CN.md)

## 2. 用例

每个用例都像调用方一样调用函数：`from troy_mode_trial import count_words`。每个测试在 pytest 的 `tmp_path` 里自建文件，并以二进制方式写入用例给出的确切字节，这样 Windows 不会把 `\n` 改成 `\r\n`。输入中的 `\uXXXX` 表示一个 Unicode 字符，测试把它编码为 UTF-8。测试套件在 Windows 11 和 Linux 上运行，除非用例另有说明，每个用例在两个平台上预期相同的结果。

| 编号 | 层级 | 接口 | 测什么 | 准备和输入 | 预期结果 |
| --- | --- | --- | --- | --- | --- |
| F01-T01 | 功能 | `count_words` | 设计中的示例：两行文字，有行首、行尾和连续的空格，末尾没有换行符。 | `notes.txt` 内容为 `Hello world\n  troy-mode  trial`。以 `str` 形式传入其路径调用 `count_words`。 | 返回 `4`，且结果的类型恰好是 `int`。 |
| F01-T02 | 单元 | `count_words` | 空文件没有词（Q3）。 | 一个空文件。 | 返回 `0`。 |
| F01-T03 | 单元 | `count_words` | 只含空白的文件没有词（Q3）。 | 三个文件：`   `、`\n` 和 `\t \r\n \v\f\r`。 | 每个都返回 `0`。 |
| F01-T04 | 单元 | `count_words` | 一串不含空白的字符是一个词，即使其中有标点和数字。 | 三个文件：`a`、`troy-mode` 和 `x=1,y=2;`。 | 每个都返回 `1`。 |
| F01-T05 | 单元 | `count_words` | 每个 ASCII 空白字符都分隔词，连续多个只算一个间隔。 | `\tone  two\t\tthree\vfour\ffive \n six  ` | 返回 `6`。 |
| F01-T06 | 单元 | `count_words` | Unicode 空白分隔词（Q1）。 | `甲　乙 丙 丁 戊\u0085己` | 返回 `6`。 |
| F01-T07 | 单元 | `count_words` | `str.isspace()` 为假的字符不分隔词，即使它看起来是空白。 | `a​b c⁠d`（零宽空格和连字符号 word joiner） | 返回 `2`。 |
| F01-T08 | 单元 | `count_words` | `\n`、`\r\n` 和 `\r` 都是空白，得到相同的计数。 | 三个文件，词相同：`one two\nthree\nfour`、`one two\r\nthree\r\nfour` 和 `one two\rthree\rfour`。第四个文件以 `four\r\n` 结尾。 | 四个文件都返回 `4`。 |
| F01-T10 | 单元 | `count_words` | 忽略文件开头的一个字节顺序标记（Q5）。 | 四个文件：字节 `EF BB BF` 后接 `one two`；只有 `EF BB BF`；`EF BB BF` 后接 ` word`；`EF BB BF` 后接 `\n`。 | 依次返回 `2`、`0`、`1` 和 `0`。 |
| F01-T12 | 单元 | `count_words` | 在大文件中计数仍然正确，此时词或空白串可能跨越任何内部读取边界。 | 一个文件：200,000 个 `word ` 相连，每第 1,000 个空格换成一个换行符，其后接一个由 100,000 个 `x` 组成的词，再接 `　end`。文件大于 1 MiB。 | 返回 `200002`。 |
| F01-T13 | 功能 | `count_words` | `path` 的每种合法形式得到相同的计数。 | 一个内容为 `one two three` 的文件。分别以 `str` 形式的绝对路径、`pathlib.Path`，以及一个实现了 `__fspath__` 并返回 `str` 的测试类对象调用。 | 每个都返回 `3`。 |
| F01-T14 | 功能 | `count_words` | 相对路径按当前工作目录解析。 | 在 `tmp_path` 中建文件 `words.txt`，内容为 `alpha beta`。用 `monkeypatch.chdir` 把 `tmp_path` 设为工作目录，再分别以 `"words.txt"` 和 `pathlib.Path("words.txt")` 调用。 | 每个都返回 `2`。 |
| F01-T15 | 功能 | `count_words` | 文件不存在时抛出 Python 自带的异常（Q4）。 | `tmp_path` 中一个不存在任何东西的路径，分别以 `str` 和 `pathlib.Path` 传入。 | 每个都抛出 `FileNotFoundError`。 |
| F01-T16 | 功能 | `count_words` | 路径指向文件夹时抛出 Python 自带的异常。 | `tmp_path` 本身，以 `str` 传入。 | 抛出 `IsADirectoryError` 或 `PermissionError`。在 Linux 上抛出 `IsADirectoryError`。 |
| F01-T17 | 功能 | `count_words` | 进程无权读取的文件抛出 `PermissionError`。 | 仅限 Linux：一个内容为 `one two` 的文件，权限设为 `0o000`。在 Windows 上跳过，因为测试无法可移植地去掉自己的读权限；以 root 运行时也跳过，因为 root 仍能读取该文件。测试结束后恢复权限。 | 抛出 `PermissionError`。 |
| F01-T18 | 功能 | `count_words` | 内容不是合法 UTF-8 时抛出 Python 自带的异常（Q4）。 | 三个文件：Latin-1 编码的 `café`（`63 61 66 E9`，与原型一致）；`ok ` 后接被截断的序列 `E6 97`；带字节顺序标记的 UTF-16 编码的 `hello`。 | 每个都抛出 `UnicodeDecodeError`。 |
| F01-T19 | 功能 | `count_words` | 其他类型的 `path` 抛出 `TypeError`。 | 分别以 `b"words.txt"`（`bytes`）、一个已打开文件（内容为 `one two`）的整数文件描述符、`None`、`3.5`，以及一个 `__fspath__` 返回 `bytes` 的对象调用。测试结束后关闭该描述符。 | 每个都抛出 `TypeError`。 |
| F01-T20 | 功能 | `count_words` | 函数在返回和抛出异常之前关闭文件。 | 用 `warnings.catch_warnings(record=True)` 和 `simplefilter("always", ResourceWarning)` 记录警告。对内容为 `one two` 的文件调用一次 `count_words`，再对一个会抛出 `UnicodeDecodeError` 的文件调用一次。然后运行 `gc.collect()`，并把每个文件改名为 `tmp_path` 中的新名字。 | 没有记录到 `ResourceWarning`，两次改名都成功。在 Windows 上，改名能发现仍打开的文件，因为 Windows 无法给打开的文件改名。 |
| F01-T21 | 功能 | `count_words` | 函数不写入也不保存任何东西。 | 一个内容为 `one two` 的文件。记录它的字节、以纳秒计的修改时间，以及 `tmp_path` 中的条目列表。调用 `count_words` 两次。 | 两次都返回 `2`。文件的字节和修改时间不变，`tmp_path` 中的条目与之前相同。 |

## 3. 性能用例

无。设计没有给 `count_words` 设性能指标，需求 7.1 也没有给项目设任何性能指标（R14）。

## 4. 不测的内容

| 内容 | 原因 |
| --- | --- |
| 异常消息的文字，例如设计示例中的 `[Errno 2] No such file or directory: 'missing.txt'`。 | 消息由 Python 生成，设计只承诺异常类型（Q4）。F01-T15 到 F01-T19 检查类型。 |
| Windows 上不可读文件的 `PermissionError`。 | 在 Windows 上去掉文件的读权限需要访问控制列表，可移植的测试无法可靠地设置和恢复。F01-T17 在 Linux 上检查同一行为。 |
| 性能。 | 没有性能指标（R14）。 |
| F01-T09：`café naïve 日本語 😀 Ελληνικά` 中的词各算一次，预期 `5`。 | 被 F03 退役。F03 把预期结果改为 `4`，因为 `😀` 不含字母或数字。F03-T06 覆盖这个输入。 |
| F01-T11：出现在第一个字符以外位置的 U+FEFF 是词的一部分。文件 `a <U+FEFF> b`、`a<U+FEFF>b` 和开头有两个标记的文件，依次预期 `3`、`1` 和 `1`。 | 被 F03 退役。F03 把预期结果改为 `2`、`1` 和 `0`，因为单独的 U+FEFF 不是词。F03-T09 覆盖第一个和第三个文件。第二个文件的结果仍是 `1`，F03-T09 把它和一个单独的标记合成 `a<U+FEFF>b <U+FEFF>`，使测试在当前代码上失败（R09）。 |

## 5. 与接口设计师的对齐记录

无。设计已回答本方案提出的所有问题。

## 6. 修改记录

| 版本 | 日期 | 修改 |
| --- | --- | --- |
| 0.1 | 2026-11-07 | 初稿。 |
| 1.1 | 2026-11-07 | 把预期结果被 F03 改变的 F01-T09 和 F01-T11 退役，移到第 4 节。 |
