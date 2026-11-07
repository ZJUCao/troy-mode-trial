---
troy-doc: "F01-design"
lang: "zh-CN"
version: "1.0"
updated: "2026-11-07"
status: "Troy 已于 2026-11-07 批准"
mirror-of: "design.md"
---

# F01 统计词数：接口设计

## 1. 功能

- 编号和名称：F01 统计词数：统计一个 UTF-8 文本文件里的词数。一个词是一串连续的非空白字符。
- 需求：[docs/requirements.zh-CN.md](../../requirements.zh-CN.md#4-功能点)
- 硬依赖：无
- 软依赖：无

## 2. 接口

### 2.1 `count_words`

- 模块：counting。调用方从包 `troy_mode_trial` 导入它，这个包由 `src/troy_mode_trial/__init__.py` 定义。
- 功能：读取一个 UTF-8 文本文件，返回其中的词数。一个词是一串连续的、`str.isspace()` 为假的字符，至少一个字符。

签名：

```python
def count_words(path: str | os.PathLike[str]) -> int:
```

参数：

| 名称 | 类型 | 含义 | 约束 |
| --- | --- | --- | --- |
| `path` | `str \| os.PathLike[str]` | 要统计的文件路径，可以是绝对路径，也可以是相对于当前工作目录的路径。 | 指向一个存在、可读的普通文件，内容是合法的 UTF-8。不接受 `bytes` 路径。 |

- 返回值：`int`，文件里的词数，大于或等于 0。函数按 UTF-8 解码文件，忽略文件开头的一个字节顺序标记（U+FEFF）（Q5）。每个 `str.isspace()` 为真的字符都分隔词，包括 U+3000 等 Unicode 空白（Q1）。换行符是空白，所以 `\n`、`\r\n` 和 `\r` 得到相同的计数。空文件或只含空白的文件返回 0（Q3）。出现在第一个字符以外位置的 U+FEFF 不是空白，算作词的一部分。

错误：

函数不定义自己的异常（Q4），而是让 Python 自带的异常传给调用方。

| 错误 | 何时发生 |
| --- | --- |
| `FileNotFoundError` | `path` 处没有文件。 |
| `IsADirectoryError` 或 `PermissionError` | `path` 指向一个文件夹。Linux 抛出 `IsADirectoryError`，Windows 抛出 `PermissionError`。 |
| `PermissionError` | 进程无权读取该文件。 |
| `UnicodeDecodeError` | 文件内容不是合法的 UTF-8。 |
| `TypeError` | `path` 既不是 `str` 也不是 `os.PathLike[str]`。 |

- 副作用：函数以只读方式打开文件，并在返回或抛出异常之前关闭它。函数不写入、不发送、也不保存任何数据。
- 性能指标：无

示例：

`notes.txt` 是 UTF-8 文件，含两行：`Hello world` 和 `  troy-mode  trial`，第二行末尾没有换行符。`empty.txt` 是空文件。

```python
>>> from troy_mode_trial import count_words
>>> count_words("notes.txt")
4
>>> count_words("empty.txt")
0
>>> count_words("missing.txt")
Traceback (most recent call last):
  ...
FileNotFoundError: [Errno 2] No such file or directory: 'missing.txt'
```

## 3. 对已有接口的修改

无

## 4. 架构师审查

| 项目 | 结果 | 备注 |
| --- | --- | --- |
| 符合模块划分和数据模型 | Pass | `count_words` 属于模块 counting，该模块拥有 `src/troy_mode_trial/**`。调用方通过包 `troy_mode_trial` 使用它，这是该模块唯一的对外接口。架构没有定义数据模型，函数也不保存数据：它接收一个路径，返回一个 `int`。 |
| 遵守错误处理和命名约定 | Pass | 架构 1.0 没有自己的错误处理或命名规则。设计遵守需求 Q4：不定义异常，让 Python 自带的异常传给调用方。函数名和参数名使用 snake_case，符合 Python 的惯例。 |
| 不和已有接口重复 | Pass | 项目还没有源代码，也没有其他设计。 |
| 只依赖排序在前面的功能 | Pass | F01 没有硬依赖或软依赖，在排序中排第一。 |
| 不在模块之间增加隐性耦合 | Pass | 函数只在一个模块里，只用标准库，不保存共享或全局状态。 |
| 修改已实现的接口时走了变更流程 | Pass | 第 3 节没有修改任何接口，目前也没有已实现的接口。 |

| 轮次 | 问题 | 解决方式 |
| --- | --- | --- |
| 1 | 没有阻塞问题。给开发者一条不阻塞的说明：`open()` 接受 `bytes` 路径和整数文件描述符，所以设计中 `path` 为其他类型时抛出的 `TypeError` 需要显式的类型检查。 | 第 1 轮通过。 |

## 5. 修改记录

| 版本 | 日期 | 修改 |
| --- | --- | --- |
| 0.1 | 2026-11-07 | 初稿。 |
