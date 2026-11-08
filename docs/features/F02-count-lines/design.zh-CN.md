---
troy-doc: "F02-design"
lang: "zh-CN"
version: "1.0"
updated: "2026-11-08"
status: "Troy 已于 2026-11-08 批准"
mirror-of: "design.md"
---

# F02 统计行数：接口设计

## 1. 功能

- 编号和名称：F02 统计行数
- 需求：[docs/requirements.zh-CN.md](../../requirements.zh-CN.md#4-功能点)
- 硬依赖：无
- 软依赖：无

## 2. 接口

### 2.1 `count_lines`

- 模块：counting。调用方从包 `troy_mode_trial` 导入它，这个包由 `src/troy_mode_trial/__init__.py` 定义，和 `count_words` 放在一起。
- 功能：读取一个 UTF-8 文本文件，返回其中的行数。只有 `\n`、`\r\n` 和 `\r` 结束一行（Q2），最后一行即使没有换行符也计数。

签名：

```python
def count_lines(path: str | os.PathLike[str]) -> int:
```

参数：

| 名称 | 类型 | 含义 | 约束 |
| --- | --- | --- | --- |
| `path` | `str \| os.PathLike[str]` | 要统计的文件路径，可以是绝对路径，也可以是相对于当前工作目录的路径。`pathlib.Path` 属于 `os.PathLike[str]`，可以使用。 | 指向一个存在、可读的普通文件，内容是合法的 UTF-8。不接受 `bytes` 路径。 |

- 返回值：`int`，文件里的行数，大于或等于 0。函数按 UTF-8 解码文件，忽略文件开头的一个字节顺序标记（U+FEFF）（Q5）。然后统计文本中的换行符个数；如果最后一个换行符之后还有文本，或者文本不为空但没有换行符，再加 1。

  换行符的规则：

  - 换行符只有三种：`\n`、`\r\n` 和 `\r`（Q2）。紧跟 `\n` 的 `\r` 合起来是一个换行符 `\r\n`，不是两个。所以同一段文本无论用 Windows 还是 Linux 的换行符，计数都相同。
  - 其他字符都不结束一行。Python 的 `str.splitlines()` 视为换行的其他字符，在 F02 里都是普通字符：`\v`（U+000B）、`\f`（U+000C）、U+001C、U+001D、U+001E、U+0085、U+2028 和 U+2029。含有这些字符的行和其他行一样只算一行。因此函数不得用 `str.splitlines()` 计数。
  - 空文件或只含字节顺序标记的文件返回 0（Q3）。只含一个换行符的文件返回 1（Q3）。两个换行符之间的空行算一行。

  | 解码后的文本（已去掉字节顺序标记） | 结果 |
  | --- | --- |
  | （空） | `0` |
  | `\n` | `1` |
  | `Hello world\n  troy-mode  trial` | `2` |
  | `Hello world\r\n  troy-mode  trial\r\n` | `2` |
  | `first\n\nthird\n` | `3` |
  | `one\rtwo\r\nthree\nfour` | `4` |
  | `\r\r\n` | `2` |
  | `\n\r` | `2` |
  | `a b\fc\x85d` | `1` |

错误：

函数不定义自己的异常（Q4），而是让 Python 自带的异常传给调用方，和 `count_words` 相同。

| 错误 | 何时发生 |
| --- | --- |
| `FileNotFoundError` | `path` 处没有文件，或 `path` 是空字符串。 |
| `IsADirectoryError` 或 `PermissionError` | `path` 指向一个文件夹。Linux 抛出 `IsADirectoryError`，Windows 抛出 `PermissionError`。 |
| `PermissionError` | 进程无权读取该文件。 |
| `UnicodeDecodeError` | 文件内容不是合法的 UTF-8。 |
| `TypeError` | `path` 既不是 `str` 也不是 `os.PathLike[str]`，例如 `bytes` 或 `int`。 |

- 副作用：函数以只读方式打开文件，并在返回或抛出异常之前关闭它。函数不写入、不发送、也不保存任何数据。
- 性能指标：无

示例：

`notes.txt` 是 UTF-8 文件，含两行：`Hello world` 和 `  troy-mode  trial`，第二行末尾没有换行符。`windows.txt` 含同样的文本，换行符是 `\r\n`。`empty.txt` 是空文件。

```python
>>> from pathlib import Path
>>> from troy_mode_trial import count_lines
>>> count_lines("notes.txt")
2
>>> count_lines(Path("windows.txt"))
2
>>> count_lines("empty.txt")
0
>>> count_lines("missing.txt")
Traceback (most recent call last):
  ...
FileNotFoundError: [Errno 2] No such file or directory: 'missing.txt'
```

## 3. 对已有接口的修改

无。F02 新增 `count_lines`，`count_words` 保持不变。

## 4. 架构师审查

| 项目 | 结果 | 备注 |
| --- | --- | --- |
| 符合模块划分和数据模型 | 通过 | `count_lines` 属于模块 counting，该模块负责 `src/troy_mode_trial/**`；调用方通过模块的对外接口 `src/troy_mode_trial/__init__.py` 使用它，符合 R07。需求 Q6 已确定统计行数属于 counting，无需修改架构。架构没有定义数据模型；函数接收一个路径，返回一个 `int`，和 `count_words` 相同。 |
| 遵守错误处理和命名约定 | 通过 | 只抛出 Python 自带的异常，不定义自己的异常（Q4）。错误表和 `count_words` 的实现一致，包括 `bytes` 路径抛出 `TypeError`、空字符串抛出 `FileNotFoundError`。名称沿用 `count_words` 的形式：snake_case，动词 `count_` 加上所统计的对象。 |
| 不和已有接口重复 | 通过 | 已有的接口只有 `count_words`，它统计词数而不是行数。没有已有函数统计换行符。 |
| 只依赖排序在前面的功能 | 通过 | F02 没有硬依赖或软依赖，在顺序 F01、F03、F02 中排在最后。它不使用 F01 或 F03 的任何接口。 |
| 不在模块之间增加隐性耦合 | 通过 | 项目只有一个模块，设计没有新增模块、共享状态或跨模块导入。它只使用标准库（需求第 7 节）。 |
| 修改已实现的接口时走了变更流程 | 通过 | 第 3 节没有修改已实现的接口：`count_words` 的签名和行为都不变。在 `__init__.py` 中和 `count_words` 一起导出 `count_lines` 只是新增一个名称，不改变已有名称。 |

| 轮次 | 问题 | 解决方式 |
| --- | --- | --- |
| 1 | 无。六项全部通过。 | 批准，无需修改。 |

## 5. 修改记录

| 版本 | 日期 | 修改 |
| --- | --- | --- |
| 0.1 | 2026-11-08 | 初稿。 |
| 1.0 | 2026-11-08 | Troy 批准。 |
