---
troy-doc: "ADR-0003"
lang: "zh-CN"
version: "1.0"
updated: "2026-11-26"
status: "Troy 已于 2026-11-26 批准"
mirror-of: "ADR-0003-settings-module.md"
---

# ADR-0003：`wordcount` 命令通过新模块 settings 记住上次的选项

## 1. 状态

已接受。Troy 于 2026-11-26 批准 `docs/architecture.md`，接受了这条记录。 （Proposed）

## 2. 背景

需求 8.0 新增 F08。`wordcount --again FILE` 用上一次打印出计数的运行所用的选项来统计 FILE。每一次这样的运行都把它的选项，或它没有选项这一事实，写进一个设置文件：Windows 上是 `%APPDATA%\wordcount\settings.json`，Linux 上是 `$XDG_DATA_HOME/wordcount/settings.json` 或 `~/.local/share/wordcount/settings.json`。该文件只保存这个选项（Q18）。失败的运行不改动它（Q19）。没有已保存的选项或文件无法读取时，`--again` 报一条指出该文件的错误，退出码 2（Q20）。文件无法写入时，照常打印计数，在标准错误写一条指出该文件的警告，退出码 0（Q22）。需求第 7 节现在允许命令写这一个文件，库仍然只读文件。F09 排在 F08 之后，并让 `--again` 也记住 `--sentences`。

架构 3.0 没有覆盖这些：

- 它的数据模型是空的，程序不保存任何文件。设置文件是第一个被保存的格式，而且它比写它的每个程序版本都活得久。
- 它的第 6 节只允许 cli 捕获 counting 抛出的 `OSError` 和 `UnicodeDecodeError`，其他异常都算缺陷。内容损坏的设置文件会让 `json` 抛出 `ValueError`，而写入失败又不能改变退出码。
- 它的第 8 节说标准错误只放错误和用法行。退出码为 0 时出现警告是新情况。
- 它没有测试设置。F04 到 F07 现有测试里每一次成功调用 `main`，都会写 Troy 数据文件夹里真正的设置文件。其中几个测试还检查自己的工作文件夹没有变化。
- 需求第 7 节只允许使用标准库。

## 3. 决定

1. **新模块 settings** 拥有 `src/troy_mode_trial/settings.py`。它找到设置文件、读取已保存的选项并写入选项。它的外部接口是 `src/troy_mode_trial/settings.py`。它不依赖任何模块。cli 可以依赖 counting 和 settings。counting 从不导入 settings，`src/troy_mode_trial/__init__.py` 也不导入它、不从它导出，所以 R07 保证库不写任何文件。F08 的设计给出函数名。
2. **文件位置。** 在 Windows 上（`sys.platform == "win32"`）是 `<APPDATA>\wordcount\settings.json`。在其他系统上，`XDG_DATA_HOME` 设为绝对路径时是 `<XDG_DATA_HOME>/wordcount/settings.json`，否则是 `~/.local/share/wordcount/settings.json`。路径在每次运行时从环境变量算出，从不缓存。Windows 上没有设置 `APPDATA` 时，按第 5 点算作设置错误，而不是缺陷。
3. **数据模型。** 文件是 UTF-8 编码的 JSON：一个对象，只有一个键，值为 `null` 表示运行没有选项，否则是某个计数选项的名字。F08 的设计确定键名和取值（`lines`、`chars`、`longest`）；F09 的设计加上 `sentences`。其他任何内容，例如损坏的 JSON、别的键或未知的值，都算无法读取的文件（Q20）。文件从不保存文件名、路径、计数或文件里的文字（Q18）。
4. **何时写、怎样写。** cli 只在计数和换行已经写到标准输出之后才写入选项，所以失败的运行从不写入（Q19）。settings 在 `wordcount` 文件夹不存在时创建它，先把新内容写进同一文件夹里的临时文件，再用 `os.replace` 替换旧文件。写入失败或中断时，旧文件保持完整，或者根本没有文件，绝不会留下写了一半的文件。标准库的 `json`、`os`、`pathlib` 和 `tempfile` 已经够用，所以不增加依赖。
5. **错误处理。** settings 不定义自己的异常。它让 `OSError` 及其子类直接抛出，内容不是已保存的选项时抛出 `ValueError`（`json.JSONDecodeError` 是一种 `ValueError`）。cli 只在调用 settings 的地方捕获 `OSError` 和 `ValueError`，从不在 counting 周围捕获。为 `--again` 读取时，它写一行指出设置文件的错误，返回退出码 2。文件不存在表示没有已保存的选项。写入时，它在标准错误写一行指出设置文件的警告，返回退出码 0。F08 的设计确定这些文字。
6. **输出。** 标准输出仍然只放计数和一个换行。退出码为 0 的运行，标准错误里可以有一行警告。
7. **测试设置。** 任何测试都不读写 Troy 真正的数据文件夹。`tests/conftest.py` 和 `version-tests/conftest.py` 里各有一个自动夹具（fixture），为每个测试把 `APPDATA` 和 `XDG_DATA_HOME` 设为测试工作文件夹之外的一个新的空文件夹。运行已安装程序的子进程会继承这些变量。测试经理在 F08 的测试计划里加入这些夹具。

Troy 批准后，架构随之修改：模块表加上 settings，依赖规则加上 `cli --> settings`，第 5 到 8 节和第 10 节写入第 3 到 7 点，决策记录加上本 ADR。

## 4. 考虑过的方案

| 方案 | 优点 | 缺点 |
| --- | --- | --- |
| 新模块 settings，只有 cli 使用它（选中） | R07 保证 counting 仍是只读的库。保存的格式和它的错误集中在一处，F09 在这里扩展。cli 仍然只管命令行。 | 架构要改，模块表多一行。 |
| 把设置代码放进 `src/troy_mode_trial/cli.py` | 不需要新模块。 | cli 的文件把命令行和文件路径、JSON、安全写入混在一起，F09 又会让它变大。没有检查能管住写文件的代码放在哪里。 |
| 把设置代码放进 counting | 不需要新模块。 | 库里会有写文件的代码，违反需求第 7 节。 |
| 用第三方包 `platformdirs` 找文件夹 | 支持更多系统。 | 新依赖，违反需求第 7 节。它在 Windows 上的默认位置不是 `%APPDATA%\wordcount`。 |
| 直接覆盖写文件，不用临时文件 | 代码略少。 | 写入失败可能留下写了一半的文件，之后的 `--again` 就会失败。 |

## 5. 影响

- 程序第一次在 Troy 的电脑上保存文件。它的格式以后难改：新版本必须仍能读取旧版本写的文件，或者把它当作无法读取。
- 每次打印出计数的运行都会写一个小文件，所以 `wordcount` 每次运行多做一点事。
- F04 设计里 `main` 不写任何文件的承诺改变了。F08 的设计把这一点和新的用法行记为对现有接口的修改。
- F05 和 F07 已验收的测试中逐字比较用法行的那些，以及 F04 到 F07 中调用 `main` 的测试，都依赖 F08 的测试计划：前者需要新的用法行，所有这些都需要第 7 点的夹具。
- F09 的设计会修改 F08 的接口：它在可保存的值里加上 `sentences`。

## 6. 相关

- 功能：F08、F09、F04
- 规则：R07、R16
