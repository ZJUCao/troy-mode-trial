---
troy-doc: "F08-design"
lang: "zh-CN"
version: "1.0"
updated: "2026-11-26"
status: "Troy 已于 2026-11-26 批准"
mirror-of: "design.md"
---

# F08 记住上次的选项：接口设计

## 1. 功能

- 编号和名称：F08 Remember the last options（记住上次的选项）
- 需求：[docs/requirements.zh-CN.md](../../requirements.zh-CN.md#4-功能点)
- 硬依赖：F04
- 软依赖：无

## 2. 接口

F08 新增模块 settings，它拥有新文件 `src/troy_mode_trial/settings.py`（架构第 3 节，ADR-0003）。第 2 节只包含新接口：2.1 节是设置文件的格式，2.2 到 2.6 节是 settings 的对外接口。第 3 节列出对模块 cli 中 `wordcount` 和 `main` 的修改，它们新增选项 `--again`。

只有 cli 使用 settings。`src/troy_mode_trial/__init__.py` 不导入它，也不从它导出任何东西（架构第 4 节），所以库仍然不写任何文件。测试以 `from troy_mode_trial.settings import ...` 导入下面的名字。

可以保存的值就是一个元组 `OPTION_NAMES`（2.2 节）中的名字。F09 在这个元组中加入 `sentences`。这样 `load_option` 和 `save_option` 无需对 settings 做其他修改就能接受它，2.1 节的文件格式也不变。

本设计中有两点是提议，由 Troy 接受或修改，并在所在位置注明：新的用法行（3.1 节，提议 1），以及设置错误和警告的三条文本（3.1 节，提议 2）。

### 2.1 设置文件

- 模块：settings。只有 settings 打开这个文件：`load_option` 读取它，`save_option` 写入它（架构第 8 节）。
- 功能：保存上一次打印出计数的 `wordcount` 运行所用的选项，或者它没有选项这一事实，让 `wordcount --again FILE` 可以用这个选项计数（需求 F08，架构第 5 节）。

签名：

```json
{"option": "lines"}
```

文件是 UTF-8 JSON：一个对象，恰好有一个键 `"option"`。文件在哪里：见 2.3 节。

参数：

| 名称 | 类型 | 含义 | 约束 |
| --- | --- | --- | --- |
| `"option"` | JSON 字符串或 `null` | 上一次打印出计数的运行所用的计数选项，不带开头的 `--`。`null` 表示那次运行没有计数选项，所以统计的是词数。 | `null`，或者 `OPTION_NAMES`（2.2 节）中恰好一个名字：`"lines"`、`"chars"` 或 `"longest"`。名字是小写，必须完全一致。F09 加入 `"sentences"`。 |

- 返回值：无。这个文件是数据，不是调用。

  `save_option` 按下面的字节原样写入内容，不带字节顺序标记，在所有系统上都以 `\n` 结尾：

  | 上一次运行 | 文件的字节 |
  | --- | --- |
  | `wordcount FILE` | `{"option": null}` 后跟 `\n` |
  | `wordcount --lines FILE` | `{"option": "lines"}` 后跟 `\n` |
  | `wordcount --chars FILE` | `{"option": "chars"}` 后跟 `\n` |
  | `wordcount --longest FILE` | `{"option": "longest"}` 后跟 `\n` |

  `load_option` 也接受这些内容在 JSON 记号之间带有空白、开头带有一个字节顺序标记的形式，所以 Troy 用文本编辑器保存过的文件仍然能读。下面错误表列出的每种形式它都拒绝，这张表是无法读取的文件的唯一规则。

错误：

不是已保存选项的内容，就是无法读取的设置文件（需求 Q20，架构第 5 节）。`load_option` 对它抛出 `ValueError`（2.5 节）。

| 错误 | 何时发生 |
| --- | --- |
| 无法读取 | 字节不是合法的 UTF-8。 |
| 无法读取 | 文本不是合法的 JSON，例如空文件，或者缺少右花括号的 `{"option": "lines"`。 |
| 无法读取 | JSON 不是对象，例如 `"lines"` 或 `[]`。 |
| 无法读取 | 对象没有键、有 `"option"` 以外的键，或者有第二个键，例如 `{}`、`{"Option": "lines"}` 或 `{"option": "lines", "file": "a.txt"}`。 |
| 无法读取 | 对象中键 `"option"` 出现不止一次，值相同也算，例如 `{"option": "lines", "option": "chars"}` 或 `{"option": null, "option": null}`。Python 的 `json` 模块只会保留最后一个值，所以 `load_option` 检查文本中的每一个键，而不只是 `json` 返回的对象。 |
| 无法读取 | 值既不是 `null`，也不是 `OPTION_NAMES` 中的名字，例如 `"--lines"`、`"Lines"`、F09 之前的 `"sentences"`、`true`、`1` 或 `[]`。 |

- 副作用：无。文件中从不保存：文件名、路径、计数或文件中的文本（需求 Q18）。
- 兼容性：这个格式比程序的每个版本都长久（架构第 5 节）。认识更多名字的版本，例如有 F09 的 `sentences` 的版本，能读取 F08 写出的每个文件。F08 的程序把含 `"sentences"` 的文件当作无法读取的文件，所以这时 `wordcount --again` 给出 3.1 节的设置错误；下一次打印出计数的运行会按 F08 的格式重新写入这个文件。
- 性能指标：无

示例：

```text
PS> wordcount --longest notes.txt
9
PS> Get-Content $env:APPDATA\wordcount\settings.json
{"option": "longest"}
PS> wordcount notes.txt
4
PS> Get-Content $env:APPDATA\wordcount\settings.json
{"option": null}
```

### 2.2 `OPTION_NAMES`

- 模块：settings，位于 `src/troy_mode_trial/settings.py`。
- 功能：除 `null` 外，设置文件的 `"option"` 值可以取的名字。只有这一处列出它们，所以 F09 在这里加一个名字就扩展了可保存的值。

签名：

```python
OPTION_NAMES: Final[tuple[str, ...]] = ("lines", "chars", "longest")
```

`Final` 是 `typing.Final`。

参数：无

- 返回值：无。它是一个常量：由小写选项名组成的元组，不带开头的 `--`，顺序与命令的用法行相同。F09 在末尾加入 `"sentences"`。

错误：无

- 副作用：无
- 性能指标：无

示例：

```python
>>> from troy_mode_trial.settings import OPTION_NAMES
>>> OPTION_NAMES
('lines', 'chars', 'longest')
```

### 2.3 `settings_path`

- 模块：settings，位于 `src/troy_mode_trial/settings.py`。
- 功能：根据运行中进程的环境，算出设置文件的路径（需求 Q17，架构第 5 节）。

签名：

```python
def settings_path() -> pathlib.Path:
```

参数：无。函数每次调用时都读取 `sys.platform` 和下面的环境变量，不缓存任何东西，所以修改了它们的测试在下一次调用时就能看到变化。

- 返回值：`pathlib.Path`，设置文件的绝对路径。函数只拼出路径。它不检查文件或文件夹是否存在，也不解析链接或 `..`。

  | 系统 | 环境 | 结果 |
  | --- | --- | --- |
  | Windows（`sys.platform == "win32"`） | `APPDATA` 是绝对路径，例如 `C:\Users\me\AppData\Roaming` | `C:\Users\me\AppData\Roaming\wordcount\settings.json` |
  | 其他系统 | `XDG_DATA_HOME` 是绝对路径，例如 `/data` | `/data/wordcount/settings.json` |
  | 其他系统 | `XDG_DATA_HOME` 未设置、为空或不是绝对路径，主文件夹是 `/home/me` | `/home/me/.local/share/wordcount/settings.json` |

  在 Windows 上，函数忽略 `XDG_DATA_HOME`；在其他系统上，它忽略 `APPDATA`。主文件夹是 `pathlib.Path.home()` 的返回值。

错误：

函数不定义自己的异常（架构第 6 节）。

| 错误 | 何时发生 |
| --- | --- |
| `ValueError` | 在 Windows 上，`APPDATA` 未设置、为空或不是绝对路径。在其他系统上，`XDG_DATA_HOME` 给不出绝对路径，而且找不到主文件夹或主文件夹不是绝对路径。`pathlib.Path.home()` 找不到主文件夹时抛出 `RuntimeError`，函数改为抛出 `ValueError`，这样调用方只需捕获 `OSError` 和 `ValueError`。消息说明缺少哪个变量，但调用方不读取它。 |

- 副作用：无。它只读取环境。
- 性能指标：无

示例：

```python
>>> import os
>>> from troy_mode_trial.settings import settings_path
>>> os.environ["APPDATA"] = r"C:\Users\me\AppData\Roaming"  # on Windows
>>> settings_path()
WindowsPath('C:/Users/me/AppData/Roaming/wordcount/settings.json')
>>> del os.environ["APPDATA"]
>>> settings_path()
Traceback (most recent call last):
  ...
ValueError: APPDATA is not set to an absolute path
```

### 2.4 `settings_name`

- 模块：settings，位于 `src/troy_mode_trial/settings.py`。
- 功能：给出设置文件的名字，用于错误行或警告行；`settings_path` 算不出路径时也能给出（需求 Q20 和 Q22：这一行要说出设置文件）。

签名：

```python
def settings_name() -> str:
```

参数：无

- 返回值：`str`。`settings_path()` 返回路径时，结果是这个路径的 `str()`，例如 Windows 上的 `C:\Users\me\AppData\Roaming\wordcount\settings.json`，或 Linux 上的 `/home/me/.local/share/wordcount/settings.json`。`settings_path()` 抛出 `ValueError` 时，结果是固定文本：Windows 上是 `%APPDATA%\wordcount\settings.json`，其他系统上是 `~/.local/share/wordcount/settings.json`，所以这一行仍然告诉 Troy 说的是哪个文件。

错误：无。在任何环境下，函数都不会抛出异常。

- 副作用：无。它只读取环境。
- 性能指标：无

示例：

```python
>>> from troy_mode_trial.settings import settings_name
>>> settings_name()  # on Windows, with APPDATA set
'C:\\Users\\me\\AppData\\Roaming\\wordcount\\settings.json'
>>> settings_name()  # on Windows, with APPDATA unset
'%APPDATA%\\wordcount\\settings.json'
```

### 2.5 `load_option`

- 模块：settings，位于 `src/troy_mode_trial/settings.py`。
- 功能：为 `wordcount --again` 从设置文件读取已保存的选项。

签名：

```python
def load_option(path: pathlib.Path) -> str | None:
```

参数：

| 名称 | 类型 | 含义 | 约束 |
| --- | --- | --- | --- |
| `path` | `pathlib.Path` | 要读取的设置文件。cli 传入 `settings_path()` 的返回值。测试传入临时文件夹中的文件。 | 任意路径。函数不检查它是不是 2.3 节的路径。 |

- 返回值：`str | None`。文件保存的是 `OPTION_NAMES` 中的某个名字时，返回这个名字；文件保存的是 `null` 时，返回 `None`，表示上一次运行没有计数选项，`--again` 统计词数。函数读取整个文件，按 UTF-8 解码并去掉开头的一个字节顺序标记，再按 2.1 节检查内容。

错误：

函数不定义自己的异常。它让 `OSError` 及其子类直接传出，对不是已保存选项的内容抛出 `ValueError`（架构第 6 节）。文件不存在表示没有已保存的选项，这时函数抛出 `FileNotFoundError`，cli 把它和其他错误区分开。

| 错误 | 何时发生 |
| --- | --- |
| `FileNotFoundError` | `path` 处没有文件，或者路径中的某个文件夹不存在：还没有哪次运行打印过计数。 |
| 其他 `OSError` | 文件无法打开或读取，例如 `path` 指向文件夹时的 `IsADirectoryError` 或 `PermissionError`，进程无权读取时的 `PermissionError`，或者路径中的某个文件夹是文件时的 `NotADirectoryError`。 |
| `ValueError` | 内容不是已保存的选项，见 2.1 节的错误表。非法的 UTF-8 抛出 `UnicodeDecodeError`，损坏的 JSON 抛出 `json.JSONDecodeError`。两者都是 `ValueError` 的子类，函数让它们原样传出。 |

- 副作用：以只读方式打开文件，在返回或抛出异常之前关闭它。它不写任何东西。
- 性能指标：无

示例：

```python
>>> from troy_mode_trial.settings import load_option, settings_path
>>> load_option(settings_path())  # the file holds {"option": "lines"}
'lines'
>>> load_option(settings_path())  # the file holds {"option": null}
>>> load_option(settings_path())  # no file yet
Traceback (most recent call last):
  ...
FileNotFoundError: [Errno 2] No such file or directory: '...settings.json'
```

### 2.6 `save_option`

- 模块：settings，位于 `src/troy_mode_trial/settings.py`。
- 功能：把一次打印出计数的运行所用的选项写入设置文件，写入失败或中断时也绝不留下写了一半的文件（架构第 5 节）。

签名：

```python
def save_option(path: pathlib.Path, option: str | None) -> None:
```

参数：

| 名称 | 类型 | 含义 | 约束 |
| --- | --- | --- | --- |
| `path` | `pathlib.Path` | 要写入的设置文件。cli 传入 `settings_path()` 的返回值。 | 任意路径，其上级文件夹是文件夹，或者可以创建为文件夹。 |
| `option` | `str \| None` | 这次运行的计数选项，不带开头的 `--`；运行没有计数选项时为 `None`。 | `None`，或者 `OPTION_NAMES` 中的名字。 |

- 返回值：无。函数返回时，`path` 处的文件保存着 2.1 节中 `option` 对应的字节。

  函数按下面的顺序工作：

  1. 检查 `option`。未知的名字抛出 `ValueError`，这时还没有碰任何文件夹或文件。
  2. `path` 的上级文件夹不存在时，创建它以及它上面缺少的文件夹。在 Linux 上，这可能连 `~/.local/share` 也一起创建。
  3. 把新内容写入这个文件夹中的一个新临时文件，文件名以 `settings.` 开头、以 `.tmp` 结尾，然后关闭它。
  4. 用 `os.replace` 以临时文件替换 `path`。

  第 3 步或第 4 步失败时，函数先删除自己的临时文件，再抛出异常。旧的设置文件保持完整，或者仍然没有文件（架构第 5 节）。如果连删除也失败，文件夹中可能留下一个 `settings.*.tmp` 文件。`load_option` 从不读取它，它也没有害处。

错误：

函数不定义自己的异常。它让 `OSError` 及其子类直接传出。

| 错误 | 何时发生 |
| --- | --- |
| `ValueError` | `option` 既不是 `None`，也不是 `OPTION_NAMES` 中的名字。cli 只传入已知的名字，所以出现这个错误说明 cli 有缺陷。 |
| `OSError` | 文件夹无法创建、临时文件无法写入，或者替换失败。例如：文件夹只读，或者在 Windows 上另一个程序打开着设置文件时的 `PermissionError`；本该是文件夹的位置上有一个文件时的 `FileExistsError` 或 `NotADirectoryError`；`path` 指向文件夹时的 `IsADirectoryError` 或 `PermissionError`；或者磁盘已满。 |

- 副作用：`path` 所在的文件夹不存在时创建它，在其中创建一个临时文件，然后重命名或删除它，并替换设置文件。即使文件已经保存着相同的内容，它也照样写入，所以文件的时间反映最后一次打印出计数的运行。
- 性能指标：无

示例：

```python
>>> from troy_mode_trial.settings import load_option, save_option, settings_path
>>> save_option(settings_path(), "chars")
>>> load_option(settings_path())
'chars'
>>> save_option(settings_path(), None)
>>> settings_path().read_bytes()
b'{"option": null}\n'
>>> save_option(settings_path(), "--chars")
Traceback (most recent call last):
  ...
ValueError: not a saved option name: '--chars'
```

## 3. 对已有接口的修改

需求 8.0 把 F08 作为新功能加入，带有选项 `--again` 和 Troy 的决定 Q17 到 Q22，见已合并的 [docs] PR “[docs] Change the requirements: remember the last options and count sentences”（提交 `1c21dd6`）。架构 4.0 和 ADR-0003 新增了模块 settings，见已合并的 [docs] PR “[docs] Change the architecture for F08”（提交 `ac1a71c`）。F04、F05、F06 和 F07 都已验收。F08 按 3.1 节和 3.2 节修改它们的接口 `wordcount`（F04 设计 2.1 节，即 F07 设计 2.1 节留下的样子）和 `main`（F04 设计 2.2 节）。3.3 节列出随之修改的测试。

不变的部分：计数函数 `count_words`、`count_lines`、`count_chars` 和 `count_longest` 的签名、行为和错误都不变。`src/troy_mode_trial/__init__.py` 的导出不变，它既不导入 cli，也不导入 settings。`wordcount FILE`、`--lines`、`--chars` 和 `--longest` 打印的数、文件错误行和退出码都与以前相同。`pyproject.toml` 中的控制台脚本不变。

### 3.1 `wordcount`

1. **新选项 `--again`。** `wordcount --again FILE` 用设置文件中保存的选项（2.1 节）统计 `FILE`：`null` 统计词数，名字则对应 `--lines`、`--chars` 或 `--longest`。运行 `wordcount --lines a.txt` 之后，`wordcount --again b.txt` 打印 `b.txt` 的行数；运行 `wordcount a.txt` 之后，它打印词数（需求 F08）。

   | 名称 | 类型 | 含义 | 约束 |
   | --- | --- | --- | --- |
   | `--again` | 选项，不带值的开关 | 用上一次打印出计数的运行所保存的选项统计 `FILE`。 | 可选。只有全名 `--again`，没有短形式，也不接受 `--ag` 这样的缩写，与其他选项相同。它可以写在 `FILE` 之前或之后。写两次与写一次相同。`--again=VALUE` 是错误的命令行。它不能与 `--lines`、`--chars` 或 `--longest` 一起出现，不论顺序如何（需求 Q21）。 |

   这个命令仍然没有 `-h` 或 `--help`，除 `--lines`、`--chars`、`--longest` 和 `--again` 外没有其他选项（需求第 8 节；F09 加入 `--sentences`）。

2. **提议 1，用法行，由 Troy 接受或修改。** 用法行从 `usage: wordcount [--lines | --chars | --longest] FILE` 改为：

   ```text
   usage: wordcount [--lines | --chars | --longest | --again] FILE
   ```

   `--again` 加入这一组互斥的选项，因为一个命令最多取其中一个（需求 Q21）。这是 Troy 为 F05 和 F07 批准的形式，也正是 argparse 为这组选项写出的行，所以不需要额外的代码。`--again` 排在最后，与需求中的顺序一致。另一种做法是把 `--again` 放进单独的方括号：`usage: wordcount [--lines | --chars | --longest] [--again] FILE`，这样就看不出 `--again` 不能与其他选项一起用。

3. **新的用法错误。** `--again` 与计数选项一起出现是错误的命令行，退出码 2（需求 Q21）。argparse 先写提议 1 的用法行，再写一行 argparse 自己措辞的消息，先说后出现的选项，与两个计数选项的情况相同（F05 设计 2.1 节，已批准）。例如 `wordcount --lines --again notes.txt` 得到 `wordcount: error: argument --again: not allowed with argument --lines`，`wordcount --again notes.txt --chars` 得到 `wordcount: error: argument --chars: not allowed with argument --again`。其他用法错误的消息不变，第一行变为提议 1 的用法行。用法错误既不读也不写设置文件。

4. **带 `--again` 的运行的顺序。** 命令先读设置文件，再打开 `FILE`（架构第 6 节）。所以设置错误先出现，这样的运行不打印计数：没有已保存的选项时，`wordcount --again missing.txt` 给出设置错误，而不是 `no such file`。有已保存的选项时，文件错误给出的行和退出码，与不加 `--again` 的同一命令完全相同。

5. **提议 2，设置错误和警告的文本，由 Troy 接受或修改。** 每条文本都是标准错误上的一行，后跟一个换行符，程序名为 `wordcount`。`<settings file>` 是 `settings_name()` 的返回值（2.4 节）：完整路径，例如 `C:\Users\me\AppData\Roaming\wordcount\settings.json`；`APPDATA` 未设置时是 `%APPDATA%\wordcount\settings.json`。第一条文本就是 F08 原型中的文本。这些文本在 Windows 和 Linux 上相同。

   | 行 | 何时出现 | 退出码 |
   | --- | --- | --- |
   | `wordcount: no saved options to run again: <settings file>` | 使用 `--again`，而设置文件还不存在，因为还没有哪次运行打印过计数（需求 Q20）。`load_option` 抛出了 `FileNotFoundError`。 | 2 |
   | `wordcount: cannot read the settings file: <settings file>` | 使用 `--again`，而设置文件无法读取：内容不是已保存的选项（2.1 节）、文件无法打开，或者 `settings_path()` 算不出它的路径（需求 Q20）。 | 2 |
   | `wordcount: warning: cannot write the settings file: <settings file>` | 运行已经打印出计数，之后设置文件无法写入，或者 `settings_path()` 算不出它的路径（需求 Q22）。 | 0 |

   两种错误之后，标准输出都为空。警告之后，标准输出与成功时一样，是计数和一个换行符，标准错误只有这条警告（架构第 8 节）。文件错误、设置错误和错误的命令行都使用退出码 2，只有标准错误上的文本能区分它们（架构第 6 节）。

6. **新的副作用。** 每次打印出计数的运行，现在都在计数和换行符写到标准输出之后，把它的选项写入设置文件：`wordcount FILE` 写 `null`，那三个选项分别写 `"lines"`、`"chars"` 或 `"longest"`，`--again` 写它用过的选项，也就是已经保存的那个（需求 F08 和 Q19）。用法错误、文件错误或设置错误不写任何东西，所以设置保持原样。这取代了 F04 设计 2.1 节中命令“不写任何文件”的承诺。命令仍然只以只读方式打开 `FILE`，也不向任何地方发送数据（需求第 7 节）。为了找到设置文件，命令在 Windows 上读取环境变量 `APPDATA`，在其他系统上读取 `XDG_DATA_HOME` 和主文件夹。F08 合入后，项目要重新安装一次，例如运行 `uv pip install -e . --no-deps`，这个选项才会存在。

示例，在 Windows 上，用户文件夹是 `C:\Users\me`，`wordcount` 设置文件夹还不存在。`notes.txt` 和 `greeting.txt` 是 F08 原型中的文件：`notes.txt` 有 `Hello world` 和 `  troy-mode  trial` 两行，`greeting.txt` 有 `你好 世界!` 一行。

```text
PS> wordcount --again notes.txt
wordcount: no saved options to run again: C:\Users\me\AppData\Roaming\wordcount\settings.json
PS> $LASTEXITCODE
2
PS> wordcount --lines notes.txt
2
PS> wordcount --again greeting.txt
1
PS> wordcount notes.txt
4
PS> wordcount --again greeting.txt
2
PS> wordcount --longest notes.txt
9
PS> wordcount --longest missing.txt
wordcount: missing.txt: no such file
PS> wordcount --again greeting.txt
3
PS> wordcount --lines --again notes.txt
usage: wordcount [--lines | --chars | --longest | --again] FILE
wordcount: error: argument --again: not allowed with argument --lines
PS> $LASTEXITCODE
2
PS> Set-Content $env:APPDATA\wordcount\settings.json 'not json'
PS> wordcount --again notes.txt
wordcount: cannot read the settings file: C:\Users\me\AppData\Roaming\wordcount\settings.json
PS> $LASTEXITCODE
2
```

设置文件夹只读时，计数照样打印：

```text
PS> wordcount notes.txt
4
wordcount: warning: cannot write the settings file: C:\Users\me\AppData\Roaming\wordcount\settings.json
PS> $LASTEXITCODE
0
```

### 3.2 `main`

1. **签名。** 不变：`def main(argv: Sequence[str] | None = None) -> int:`。`argv` 现在可以包含 `--again`，规则见 3.1 节。
2. **功能。** 它现在还会为 `--again` 通过 `load_option` 读取已保存的选项，并在计数之后通过 `save_option` 保存这次运行的选项。它从 `troy_mode_trial.settings` 导入 `settings_path`、`settings_name`、`load_option` 和 `save_option`，计数函数仍然从包 `troy_mode_trial` 导入（架构第 4 节）。
3. **返回值。** 把计数和一个换行符写到标准输出之后返回 `0`，之后又写了设置警告时也是如此。把一行文件错误或 3.1 节的两条设置错误之一写到标准错误之后返回 `2`。它在保存选项之前刷新标准输出，所以计数在写设置文件之前就已经输出。
4. **错误。** 错误的命令行引发退出码为 2 的 `SystemExit`，现在也包括 `--again` 与计数选项一起出现的情况，这发生在任何 settings 调用之前。只在调用 settings 的地方，`main` 捕获 `OSError` 和 `ValueError`，与架构第 6 节的要求相同：`load_option` 的 `FileNotFoundError` 给出 3.1 节表格的第一行；`settings_path` 或 `load_option` 的其他被捕获的异常给出第二行；`settings_path` 或 `save_option` 的被捕获的异常给出警告。`main` 传给 `save_option` 的只有 `None`、取自解析出的计数选项的名字，或者 `load_option` 返回的名字，所以警告永远不会掩盖 2.6 节称为 cli 缺陷的 `ValueError`。在调用计数函数的地方，它仍然只捕获 `OSError` 和 `UnicodeDecodeError`。其他任何异常都是缺陷，会传给调用方，于是 Python 以退出码 1 退出。
5. **副作用。** 它按 3.1 节第 6 项写设置文件。它仍然不在进程中保留状态，所以测试可以多次调用它；但每次打印出计数的调用，现在都会改变下一次带 `--again` 的调用所读取的设置文件。因此每个调用 `main` 的测试都需要 3.3 节的设置文件夹。

示例，`APPDATA` 或 `XDG_DATA_HOME` 设为一个空文件夹，`notes.txt` 是 3.1 节的文件：

```python
>>> from troy_mode_trial.cli import main
>>> main(["--again", "notes.txt"])  # writes to standard error
wordcount: no saved options to run again: ...settings.json
2
>>> main(["--lines", "notes.txt"])
2
0
>>> main(["--again", "notes.txt"])
2
0
>>> main(["--again", "--chars", "notes.txt"])
usage: wordcount [--lines | --chars | --longest | --again] FILE
wordcount: error: argument --chars: not allowed with argument --again
Traceback (most recent call last):
  ...
SystemExit: 2
```

### 3.3 随 F08 修改的测试

下面这些已有测试在 F08 的测试计划中修改，它们属于测试经理。F04 到 F07 已验收，所以它们的用例在每个 F08 PR 中都必须通过，无论 F08 的代码合入之前还是之后（R10）。

1. **F05 的用法行。** `tests/test_cli_lines.py` 中的 `USAGE_ALL` 是 `usage: wordcount [--lines | --chars | --longest] FILE`，使用它的用例逐字比较第一行。`--again` 可用之后，它们期望的第一行变为提议 1 的用法行；在此之前仍是旧的用法行。它们的第二行不变。
2. **F07 的用法行。** `tests/test_cli_longest.py` 中的 `USAGE` 是同一行，按同样的方式修改。
3. **不变的用法行。** `tests/test_cli_chars.py` 中 F06 的模式接受 ` FILE` 之前任何含 `--chars` 的方括号，新的用法行仍然符合。`tests/test_cli.py` 和 `version-tests/test_v0_2_scenarios.py` 只检查这一行是否以 `usage: wordcount ` 或 `usage:` 开头。
4. **每个测试的设置文件夹。** `tests/conftest.py` 中的一个自动夹具，以及 `version-tests/conftest.py` 中的一个，为每个测试把 `APPDATA` 和 `XDG_DATA_HOME` 设为测试工作文件夹之外的一个新的空文件夹（架构第 10 节，ADR-0003）。没有它，每次成功调用 `main` 都会写 Troy 真实的设置文件；`version-tests/test_v0_2_scenarios.py` 中在子进程里运行已安装的 `wordcount` 的版本测试也是如此。这个文件夹必须在 F04 到 F07 的测试检查“运行不在其中写文件”时扫描的文件夹之外，例如 `tests/test_cli.py`、`tests/test_cli_lines.py` 和 `tests/test_cli_longest.py` 中的这类检查，这样那些用例不用修改就能继续通过。

## 4. 架构师审查

| 项目 | 结果 | 备注 |
| --- | --- | --- |
| 符合模块划分和数据模型 | 通过 | 模块划分相符。新接口都在 settings 模块里，它拥有 `src/troy_mode_trial/settings.py`（架构第 3 节，ADR-0003）。cli 直接导入 settings，`__init__.py` 既不导入它也不导出它的内容，settings 不导入任何模块（第 4 节）。路径规则、键 `"option"` 及其取值 `null` 和三个名字、在计数之后写入、以及临时文件加 `os.replace`，都与第 5 节一致。第 2 轮中，2.1 节的错误表是无法读取的文件的唯一规则，符合第 5 节“恰好一个键”的要求：键 `"option"` 重复出现的文件无法读取，值相同也算，`load_option` 检查文本中的每一个键。错误表上面那句话只接受记号之间的空白和开头的一个字节顺序标记。第二个字节顺序标记不是 JSON 空白，所以由“文本不是有效的 JSON”那一行涵盖。 |
| 遵守错误处理和命名约定 | 通过 | settings 不定义自己的异常。它让 `OSError` 传出、抛出 `ValueError`，并把 `Path.home()` 的 `RuntimeError` 换成 `ValueError`，所以 cli 只需捕获第 6 节列出的两种类型。`main` 只在调用 settings 的地方捕获它们，在调用计数的地方仍只捕获 `OSError` 和 `UnicodeDecodeError`。退出码与第 6 节一致：两个设置错误返回 2，并且在打开 `FILE` 之前读取；写入失败时返回 0，并输出一行警告。标准输出只有计数，警告写到标准错误（第 8 节）。只有 settings 写文件。命名遵循 Python 的习惯。第 1 轮我用 argparse 3.14 运行了提议的互斥组：它给出的用法行与方案 1 相同，两行 `not allowed with` 与 3.1 节写的完全一致；`--again --again` 能解析，`--again=1` 和 `--ag` 以退出码 2 结束。 |
| 不和已有接口重复 | 通过 | 现在还没有任何设置相关的接口。`settings_name` 包装了 `settings_path`，只用于 `settings_path` 覆盖不了的一种情况，即算不出路径时的错误行，它并没有用第二种方式计算路径。`main` 仍然通过已有的计数函数计数。 |
| 只依赖排序在前面的功能 | 通过 | F08 唯一的硬依赖是 F04，它在顺序中排在 F08 前面（F01、F03、F04、F07、F06、F02、F05、F08、F09），并且已验收。设计提到 F09 只是说它以后会修改 `OPTION_NAMES`，并不使用它。 |
| 不在模块之间增加隐性耦合 | 通过 | cli 只依赖 settings 写明的行为。它靠 `FileNotFoundError` 区分“没有已保存的选项”和“无法读取”，而 `load_option` 把这个异常写明为该信号。可保存的名字只在 settings 的 `OPTION_NAMES` 里列出。3.3 节的测试夹具设置的是 `settings_path` 写明的环境变量，设计也说明了它必须放在已验收测试扫描的文件夹之外。 |
| 修改已实现的接口时走了变更流程 | 通过 | 对 `wordcount` 和 `main` 的修改在需求 8.0（Q17 到 Q22）以及架构 4.0 和 ADR-0003 之后，这些都已由 Troy 批准并合并（`1c21dd6`、`ac1a71c`）。ADR-0003 的“后果”已列出 F04“不写文件”的承诺不再成立，以及新的用法行。`main` 的签名不变。3.3 节把 F05 和 F07 要改的测试和新夹具交给 F08 的测试计划，由测试经理负责。 |
| 给 Troy 的摘要和设计说的一致，并列出了需要 Troy 决定的每一件事 | 通过 | 第 2 轮中，摘要与设计一致：`--again` 及它重复的内容；设置文件、它在 Windows 和 Linux 上的文件夹（现在写明了 `$XDG_DATA_HOME`，见第 1 轮备注 b）以及它从不保存的内容；手工编辑可以加空格，其他任何无效内容都会让文件无法读取（2.1 节）；出错时不打印计数、退出码为 2；`--again` 不能和计数选项一起用；不带 `--again` 时什么都不变。它的两个决定点就是设计的两个方案，各有推荐。它的风险也是设计里的：写入失败时的警告和旧的选项，以及共用的退出码 2。设计没有其他待定的选择。英文摘要约 1,300 个字符，不超过 2,000，不含内部编号。它不再提到只有重新安装项目后 `--again` 才能用（3.1 节第 6 条）。这不是需要决定的事，所以不阻塞。见备注 d。 |

| 轮次 | 问题 | 解决方式 |
| --- | --- | --- |
| 1 | 问题 1，阻塞，属于第 1 项，在 2.1 节字节表之后的那段话和错误表。接受“Python 的 `json` 模块读成这样一个对象”的任何内容的那句话，对重复的键（例如 `{"option": "lines", "option": "chars"}`）与错误表和架构第 5 节矛盾。请只在一处写明规则。我建议这样的文件算作无法读取，因为架构第 5 节说对象恰好有一个键，错误表也已列出“有第二个键”。请把这个例子加入错误表，并把那句话改为：`load_option` 接受记号之间的空白和开头的一个字节顺序标记，拒绝错误表列出的其他所有形式。镜像也做同样的修改。备注，不阻塞。a. 给开发者：`save_option` 对未知名字抛出 `ValueError`，2.6 节说这意味着 cli 有缺陷，但 3.2 节第 4 条把它变成了警告。架构第 6 节允许这样做，但请让 cli 传给 `save_option` 的名字只来自解析出的选项，这样警告就不会掩盖缺陷。用读取和保存的辅助函数让 `main` 不超过 50 行（R04）。b. 给接口设计者：如果因问题 1 修改摘要，Linux 文件夹可以写成“设置了 `$XDG_DATA_HOME` 时为 `$XDG_DATA_HOME/wordcount`”。c. 给测试经理：F05 和 F07 中比较用法行的用例必须在 F08 的每个 PR 中都通过（R10）。请规划它们如何在 `--again` 落地的同时改变，而不是让它们接受两种用法行；并按修改后的 2.1 节给 `load_option` 的重复键测试定下结果。 | 第 1 轮要求修改。 |
| 2 | 按设计 0.2 检查第 1 轮的问题 1 和备注 a。没有新的阻塞问题。备注，不阻塞。d. 给接口设计者：给 Troy 的摘要可以再用一行说明，只有重新安装项目后 `--again` 才能用，如 3.1 节第 6 条所说。第 1 轮给测试经理的备注 c 仍然有效：`load_option` 的重复键测试应期望文件无法读取，值相同也一样。 | 问题 1 已解决：2.1 节的错误表是唯一规则，含两个重复键的例子，表上面那句话只接受记号之间的空白和一个字节顺序标记。备注 a 已在 3.2 节第 4 条解决。第 2 轮批准。 |

## 5. 修改记录

| 版本 | 日期 | 修改 |
| --- | --- | --- |
| 0.1 | 2026-11-26 | 初稿。 |
| 0.2 | 2026-11-26 | 架构师审查第 1 轮，发现 1：2.1 节在一处说明键 `"option"` 出现多次的文件无法读取，在错误表中加入这个例子，并说明除了原样的字节之外，`load_option` 只接受记号之间的空白和一个字节顺序标记。3.2 节说明 `main` 传给 `save_option` 哪些名字（备注 a）。 |
| 1.0 | 2026-11-26 | Troy 批准。 |
