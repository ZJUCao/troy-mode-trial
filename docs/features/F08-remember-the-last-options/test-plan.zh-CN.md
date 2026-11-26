---
troy-doc: "F08-test-plan"
lang: "zh-CN"
version: "0.1"
updated: "2026-11-26"
status: "草稿，正在与接口设计师对齐。"
mirror-of: "test-plan.md"
---

# F08 记住上次的选项：测试方案

## 1. 功能

- 编号和名称：F08 记住上次的选项
- 设计：[design.zh-CN.md](design.zh-CN.md)

## 2. 用例

F08 新增设置文件和 settings 的外部接口，并改动 `main` 和 `wordcount`。用例按各自调用方的方式调用每个接口。

- **settings。** F08-T01 到 F08-T25 按设计第 2 节所说，以 `from troy_mode_trial.settings import ...` 导入 `OPTION_NAMES`、`settings_path`、`settings_name`、`load_option` 和 `save_option`。它们传给 `load_option` 和 `save_option` 的是测试 `tmp_path` 中的 `pathlib.Path`。
- **`main`。** F08-T26 到 F08-T43 在测试自己的进程里调用它：`from troy_mode_trial.cli import main`。它们用 pytest 的 `capsys` 读取标准输出和标准错误，并用 `monkeypatch.chdir` 把测试的 `tmp_path` 设为工作目录，用例另有说明的除外。通过 `capsys`，换行符在两个系统上都是 `\n`。
- **`wordcount`。** F08-T44 到 F08-T48 按 F07 方案的方式以新进程启动已安装的程序：不经过 shell，工作目录设为 `tmp_path`，以字节形式捕获标准输出和标准错误，用 `shutil.which("wordcount", path=sysconfig.get_path("scripts"))` 查找程序。程序不在那里时测试失败，绝不跳过。进程继承测试的环境，因此使用下面的数据文件夹。这些用例中的 `<NL>` 是字节形式的 `os.linesep`。F08 的代码合入后必须重新安装程序（设计第 3.1 节第 6 项）。F08 之前的安装会使这些用例失败，它们绝不跳过。

