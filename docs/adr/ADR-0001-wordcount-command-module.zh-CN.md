---
troy-doc: "ADR-0001"
lang: "zh-CN"
version: "1.0"
updated: "2026-11-14"
status: "Troy 已于 2026-11-14 批准"
mirror-of: "ADR-0001-wordcount-command-module.md"
---

# ADR-0001：`wordcount` 命令放在单独的模块 cli 里

## 1. 状态

提议中（Proposed）

## 2. 背景

需求 4.0 新增 F04：Troy 在 PowerShell 里运行的 `wordcount FILE` 命令。它打印一个 UTF-8 文本文件的词数，按 F03 的方式计数。文件不存在时，它打印 `wordcount: missing.txt: no such file`，退出码为 1（原型 `docs/prototypes/F04-word-count-command.md`）。

架构 1.0 只有一个模块 counting。它拥有 `src/troy_mode_trial/**`，负责统计一段文字的词数，唯一的对外接口是 `src/troy_mode_trial/__init__.py`。架构没有说明从命令行启动的程序：怎样安装、向标准输出和标准错误写什么、用哪些退出码、Python 异常在哪里变成提示信息。库这一侧遵循 Q4：把 Python 自己的异常交给调用方。

需要权衡的因素：

- 库在 Troy 的脚本里的用法必须完全不变。F01、F02、F03 不变。
- ruff 的 T20 规则禁止在包里使用 `print()`，库要保留这道防线。
- R07 按模块表检查导入。troy-check 把一个文件归给第一个 Owns 匹配它的模块，所以 Owns 模式重叠时，结果取决于行的顺序。
- 需求第 7 节只允许使用标准库，并要求在 Windows 11 和 Linux 上运行。

## 3. 决定

1. 新模块 **cli** 拥有 `src/troy_mode_trial/cli.py`。它只负责命令行：读取参数、调用 counting、写出结果或错误、返回退出码。它的对外接口是 `src/troy_mode_trial/cli.py`，其他模块都不导入它，唯一的调用方是控制台脚本。cli 可以依赖 counting，且只通过 `src/troy_mode_trial/__init__.py`。
2. counting 的 Owns 改为明确列出 `src/troy_mode_trial/__init__.py` 和 `src/troy_mode_trial/counting.py`，这样两个模块不重叠，R07 也不依赖行的顺序。`src/troy_mode_trial/__init__.py` 永远不导入 cli。在 `src/troy_mode_trial/` 下新增文件的设计要写明由哪个模块拥有它，架构的模块表在同一个变更流程里加上它。
3. `pyproject.toml` 增加 `[project.scripts]` 表，内容为 `wordcount = "troy_mode_trial.cli:main"`。安装工具（uv 或 pip）据此在环境的脚本文件夹里生成 `wordcount` 程序，在 Windows 上是 `wordcount.exe`。没有新依赖：现有的构建后端 hatchling 支持这个表，参数解析用标准库的 `argparse`。
4. 命令行的错误处理：cli 只捕获 counting 为文件写明的异常（`OSError` 及其子类，以及 `UnicodeDecodeError`），向标准错误写一行 `wordcount: <按原样输入的 FILE>: <原因>`，并返回 1。命令行写错时，例如没有文件或给了两个文件，按 `argparse` 的做法在标准错误写一行用法说明，退出码为 2。其他异常都是缺陷，不捕获。成功时，cli 返回 0。标准输出只有词数和一个换行。原因文字和 `main` 的确切签名由 F04 的设计确定。
5. cli 用 `sys.stdout.write` 和 `sys.stderr.write` 输出，不用 `print()`，这样 ruff 的 T20 规则对整个包保持开启，不需要按文件豁免。

## 4. 考虑过的方案

| 方案 | 优点 | 缺点 |
| --- | --- | --- |
| 新模块 cli，counting 的 Owns 缩小到它的两个文件（采用） | counting 仍是没有输出、没有退出码的库。R07 阻止 cli 访问 counting 的内部，也阻止 counting 导入 cli。命令的规则集中在一处。 | 架构要改。counting 的 Owns 逐个列出文件，包里新增文件时要更新模块表。 |
| 把命令放在模块 counting 里，即 `src/troy_mode_trial/cli.py`，只增加 `[project.scripts]` | 模块表不变：counting 已经拥有 `src/troy_mode_trial/**`。 | counting 的职责变成计数加运行程序。R07 无法阻止库导入命令行代码。架构仍需要输出和退出码的规则，所以还是要改。 |
| 新模块 cli，counting 保留 `src/troy_mode_trial/**`，cli 的行放在前面 | counting 的 Owns 仍是一个模式。 | 只有 cli 的行一直在 counting 上面时才正确，因为 troy-check 把文件归给第一个匹配的行。表的顺序一旦调换，`cli.py` 会悄悄归到 counting。 |
| 用 PowerShell 脚本或函数 `wordcount.ps1` 调用 `python -c` | 不改 `pyproject.toml`。 | 只能在 PowerShell 里用，多了一种语言，要自己找到正确的 Python，troy-mode 的检查也覆盖不到它。 |

## 5. 后果

- F04 合并后，Troy 要把项目重新安装到 `troy-mode-trial` 环境里一次（`uv pip install -e . --no-deps`），安装工具才会生成 `wordcount`。只有在这个环境激活时，或者它的脚本文件夹在 `PATH` 上时，PowerShell 才找得到这个命令。
- `pyproject.toml` 在 F04 的实现 PR 里修改。CI 会标记依赖文件的每次修改（R16）；这次修改不增加依赖。
- 模块表必须列出 `src/troy_mode_trial/` 下的每个新文件。架构师在每次设计评审时检查这一点。
- F04 的测试可以在进程内用参数列表调用 `main`，检查标准输出、标准错误和返回的退出码。运行已安装的 `wordcount` 程序的测试需要可编辑安装，CI 已经这样安装。
- counting 不变。F02 的 `count_lines` 仍在 counting 里。

## 6. 相关

- 功能：F04、F03、F02
- 规则：R07、R16
- 架构：1.1 版的技术栈、模块表、依赖规则、错误处理、命名和编码规范、决策记录
