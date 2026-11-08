---
troy-doc: "F03-design"
lang: "zh-CN"
version: "1.0"
updated: "2026-11-07"
status: "Troy 已于 2026-11-07 批准"
mirror-of: "design.md"
---

# F03 词须含字母或数字：接口设计

## 1. 功能

- 编号和名称：F03 Words need a letter or digit（词须含字母或数字）
- 需求：[docs/requirements.zh-CN.md](../../requirements.zh-CN.md#4-功能点)
- 硬依赖：F01
- 软依赖：无

## 2. 接口

无。F03 不新增接口，它修改 F01 的 `count_words` 统计的内容，见第 3 节。

## 3. 对已有接口的修改

需求 2.0 在已合并的 [docs] PR [#16](https://github.com/ZJUCao/troy-mode-trial/pull/16) 中批准了这项修改。

### 3.1 `count_words` 只统计含字母或数字的串

修改的是 F01 设计 2.1 节的 [`count_words`](../F01-count-words-count-the-words-in-one-utf-8-text-file-a-word-is-a-run-of-characters-that-are-not-white-space/design.zh-CN.md#21-count_words)，它属于模块 counting。

不变的部分：

- 签名：`def count_words(path: str | os.PathLike[str]) -> int:`
- 参数、错误、副作用和性能指标（无）。
- 函数按 UTF-8 解码文件，忽略文件开头的一个字节顺序标记（U+FEFF）（Q5）。
- 每个 `str.isspace()` 为真的字符都分隔串（Q1）。换行符是空白。

修改的部分：

| 字段 | F01 设计 1.0 | F03 之后 |
| --- | --- | --- |
| 功能 | 一个词是一串连续的、`str.isspace()` 为假的字符，至少一个字符。 | 一个词是一串连续的、`str.isspace()` 为假的字符，至少一个字符，并且串中至少有一个使 `str.isalnum()` 为真的字符。 |
| 返回值 | 连续非空白字符串的个数。出现在第一个字符以外位置的 U+FEFF 算作词的一部分。 | 按新的“功能”定义算作词的串的个数。不含任何使 `str.isalnum()` 为真的字符的串，例如 `--`、`...`、`_`、`😀` 或单独的 U+FEFF，不是词，不计数。出现在第一个字符以外位置的 U+FEFF 仍然不是空白：它仍属于所在的串，该串只有含字母或数字时才是词。空文件、只含空白的文件、只含不带字母或数字的串的文件都返回 0。 |

含字母或数字的串只算一个词，不论它还含什么字符。所以 `don't`、`x--y` 和 `3.14` 各算一个词。

`src/troy_mode_trial/counting.py` 中 `count_words` 的文档注释在 F03 的实现 PR 中改为新的词定义。

对 F01 测试的影响：F01-T09 和 F01-T11 按旧的词定义给出预期结果，随 F03 修改。F01 的其他用例和 B13 的复现测试预期结果不变。

| 用例 | 输入 | F01 的预期 | F03 的预期 | 原因 |
| --- | --- | --- | --- | --- |
| F01-T09 | `café naïve 日本語 😀 Ελληνικά` | `5` | `4` | `😀` 不含字母或数字。 |
| F01-T11 | `a <U+FEFF> b`、`a<U+FEFF>b`，以及开头有两个 U+FEFF 的文件 | `3`、`1`、`1` | `2`、`1`、`0` | 单独的 U+FEFF 不是词。第三个文件中，第一个标记被忽略，第二个是不含字母或数字的串。 |

示例：

`dashes.txt` 是 UTF-8 文件，含一行 `Wait -- what ... don't x--y 3.14 _`。`only-symbols.txt` 只含 `-- ... !!!`。

```python
>>> from troy_mode_trial import count_words
>>> count_words("dashes.txt")
5
>>> count_words("only-symbols.txt")
0
```

## 4. 架构师审查

| 项目 | 结果 | 备注 |
| --- | --- | --- |
| 符合模块划分和数据模型 | 通过 | 修改只在模块 counting 的 `count_words` 内部。该模块拥有 `src/troy_mode_trial/**`，负责统计文本的词数。调用方仍通过 `src/troy_mode_trial/__init__.py` 使用它。架构没有定义数据模型，函数仍然接收路径、返回 `int`。 |
| 遵守错误处理和命名约定 | 通过 | 签名、参数名和错误都与 F01 设计 2.1 节相同，所以设计仍遵守 Q4：不定义自己的异常。架构 1.0 没有其他错误处理或命名规则。 |
| 不和已有接口重复 | 通过 | F03 不新增接口。它修改已有的 `count_words`，没有在旁边再加一个统计函数。 |
| 只依赖排序在前面的功能 | 通过 | F03 只依赖 F01。F01 在顺序（F01、F03、F02）中排在前面，并已在 main 上通过测试。 |
| 不在模块之间增加隐性耦合 | 通过 | 项目只有一个模块。新规则只用到标准库的 `str.isspace()` 和 `str.isalnum()`，不增加共享状态或全局状态。 |
| 修改已实现的接口时走了变更流程 | 通过 | Troy 在已合并的 [docs] PR #16 中批准了修改后的需求（2.0）。第 3 节列出了 F01 设计 2.1 节中修改的字段，保留签名和错误，并列出预期结果改变的两个 F01 用例 F01-T09 和 F01-T11。我按新的词定义核对了 F01 的其他用例和 B13 的测试：它们的结果不变。 |

| 轮次 | 问题 | 解决方式 |
| --- | --- | --- |
| 1 | 没有阻塞问题。两条不阻塞的提示。给测试经理：单独的 U+FEFF 不再计数后，测试名 `test_f01_t11_inner_bom_is_word_part` 不再描述该用例。给开发者：`count_words` 保持在 50 行以内（R04），例如用一个私有辅助函数判断一个串是否含字母或数字。 | 第 1 轮通过。 |

## 5. 修改记录

| 版本 | 日期 | 修改 |
| --- | --- | --- |
| 0.1 | 2026-11-07 | 初稿。 |