**数据文件夹。** 没有测试读写 Troy 真实的数据文件夹（架构第 10 节，设计第 3.3 节第 4 项）。本 PR 加入两个自动夹具，一个在 `tests/conftest.py`，一个在 `version-tests/conftest.py`。每个测试运行时，它们各用 `tmp_path_factory` 新建一个空文件夹，因此该文件夹从不位于测试的 `tmp_path` 之内，并用 `monkeypatch.setenv` 把 `APPDATA` 和 `XDG_DATA_HOME` 都设为它的绝对路径。本方案把这个文件夹称为数据文件夹。测试可以向夹具索取它。“设置文件”是 `<数据文件夹>/wordcount/settings.json`，`<S>` 是该路径的 `str()`，由测试用 `pathlib.Path` 构造，因此在 Windows 上使用 `\`。F04 到 F07 中检查一次运行不写文件的测试只扫描 `tmp_path`，所以它们不加修改仍能通过（第 4 节）。改动 `APPDATA`、`XDG_DATA_HOME` 或 `HOME` 的用例都通过 `monkeypatch` 改动；在 Linux 上取消 `XDG_DATA_HOME` 的用例同时把 `HOME` 设为自己的文件夹，使主文件夹的回退路径绝不落到真实的主文件夹。

**文件。** 每个测试自建文件，并以二进制方式写入用例给出的确切字节。`EF BB BF` 表示字节顺序标记的字节，其他两位十六进制数组表示单个字节。用例未另作说明时，`tmp_path` 中有这些文件：

- `notes.txt` 内容为 `Hello world\n  troy-mode  trial\n`，即原型中的文件：4 个词、2 行、31 个字符，最长的词 9。
- `greeting.txt` 内容为 `你好 世界!\r\n`，即原型中的文件：2 个词、1 行，最长的词 3。
- `latin1.txt` 内容为 Latin-1 编码的 `café au lait\n`。
- `sub` 是一个空文件夹。

**保存的字节。** 这是设计第 2.1 节的四种内容，每种末尾各有一个 `\n`，没有字节顺序标记：null 字节 `{"option": null}\n`、lines 字节 `{"option": "lines"}\n`、chars 字节 `{"option": "chars"}\n` 和 longest 字节 `{"option": "longest"}\n`。“内容为 lines 字节”指文件的全部内容恰好是这些字节。对文件而言，“不变”指字节相同、以纳秒计的修改时间也相同。对文件夹而言，“只含 `X`”指 `X` 是其中唯一的条目，因此没有留下 `settings.*.tmp` 文件。

**用法行。** “F08 用法行”恰好是 `usage: wordcount [--lines | --chars | --longest | --again] FILE`，即设计第 3.1 节的方案 1，Troy 已随设计批准。“用法错误”指：`main` 抛出 `code` 为 `2` 的 `SystemExit`，或程序以退出码 2 退出，且标准输出为空，标准错误恰好有两行，第一行恰好是 F08 用法行，第二行以 `wordcount: error: ` 开头。

“恰好是”指完整的文字，与 F04 方案相同。测试套件在 Windows 11 和 Linux 上运行。用例未指明系统时，在两个系统上预期相同的结果。只针对一个系统的用例在另一个系统上跳过。去掉某项权限的 Linux 用例在进程以 root 运行时跳过，因为 root 本来就有全部权限；测试结束后恢复权限。

**F05 和 F07 的用法行用例。** F05-T13、F05-T14、F05-T15 和 F05-T23 逐字检查用法错误的第一行，预期 F07 的那一行 `usage: wordcount [--lines | --chars | --longest] FILE`，F07-T30、F07-T31、F07-T32 和 F07-T36 也是如此。F08 改变这一行（设计第 3.3 节第 1、2 项）。F05 和 F07 已验收，所以这八个用例在每个 F08 PR 中都必须通过，无论 F08 的代码合入前后（R10），而实现 PR 不得修改测试（R08）。因此本 PR 把 F05 的方案改为 0.3 版，把 F07 的方案改为 1.1 版。两者预期的用法行都增加一种状态：被测分支上有 F08 的代码时为 F08 用法行，没有时为 F07 的那一行。每个用例通过它所测的接口、用一次丢弃输出的探测来确定状态：

- F08 的代码合入后，`main(["--again", "notes.txt"])` 不抛异常地返回 `0` 或 `2`。尚未合入时，它抛出 `code` 为 `2` 的 `SystemExit`，且标准错误的第二行恰好是 `wordcount: error: unrecognized arguments: --again`。
- F08 的代码合入后，`wordcount --again notes.txt` 以退出码 0 退出，或以退出码 2 退出且标准错误恰好是一行、以 `wordcount: no saved options to run again: ` 开头。尚未合入时，它以退出码 2 退出，且标准错误的第二行恰好是 `wordcount: error: unrecognized arguments: --again`。

探测得到任何其他结果时用例失败，所以没有用例同时接受两种用法行。`--again` 不改变它们的任何第二行。这八个用例保留原名，其他内容不变。F04 到 F07 没有用例被废止：F06-T28 和 F06-T34 用一个 F08 用法行也能匹配的模式检查这一行，F04 和 F06 的其他用法错误，以及 `version-tests/test_v0_2_scenarios.py` 中的 v0.2-S16，只检查这一行的开头（设计第 3.3 节第 3 项）。`version-tests/test_v0_2_scenarios.py` 的测试保持原样，它对 `wordcount` 的运行使用 `version-tests/conftest.py` 中新夹具的数据文件夹。

**在模拟实现上。** 这里假定模拟实现 PR 加入 `src/troy_mode_trial/settings.py`，其中 `OPTION_NAMES` 与设计第 2.2 节一致，四个函数的函数体都抛出 `NotImplementedError`，并让 `main` 及其用法行与 `main` 分支上的完全一样。这样，每个 settings 用例得到 `NotImplementedError`，而不是其结果或其异常。F08-T01 把 `OPTION_NAMES` 与 `save_option` 和 `load_option` 一起检查，所以它也会失败。每个带 `--again` 的 `main` 和 `wordcount` 用例得到一个 `--again` 无法识别的用法错误，或得到 F07 用法行而不是 F08 用法行。每个不带 `--again` 的用例都检查保存的文件、一条警告或之后的一次 `--again` 运行，而模拟实现给不出这些（R09）。F05 和 F07 的八个用例在模拟实现上能通过，因为它们的探测发现 F08 的代码尚未合入。如果模拟实现的 `main` 已经接受 `--again`，探测会得到 `NotImplementedError`，这些用例就会失败，而 R10 不允许这样，所以测试工程师要在测试 PR 之前报告。

| 编号 | 层级 | 接口 | 测什么 | 准备和输入 | 预期结果 |
| --- | --- | --- | --- | --- | --- |
| F08-T01 | 单元 | `OPTION_NAMES`、`save_option`、`load_option` | 保存的名称恰好是三个计数选项，且每个可保存的值读回时与保存时相同。 | `path` 为 `tmp_path / "wordcount" / "settings.json"`。对 `None` 以及 `OPTION_NAMES` 的每一项依次调用 `save_option(path, 值)`，再调用 `load_option(path)`。 | `OPTION_NAMES` 恰好是元组 `("lines", "chars", "longest")`，类型为 `tuple`。每次 `load_option` 都返回刚保存的值：`None`、`"lines"`、`"chars"` 和 `"longest"`。 |
| F08-T02 | 单元 | `save_option` | 文件内容是设计第 2.1 节的确切字节，在每个系统上都用 `\n`，没有字节顺序标记，也不留下临时文件。 | `tmp_path / "wordcount"` 是一个已存在的空文件夹。对其中的 `settings.json` 依次以 `None`、`"lines"`、`"chars"` 和 `"longest"` 调用 `save_option`，每次调用后读取字节。 | 各次调用后文件内容依次为 null 字节、lines 字节、chars 字节和 longest 字节。每次调用后该文件夹只含 `settings.json`。 |
| F08-T03 | 单元 | `save_option` | 函数创建文件所在的文件夹及其上方所有缺失的文件夹。 | `path` 为 `tmp_path / "a" / "b" / "wordcount" / "settings.json"`，`a` 不存在。调用 `save_option(path, "lines")`。 | 返回 `None`。文件内容为 lines 字节，`tmp_path / "a" / "b" / "wordcount"` 只含 `settings.json`。 |
| F08-T04 | 单元 | `save_option` | 函数替换已有的文件，包括内容不同的文件，并且总是写入，内容相同时也写入。 | `tmp_path` 中的 `settings.json` 内容为 `not json`。以 `"chars"` 调用 `save_option`。用 `os.utime` 把文件的修改时间设为 2001-01-01。再次以 `"chars"` 调用 `save_option`。 | 第一次调用后文件内容为 chars 字节。第二次调用后仍为 chars 字节，且修改时间晚于 2001-01-01。`tmp_path` 只含 `settings.json`。 |
| F08-T05 | 单元 | `save_option` | 不在 `OPTION_NAMES` 中的名称在触碰任何文件夹或文件之前就抛出 `ValueError`。 | 六个名称：`"--chars"`、`"Lines"`、`"sentences"`、`"again"`、`"words"` 和 `""`。先以 `path` 为 `tmp_path / "new" / "settings.json"` 调用，`new` 不存在。再以 `path` 为 `tmp_path / "settings.json"` 调用，其内容为 lines 字节。 | 每次调用都抛出 `ValueError`。之后 `new` 不存在，`settings.json` 不变，`tmp_path` 只含 `settings.json`。 |
| F08-T06 | 功能 | `save_option` | 应是文件夹的位置上有一个文件时抛出 `OSError`，该文件保持原样。 | `tmp_path / "wordcount"` 是内容为 `x` 的文件。调用 `save_option(tmp_path / "wordcount" / "settings.json", "lines")`。 | 抛出 `FileExistsError` 或 `NotADirectoryError`。文件 `wordcount` 不变，`tmp_path` 只含 `wordcount`。 |
| F08-T07 | 功能 | `save_option` | `path` 是文件夹时抛出 `OSError`，并删除临时文件。 | `tmp_path / "settings.json"` 是一个空文件夹。以 `"lines"` 对它调用 `save_option`。 | 抛出 `IsADirectoryError` 或 `PermissionError`，在 Linux 上抛出 `IsADirectoryError`。`settings.json` 仍是空文件夹，`tmp_path` 只含 `settings.json`。 |
| F08-T08 | 功能 | `save_option` | 替换失败时旧文件保持完整，并删除临时文件。 | `tmp_path / "wordcount" / "settings.json"` 内容为 lines 字节。Linux 上：把 `wordcount` 的权限设为 `0o500`。Windows 上：测试以读方式打开 `settings.json`，并在调用期间保持打开，如同另一个程序那样。以 `"chars"` 对它调用 `save_option`。然后恢复权限或关闭文件。 | 抛出 `PermissionError`。`settings.json` 内容仍为 lines 字节，`wordcount` 只含 `settings.json`。 |
| F08-T09 | 单元 | `load_option` | `save_option` 写出的四种内容读回为各自的值。 | 四个文件，内容分别为 null 字节、lines 字节、chars 字节和 longest 字节。 | 返回 `None`、`"lines"`、`"chars"` 和 `"longest"`。 |
| F08-T10 | 单元 | `load_option` | 接受 JSON 记号之间的空白和开头的一个字节顺序标记，如同文本编辑器保存的那样（设计第 2.1 节）。 | 五个文件：没有换行的 `{"option":"lines"}`；`  {\r\n  "option" :\t"chars"\r\n}\r\n\r\n`；`EF BB BF` 后接 `{"option": "longest"}\r\n`；`EF BB BF` 后接 `{"option": null}`；`\n{"option"  :  null  }  `。 | 返回 `"lines"`、`"chars"`、`"longest"`、`None` 和 `None`。 |
| F08-T11 | 单元 | `load_option` | 不是合法 UTF-8 的字节原样抛出 Python 自己的异常 `UnicodeDecodeError`。 | 三个文件：字节 `FF FE FD`；`{"option": "` 后接字节 `E9` 和 `"}`；以带字节顺序标记的 UTF-16 编码的 `{"option": "lines"}`。 | 每个都抛出 `UnicodeDecodeError`，它是一种 `ValueError`。 |
| F08-T12 | 单元 | `load_option` | 不是合法 JSON 的文字抛出 `json.JSONDecodeError`，第二个字节顺序标记也是如此。 | 八个文件：空文件；没有右花括号的 `{"option": "lines"`；`not json`；`{'option': 'lines'}`；`{"option": "lines",}`；`{"option": "lines"}{"option": "lines"}`；`EF BB BF EF BB BF` 后接 `{"option": "lines"}`；只有 `EF BB BF`。 | 每个都抛出 `json.JSONDecodeError`，它是一种 `ValueError`。 |
| F08-T13 | 单元 | `load_option` | 不是对象的 JSON 抛出 `ValueError`。 | 六个文件：`"lines"`；`[]`；`null`；`1`；`["option", "lines"]`；`[{"option": "lines"}]`。 | 每个都抛出 `ValueError`。 |
| F08-T14 | 单元 | `load_option` | 没有键、键不同或有第二个键的对象抛出 `ValueError`。 | 五个文件：`{}`；`{"Option": "lines"}`；`{"option ": "lines"}`；`{"option": "lines", "file": "a.txt"}`；`{"file": "a.txt", "option": "lines"}`。 | 每个都抛出 `ValueError`。 |
| F08-T15 | 单元 | `load_option` | 键 `"option"` 出现不止一次时抛出 `ValueError`，值相同时也是如此（设计第 2.1 节，架构师第 2 轮）。 | 四个文件：`{"option": "lines", "option": "chars"}`；`{"option": null, "option": null}`；`{"option": "lines", "option": "lines"}`；`{"option": "lines", "option": null}`。 | 每个都抛出 `ValueError`。 |
| F08-T16 | 单元 | `load_option` | 既不是 `null` 也不是 `OPTION_NAMES` 中名称的值抛出 `ValueError`。名称须完全一致。 | 十六个文件 `{"option": <值>}`，`<值>` 为：`"--lines"`、`"Lines"`、`"LINES"`、`" lines"`、`"lines "`、`"sentences"`、`"again"`、`"words"`、`""`、`"null"`、`true`、`false`、`1`、`[]`、`["lines"]` 和 `{}`。 | 每个都抛出 `ValueError`。 |
| F08-T17 | 功能 | `load_option` | `path` 处没有文件，或路径中缺少文件夹时，抛出 `FileNotFoundError`。 | 三个路径：空的 `tmp_path` 中的 `settings.json`；`tmp_path / "wordcount" / "settings.json"`，`wordcount` 不存在；`tmp_path / "a" / "wordcount" / "settings.json"`，`a` 不存在。 | 每个都抛出 `FileNotFoundError`。`tmp_path` 中没有创建任何东西。 |
| F08-T18 | 功能 | `load_option` | 无法打开的文件抛出其他 `OSError`，而不是 `FileNotFoundError`。 | `tmp_path / "settings.json"` 是一个空文件夹。仅在 Linux 上另加：内容为 lines 字节、权限设为 `0o000` 的 `settings.json`；以及 `tmp_path / "wordcount" / "settings.json"`，其中 `wordcount` 是内容为 `x` 的文件。 | 文件夹抛出 `IsADirectoryError` 或 `PermissionError`，在 Linux 上抛出 `IsADirectoryError`。在 Linux 上，不可读的文件抛出 `PermissionError`，经过文件的路径抛出 `NotADirectoryError`。没有一个异常是 `FileNotFoundError`。 |
| F08-T19 | 单元 | `load_option` | 函数在返回前和抛出异常前关闭文件，且不写任何东西。 | 用 `warnings.catch_warnings(record=True)` 和 `simplefilter("always", ResourceWarning)` 记录警告。`good.json` 内容为 lines 字节，`bad.json` 内容为 `not json`。记录 `tmp_path` 的条目和每个文件的状态。对 `good.json` 调用两次 `load_option`，对 `bad.json` 调用一次，后者抛出 `ValueError`。然后运行 `gc.collect()`，并把每个文件改名为 `tmp_path` 中的新名称。 | 对 `good.json` 的两次调用都返回 `"lines"`。改名之前，两个文件都不变，`tmp_path` 的条目相同。没有记录到 `ResourceWarning`，两次改名都成功。改名能在 Windows 上发现未关闭的文件，因为 Windows 不能给打开着的文件改名。 |
| F08-T20 | 单元 | `settings_path` | 在 Windows 上，路径由每次调用时读取的 `APPDATA` 构造，忽略 `XDG_DATA_HOME`。 | 仅限 Windows。把 `APPDATA` 设为 `tmp_path / "Roaming"` 的绝对路径（该文件夹不存在），把 `XDG_DATA_HOME` 设为 `tmp_path / "xdg"` 的绝对路径。调用 `settings_path()`。把 `APPDATA` 设为 `tmp_path / "Other"` 的绝对路径，再调用一次。 | 第一次返回 `pathlib.Path(tmp_path / "Roaming" / "wordcount" / "settings.json")`，一个绝对路径。第二次返回 `Other` 下的同样路径。`tmp_path` 保持为空。 |
| F08-T21 | 单元 | `settings_path` | 在 Windows 上，`APPDATA` 给不出绝对路径时抛出 `ValueError`，即使设置了 `XDG_DATA_HOME`。 | 仅限 Windows。`XDG_DATA_HOME` 为 `tmp_path` 的绝对路径。三次调用：`APPDATA` 未设置、设为空字符串、设为 `Roaming`。 | 每次都抛出 `ValueError`。 |
| F08-T22 | 单元 | `settings_path` | 在其他系统上，`XDG_DATA_HOME` 是绝对路径时路径由它构造，否则由主文件夹构造，每次调用时读取，并忽略 `APPDATA`。 | 仅限 Linux。`APPDATA` 为 `tmp_path / "appdata"` 的绝对路径，`HOME` 为 `tmp_path / "home"` 的绝对路径。五次调用：`XDG_DATA_HOME` 设为 `tmp_path / "data"` 的绝对路径；设为 `tmp_path / "data2"` 的绝对路径；未设置；为空；设为相对路径 `data`。 | 前两次返回 `tmp_path / "data" / "wordcount" / "settings.json"` 和 `tmp_path / "data2" / "wordcount" / "settings.json"`。后三次都返回 `tmp_path / "home" / ".local" / "share" / "wordcount" / "settings.json"`。`tmp_path` 保持为空。 |
| F08-T23 | 单元 | `settings_path` | 在其他系统上，没有绝对的 `XDG_DATA_HOME` 也没有可用的主文件夹时抛出 `ValueError`，Python 找不到主文件夹时也是如此。 | 仅限 Linux。三次调用：`XDG_DATA_HOME` 未设置、`HOME` 设为相对路径 `me`；`XDG_DATA_HOME` 设为 `data`、`HOME` 设为 `me`；`XDG_DATA_HOME` 未设置，并用 `monkeypatch` 把 `pathlib.Path.home` 换成抛出 `RuntimeError` 的函数，如同 Python 找不到主文件夹时那样。 | 每次都抛出 `ValueError`，绝不抛出 `RuntimeError`。 |
| F08-T24 | 单元 | `settings_name` | 在 Windows 上，能算出路径时名称就是该路径，否则是固定文字。函数从不抛出异常。 | 仅限 Windows。`APPDATA` 依次设为 `tmp_path` 的绝对路径、取消设置、设为空、设为 `Roaming`。每次都调用 `settings_name()`。 | 第一次返回 `str(tmp_path / "wordcount" / "settings.json")`。另外三次都恰好返回 `%APPDATA%\wordcount\settings.json`。 |
| F08-T25 | 单元 | `settings_name` | 在其他系统上，能算出路径时名称就是该路径，否则是固定文字。函数从不抛出异常。 | 仅限 Linux。`XDG_DATA_HOME` 设为 `tmp_path / "data"` 的绝对路径；然后取消设置，`HOME` 设为 `tmp_path / "home"` 的绝对路径；然后取消设置，`HOME` 设为 `me`；然后取消设置，并按 F08-T23 的方式让 `pathlib.Path.home` 抛出 `RuntimeError`。每次都调用 `settings_name()`。 | 依次返回 `str(tmp_path / "data" / "wordcount" / "settings.json")`、`str(tmp_path / "home" / ".local" / "share" / "wordcount" / "settings.json")`，然后两次都恰好返回 `~/.local/share/wordcount/settings.json`。 |
| F08-T26 | 功能 | `main` | 在同一进程中跑通设计的示例和 F08 原型：开始时没有保存的选项，之后每次打印计数的运行都保存其选项，失败的运行保留它，`--again` 用它计数。 | 数据文件夹为空。依次八次调用：`["--again", "notes.txt"]`、`["--lines", "notes.txt"]`、`["--again", "greeting.txt"]`、`["notes.txt"]`、`["--again", "greeting.txt"]`、`["--longest", "notes.txt"]`、`["--longest", "missing.txt"]` 和 `["--again", "greeting.txt"]`。每次调用后读取输出和设置文件。 | 各次调用依次返回 `2`、`0`、`0`、`0`、`0`、`0`、`2` 和 `0`，类型都是 `int`。标准输出依次为空、`2\n`、`1\n`、`4\n`、`2\n`、`9\n`、空和 `3\n`。标准错误在第一次恰好是 `wordcount: no saved options to run again: <S>\n`，第七次恰好是 `wordcount: missing.txt: no such file\n`，其他各次为空。第一次调用后数据文件夹仍为空。其余各次之后设置文件内容依次为 lines、lines、null、null、longest、longest 和 longest 字节，数据文件夹只含 `wordcount`，而它只含 `settings.json`。 |
| F08-T27 | 功能 | `main` | `--chars` 被保存并重复使用，选项可以放在文件之后。 | 数据文件夹为空。三次调用：`["notes.txt", "--chars"]`、`["--again", "notes.txt"]` 和 `["notes.txt", "--lines"]`。 | 每次都返回 `0`，标准错误为空。标准输出为 `31\n`、`31\n` 和 `2\n`。之后设置文件内容依次为 chars、chars 和 lines 字节。 |
| F08-T28 | 单元 | `main` | `--again` 用手写设置文件中的选项计数，包括带空白和字节顺序标记的文件，并以确切的形式保存它用过的选项。 | 五次：用一种内容写入设置文件，然后调用 `["--again", "notes.txt"]`。内容为：null 字节；lines 字节；chars 字节；longest 字节；`EF BB BF` 后接 `{ "option":"lines" }\r\n`。 | 每次都返回 `0`，标准错误为空。标准输出为 `4\n`、`2\n`、`31\n`、`9\n` 和 `2\n`。各次调用后设置文件内容依次为 null、lines、chars、longest 和 lines 字节。 |
| F08-T29 | 单元 | `main` | 带 `--again` 的运行会重新写入设置文件，内容不变时也是如此。 | 设置文件内容为 lines 字节。用 `os.utime` 把它的修改时间设为 2001-01-01。调用 `["--again", "notes.txt"]`。 | 返回 `0`，写出 `2\n`。文件内容为 lines 字节，修改时间晚于 2001-01-01。 |
| F08-T30 | 功能 | `main` | `--again` 可以放在文件之后，给两次与给一次效果相同。 | 设置文件内容为 lines 字节。三次调用：`["notes.txt", "--again"]`、`["--again", "--again", "notes.txt"]` 和 `["notes.txt", "--again", "--again"]`。 | 每次都返回 `0`，向标准输出恰好写入 `2\n`，标准错误为空。设置文件内容为 lines 字节。 |
| F08-T31 | 功能 | `main` | `--again` 与计数选项同时出现是用法错误，无论顺序，且先于缺少 `FILE` 的检查，用 argparse 自己的话说，先提到后出现的选项（需求 Q21）。它不读也不写设置文件。 | 设置文件内容为 lines 字节。七次调用：(a) `["--lines", "--again", "notes.txt"]`，(b) `["--again", "notes.txt", "--chars"]`，(c) `["--again", "--lines", "notes.txt"]`，(d) `["--chars", "--again", "notes.txt"]`，(e) `["--again", "--longest", "notes.txt"]`，(f) `["--longest", "--again", "notes.txt"]`，(g) `["--again", "--lines"]`。然后清空数据文件夹，重复 (a)。 | 每次都是用法错误，标准输出中没有数字。标准错误的第二行恰好是 `wordcount: error: ` 后接：(a) `argument --again: not allowed with argument --lines`；(b) `argument --chars: not allowed with argument --again`；(c) 和 (g) `argument --lines: not allowed with argument --again`；(d) `argument --again: not allowed with argument --chars`；(e) `argument --longest: not allowed with argument --again`；(f) `argument --again: not allowed with argument --longest`。每次之后设置文件都不变。重复 (a) 之后，数据文件夹仍为空。 |
| F08-T32 | 单元 | `main` | 带 `--again` 的其他错误命令行都是用法错误，不是计数、设置错误或帮助文字：没有文件、缩写名称、大小写不同、短形式、帮助、第二个文件和带值。无论 `sys.argv[0]` 是什么，程序名都是 `wordcount`。 | 设置文件内容为 lines 字节。`monkeypatch.setattr(sys, "argv", ["other-name.py"])`。九次调用：`[]`、`["--again"]`、`["--ag", "notes.txt"]`、`["--agai", "notes.txt"]`、`["--AGAIN", "notes.txt"]`、`["-a", "notes.txt"]`、`["--again", "-h", "notes.txt"]`、`["--again", "notes.txt", "notes.txt"]` 和 `["--again=1", "notes.txt"]`。 | 每次都是用法错误。前八次调用的标准错误第二行依次恰好是：两次 `wordcount: error: the following arguments are required: FILE`，然后是 `wordcount: error: unrecognized arguments: --ag`、`... --agai`、`... --AGAIN`、`... -a`、`... -h` 和 `... notes.txt`，其中 `...` 表示 `wordcount: error: unrecognized arguments:`。`--again=1` 的第二行只需以 `wordcount: error: ` 开头。每次之后设置文件都不变。 |
| F08-T33 | 功能 | `main` | 没有保存的选项时，`--again` 在打开 `FILE` 之前给出设置错误，因此不会出现文件错误（设计第 3.1 节第 4 项）。 | 数据文件夹为空。四次调用：`["--again", "missing.txt"]`、`["--again", "latin1.txt"]`、`["--again", "sub"]` 和 `["--again", ""]`。 | 每次都返回 `2`，标准输出为空。每次的标准错误都恰好是 `wordcount: no saved options to run again: <S>\n`。数据文件夹仍为空。 |
| F08-T34 | 功能 | `main` | 有保存的选项时，带 `--again` 的文件错误给出的行和退出码与不带 `--again` 的同一命令完全相同，并保留保存的选项。 | 调用 `["--lines", "notes.txt"]`，然后记录设置文件。然后四对调用，`--again` 在先：`["--again", "missing.txt"]` 和 `["--lines", "missing.txt"]`；`["--again", "latin1.txt"]` 和 `["--lines", "latin1.txt"]`；`["--again", "sub"]` 和 `["--lines", "sub"]`；`["missing.txt", "--again"]` 和 `["missing.txt", "--lines"]`。 | 每一对中两次调用都返回 `2`，标准输出为空，写出相同的标准错误：依次恰好是 `wordcount: missing.txt: no such file\n`、`wordcount: latin1.txt: not valid UTF-8\n`、`wordcount: sub: is a folder\n` 和 `wordcount: missing.txt: no such file\n`。每次调用后设置文件都不变。 |
| F08-T35 | 功能 | `main` | 内容不是已保存选项的设置文件给出设置错误，与设计的示例一致，且文件保持原样。 | 十二次：用一种内容写入设置文件，然后调用 `["--again", "notes.txt"]`。内容为：`not json`；空文件；`{"option": "lines"`；字节 `FF FE FD`；`[]`；`{}`；`{"option": "lines", "file": "a.txt"}`；`{"option": "lines", "option": "chars"}`；`{"option": null, "option": null}`；`{"option": "sentences"}`；`{"option": "--lines"}`；`EF BB BF EF BB BF` 后接 `{"option": "lines"}`。 | 每次都返回 `2`，标准输出为空。每次的标准错误都恰好是 `wordcount: cannot read the settings file: <S>\n`。每次调用后设置文件都不变。 |
| F08-T36 | 功能 | `main` | 无法打开的设置文件给出设置错误，且保持原样。 | 设置文件是一个空文件夹。仅在 Linux 上另加：设置文件内容为 lines 字节、权限设为 `0o000`；以及数据文件夹中有一个内容为 `x` 的文件 `wordcount`，而不是文件夹。对每种情况调用 `["--again", "notes.txt"]`。 | 每次都返回 `2`，标准输出为空。标准错误恰好是 `wordcount: cannot read the settings file: <S>\n`。文件夹 `settings.json` 仍在且为空，不可读的文件内容仍为 lines 字节，文件 `wordcount` 内容仍为 `x`。 |
| F08-T37 | 功能 | `main` | 算不出路径时，`--again` 给出设置错误，计数给出警告，两者都用文件的固定名称（设计第 2.4 节）。 | Windows 上：取消设置 `APPDATA`。Linux 上：取消设置 `XDG_DATA_HOME`，并把 `HOME` 设为相对路径 `me`。两次调用：`["--again", "notes.txt"]` 和 `["notes.txt"]`。`<N>` 在 Windows 上是 `%APPDATA%\wordcount\settings.json`，在 Linux 上是 `~/.local/share/wordcount/settings.json`。 | 第一次返回 `2`，标准输出为空，标准错误恰好是 `wordcount: cannot read the settings file: <N>\n`。第二次返回 `0`，向标准输出恰好写入 `4\n`，向标准错误恰好写入 `wordcount: warning: cannot write the settings file: <N>\n`。数据文件夹和 `tmp_path` 的条目与之前相同。 |
| F08-T38 | 功能 | `main` | 打印计数的运行会替换无法读取的设置文件。 | 设置文件内容为 `not json`。两次调用：`["--lines", "notes.txt"]` 和 `["--again", "greeting.txt"]`。 | 两次都返回 `0`，标准错误为空。标准输出先是 `2\n`，再是 `1\n`。第一次调用后设置文件内容为 lines 字节。 |
| F08-T39 | 功能 | `main` | 设置文件无法写入时，计数仍然打印并以退出码 0 结束，标准错误上随后有一行警告（需求 Q22）。 | 数据文件夹中有一个内容为 `x` 的文件 `wordcount`，而不是文件夹。三次调用：`["notes.txt"]`、`["--lines", "notes.txt"]` 和 `["--longest", "notes.txt"]`。然后删除 `wordcount`，把它建成文件夹，并让设置文件成为一个空文件夹。调用 `["--chars", "notes.txt"]`。 | 每次都返回 `0`。标准输出依次恰好是 `4\n`、`2\n`、`9\n` 和 `31\n`。每次的标准错误都恰好是 `wordcount: warning: cannot write the settings file: <S>\n`。前三次调用后，数据文件夹只含文件 `wordcount`，其内容仍为 `x`。第四次之后，文件夹 `settings.json` 仍在且为空，文件夹 `wordcount` 只含 `settings.json`。 |
| F08-T40 | 功能 | `main` | 带 `--again` 的计数之后同样给出警告，保存的选项保持完整。 | 设置文件内容为 lines 字节。Linux 上：把文件夹 `wordcount` 的权限设为 `0o500`。Windows 上：测试以读方式打开设置文件，并在调用期间保持打开。调用 `["--again", "notes.txt"]`。然后恢复权限或关闭文件。 | 返回 `0`。标准输出恰好是 `2\n`。标准错误恰好是 `wordcount: warning: cannot write the settings file: <S>\n`。设置文件内容仍为 lines 字节，文件夹 `wordcount` 只含 `settings.json`。 |
| F08-T41 | 单元 | `main` | `main` 在进程中不保留状态：选项只通过设置文件从一次调用传到下一次，且不写任何其他文件。 | 记录 `tmp_path` 中每个文件的名称和字节、工作目录以及 `sys.argv`。五次调用：`["--lines", "notes.txt"]`、`["--again", "greeting.txt"]`、`["notes.txt"]`、`["--again", "missing.txt"]` 和 `["--again", "notes.txt"]`。然后删除设置文件，调用 `["--again", "notes.txt"]`。 | 各次调用依次返回 `0`、`0`、`0`、`2`、`0` 和 `2`。每次调用的输出只有它自己的：`2\n`；`1\n`；`4\n`；标准错误上的 `wordcount: missing.txt: no such file\n`；`4\n`；标准错误上的 `wordcount: no saved options to run again: <S>\n`。删除之前设置文件内容为 null 字节，数据文件夹只含 `wordcount`。之后 `tmp_path` 中的文件和字节不变，工作目录和 `sys.argv` 也不变。 |
| F08-T42 | 单元 | `main` | 不带参数时，`main` 读取 `sys.argv[1:]`，与控制台脚本一致；`argv` 可以是任何 `str` 序列，带 `--again` 时也是如此。 | 设置文件内容为 lines 字节。`monkeypatch.setattr(sys, "argv", ["wordcount", "--again", "notes.txt"])`，然后调用 `main()` 和 `main(None)`。然后调用 `main(("--again", "notes.txt"))`，一个元组。 | 每次都返回 `0`，并向标准输出恰好写入 `2\n`。 |
| F08-T43 | 单元 | `main` | 设置错误说出文件名，数据文件夹的路径含空格和非 ASCII 字符时也是如此。 | 把 `APPDATA` 和 `XDG_DATA_HOME` 设为新建空文件夹 `tmp_path / "my data 数据"` 的绝对路径。依次调用 `["--again", "notes.txt"]`、`["--lines", "notes.txt"]` 和 `["--again", "greeting.txt"]`。 | 第一次返回 `2`，恰好写出 `wordcount: no saved options to run again: <P>\n`，其中 `<P>` 是 `str(tmp_path / "my data 数据" / "wordcount" / "settings.json")`。后两次返回 `0`，写出 `2\n` 和 `1\n`，文件 `<P>` 内容为 lines 字节。 |
| F08-T44 | 集成 | `wordcount` | 已安装的程序从头到尾跑通 F08 原型和设计的示例。 | 数据文件夹为空。依次八次运行：`wordcount --again notes.txt`、`wordcount --lines notes.txt`、`wordcount --again greeting.txt`、`wordcount notes.txt`、`wordcount --again greeting.txt`、`wordcount --longest notes.txt`、`wordcount --longest missing.txt` 和 `wordcount --again greeting.txt`。每次运行后读取设置文件。 | 退出码依次为 `2`、`0`、`0`、`0`、`0`、`0`、`2` 和 `0`。标准输出依次为空、`2<NL>`、`1<NL>`、`4<NL>`、`2<NL>`、`9<NL>`、空和 `3<NL>`。标准错误在第一次恰好是 `wordcount: no saved options to run again: <S><NL>`，第七次恰好是 `wordcount: missing.txt: no such file<NL>`，其他各次为空。第一次运行后数据文件夹仍为空。其余各次之后设置文件内容依次为 lines、lines、null、null、longest、longest 和 longest 字节，用 `\n` 而不是 `<NL>`。 |
| F08-T45 | 集成 | `wordcount` | 已安装的程序把设置保存在本系统的数据文件夹中，并忽略另一个系统的变量。 | `tmp_path` 之外的第二个新建空文件夹 `other`。Windows 上：运行时把 `XDG_DATA_HOME` 设为 `other`。Linux 上：运行时把 `APPDATA` 设为 `other`，然后再运行一次，这次取消设置 `XDG_DATA_HOME`，并把 `HOME` 设为空文件夹 `tmp_path / "home"` 的绝对路径。每次运行都是 `wordcount --chars notes.txt`。 | 每次运行都以退出码 0 退出，写出 `31<NL>`，标准错误为空。设置文件内容为 chars 字节，`other` 保持为空。在 Linux 上，最后一次运行创建 `tmp_path / "home" / ".local" / "share" / "wordcount" / "settings.json"`，其内容为 chars 字节。 |
| F08-T46 | 集成 | `wordcount` | 已安装的程序以退出码 2 给出 `--again` 的设置错误和用法错误，设置文件保持原样。 | 设置文件内容为 `not json`。四次运行：`wordcount --again notes.txt`、`wordcount --lines --again notes.txt`、`wordcount --again notes.txt --chars` 和 `wordcount --ag notes.txt`。 | 每次都以退出码 2 退出，标准输出为空。第一次的标准错误恰好是 `wordcount: cannot read the settings file: <S><NL>`。其余三次恰好是两行，每行后接 `<NL>`：F08 用法行，然后依次是 `wordcount: error: argument --again: not allowed with argument --lines`、`wordcount: error: argument --chars: not allowed with argument --again` 和 `wordcount: error: unrecognized arguments: --ag`。每次运行后设置文件都不变。 |
| F08-T47 | 集成 | `wordcount` | 设置文件无法写入时，已安装的程序打印计数和警告，退出码为 0。 | 数据文件夹中有一个内容为 `x` 的文件 `wordcount`，而不是文件夹。运行 `wordcount notes.txt`。 | 退出码 0。标准输出恰好是 `4<NL>`。标准错误恰好是 `wordcount: warning: cannot write the settings file: <S><NL>`。文件 `wordcount` 内容仍为 `x`。 |
| F08-T48 | 集成 | `wordcount` | 带 `--again` 时，参数按 Troy 输入的样子到达程序。 | 设置文件内容为 lines 字节。`notes.txt` 的副本 `my notes.txt`、`日本語.txt` 和 `-notes.txt`。四次运行：在工作目录 `sub` 中运行 `wordcount --again <notes.txt 的绝对路径>`；`wordcount --again "my notes.txt"`，一个含空格的参数；`wordcount --again 日本語.txt`；`wordcount --again -- -notes.txt`。 | 每次都以退出码 0 退出，向标准输出恰好写入 `2<NL>`，标准错误为空。设置文件内容为 lines 字节。 |

## 3. 性能用例

无。设计第 2、3 节没有设定性能指标，需求 7.1 也没有为项目设定（R14）。

## 4. 不测试的内容

| 内容 | 原因 |
| --- | --- |
| `wordcount FILE`、`--lines`、`--chars` 和 `--longest` 的全部行为：它们的数字、文件错误和用法错误。 | F04 到 F07 的用例检查它们，并且在每个 PR 中都必须通过（R10）。为它们新加的 F08 用例会在模拟实现上通过，而 R09 禁止这样。F08-T26、F08-T27、F08-T34 和 F08-T39 仍在保存的选项旁检查它们的输出。 |
| F04 到 F07 的运行不在工作文件夹中写文件。 | F04-T16、F05-T18、F06-T20 和 F07-T23 检查这一点，并且不加修改仍能通过，因为数据文件夹在 `tmp_path` 之外。它们说的“不写任何文件”现在指不在那里写文件：自 F08 起，打印计数的运行还会写设置文件（设计第 3.1 节第 6 项），由 F08-T26 和 F08-T41 检查。 |
| 计数和保存的先后：`main` 在写设置文件之前刷新标准输出。 | 调用方把标准输出和标准错误当作两条流读取，看不到它们之间的先后，也看不到刷新的时刻。F08-T39 和 F08-T40 检查写入失败时计数完整地打印出来。 |
| 因断电或进程被终止而中断的写入、磁盘已满，以及无法删除的临时文件。 | 没有外部接口能可移植地引发这些情况。F08-T07 和 F08-T08 检查写入失败后旧文件保持完整，且没有临时文件。 |
| 在 Windows 上，应是文件夹 `wordcount` 的位置上有一个文件时的 `load_option` 和 `--again`。 | Windows 上的 Python 对经过文件的路径抛出 `FileNotFoundError`，而不是设计第 2.5 节举例的 `NotADirectoryError`，所以按设计第 3.2 节第 4 项的规则，`--again` 此时给出没有保存选项的那一行。两行都说出设置文件，退出码都是 2。F08-T18 和 F08-T36 在 Linux 上检查这条路径，F08-T39 和 F08-T47 在两个系统上检查写入。 |
| Windows 上不可读的设置文件的 `PermissionError`，以及只读文件夹。 | 在 Windows 上去掉权限需要访问控制列表，可移植的测试无法可靠地设置和恢复。F08-T18 和 F08-T36 在 Linux 上检查读取。F08-T08 和 F08-T40 在 Windows 上用一个保持打开的文件检查替换失败。 |
| `settings_path` 和 `settings_name` 的 Windows 各行在 Linux 上的情况，以及其他各行在 Windows 上的情况。 | 每个系统构造自己那一类路径，所以 F08-T20 到 F08-T25 在它们指明的系统上运行。CI 在 Linux 上运行。Windows 用例在 Troy 电脑上的测试套件中运行，v0.3 版本测试在那里检查路径。 |
| `settings_path` 和 `save_option` 抛出的 `ValueError` 的文字。 | 设计只规定异常类型，并说明调用方不读取消息。 |
| `save_option` 的 `ValueError` 作为缺陷以退出码 1 到达 `main` 的调用方。 | `main` 只把解析出的选项或 `load_option` 返回的名称传给 `save_option`（设计第 3.2 节第 4 项），所以没有经过外部接口的输入能到达那里。F08-T05 检查 `save_option` 本身的 `ValueError`。 |
| 缺陷：任何其他异常到达调用方，Python 写出回溯，程序以退出码 1 退出。 | 与 F04 方案相同：没有经过外部接口的输入能引发它。 |
| `path` 不是 `pathlib.Path` 的 `load_option`，以及 `option` 不是 `str` 或 `None` 的 `save_option`。 | 设计的参数类型只允许这些，其他类型在约定之外。 |
| argparse 对 `--again=值` 以及一条命令中三个选项写出的消息。 | 设计把两者交给 argparse 自己的话，只规定 `--again=值` 是用法错误。F08-T32 检查这一点。 |
| `src/troy_mode_trial/__init__.py` 既不导入也不导出 settings，只有 settings 写文件，settings 只用标准库。 | 调用方看不到模块之间如何依赖。依赖检查器保证导入关系（R07），架构第 8 节保证其余。 |
| F09 之后作为已保存名称的 `"sentences"`。 | F09 加入它（设计第 2.2 节）。在那之前，F08-T16 和 F08-T35 预期它无法读取，由 F09 的测试方案修改这些输入。 |
| 在 Windows 上 `wordcount` 写入管道时，标准错误上非 ASCII 设置路径的字节。 | 与 F04 方案相同：此时 Python 用系统代码页编码标准错误，所以字节取决于机器。F08-T43 通过 `main` 检查这样一行的文字。 |
| PowerShell 找到 `wordcount`、`$LASTEXITCODE`、对真实设置文件的 `Get-Content` 和 `Set-Content`，以及 F08 合入后需要重新安装项目。 | CI 在没有 PowerShell 的 Linux 上运行，且没有测试触碰真实的数据文件夹。v0.3 版本测试方案在 Troy 电脑的 PowerShell 中运行命令，Troy 在 v0.3-S16 中于 Windows Terminal 手动运行。Troy 手动重新安装项目，例如用 `uv pip install -e . --no-deps`（设计第 3.1 节第 6 项）。 |
| 性能。 | 没有性能指标（R14）。 |

## 5. 与接口设计师的对齐记录

无。设计已回答本方案提出的所有用例问题：第 2.1 节给出确切的字节和无法读取的文件的唯一规则，第 3.1 节给出三行文字，设计第 4 节中架构师对 argparse 的运行确认了 F08-T31 和 F08-T46 预期的用法行和 `not allowed with` 各行。设计第 4 节中架构师的说明对本方案提出两点要求。说明 c 要求 F05 和 F07 的用法行用例在每个 F08 PR 中都通过，且不同时接受两种用法行：第 2 节在 F05 方案的 0.3 版和 F07 方案的 1.1 版中，为这八个用例加入一次 `--again` 探测。第 2 轮的说明要求重复的 `"option"` 键无法读取，值相同时也是如此：由 F08-T15 和 F08-T35 检查。有一点请接口设计师留意，本方案不需要答复：在 Windows 上，经过文件的路径抛出 `FileNotFoundError`，而不是设计第 2.5 节举例的 `NotADirectoryError`（第 4 节）。

## 6. 修改记录

| 版本 | 日期 | 修改 |
| --- | --- | --- |
| 0.1 | 2026-11-26 | 初稿。 |
