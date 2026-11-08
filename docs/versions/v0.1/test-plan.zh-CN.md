---
troy-doc: "v0.1-test-plan"
lang: "zh-CN"
version: "0.2"
updated: "2026-11-08"
status: "草稿。"
mirror-of: "test-plan.md"
---

# v0.1 版本测试方案

## 1. 版本

- 版本：v0.1
- 功能：F01、F03
- 需求：[docs/requirements.zh-CN.md](../../requirements.zh-CN.md#6-版本计划)

## 2. 端到端场景

每个场景都遵循需求文档第 3 节的用户流程以及 F01 和 F03 的原型。Troy 的脚本以相对于当前工作目录的路径调用 `count_words`，所以场景也这样调用，除非场景另有说明。每个测试在临时文件夹里自建文件，并以二进制方式写入场景给出的确切字节，这样 Windows 不会把 `\n` 改成 `\r\n`。非 ASCII 字符按 UTF-8 编码，除非场景给出了别的字节。设计只承诺异常的类型，不承诺异常的消息（Q4），所以预期异常的场景只检查类型。

| 编号 | 场景 | 由谁运行 | 步骤 | 预期结果 |
| --- | --- | --- | --- | --- |
| v0.1-S01 | 统计一个文件的词数，与 F01 原型相同。 | Claude | 1. 写入 `notes.txt`，内容为 `Hello world\n  troy-mode  trial`，末尾没有换行符。2. 把 `notes.txt` 所在文件夹设为工作目录。3. 执行 `from troy_mode_trial import count_words`。4. 调用 `count_words("notes.txt")`。 | 返回 `4`，且结果的类型恰好是 `int`。 |
| v0.1-S02 | 统计一个空文件的词数，与 F01 原型相同。 | Claude | 1. 写入一个空的 `empty.txt`。2. 把它所在文件夹设为工作目录。3. 调用 `count_words("empty.txt")`。 | 返回 `0`。 |
| v0.1-S03 | 统计一个不存在的文件，与 F01 原型相同。 | Claude | 1. 把一个空文件夹设为工作目录。2. 调用 `count_words("missing.txt")`。 | 抛出 `FileNotFoundError`。 |
| v0.1-S04 | 统计一个不是合法 UTF-8 的文件，与 F01 原型相同。 | Claude | 1. 写入 `latin1.txt`，内容为 Latin-1 编码的 `café au lait`，所以其字节以 `63 61 66 E9 20` 开头。2. 把它所在文件夹设为工作目录。3. 调用 `count_words("latin1.txt")`。 | 抛出 `UnicodeDecodeError`。 |
| v0.1-S05 | 统计一个并非每串都含字母或数字的文件，与 F03 原型相同。 | Claude | 1. 写入 `dashes.txt`，内容为 `Wait -- what ... don't x--y 3.14 _`。2. 把它所在文件夹设为工作目录。3. 调用 `count_words("dashes.txt")`。 | 返回 `5`。`--`、`...` 和 `_` 这几串不算。 |
| v0.1-S06 | 统计一个只含不带字母或数字的串的文件，与 F03 原型相同。 | Claude | 1. 写入 `only-symbols.txt`，内容只有 `-- ... !!!`。2. 把它所在文件夹设为工作目录。3. 调用 `count_words("only-symbols.txt")`。 | 返回 `0`。 |
| v0.1-S07 | Troy 的一个脚本在 Troy 的电脑上、在自己的 Python 进程中统计在 Windows 和 Linux 上生成的文件，相同的词无论换行符如何都得到相同的计数。 | Claude | 1. 写入三个文件。`windows.txt` 内容为字节 `EF BB BF` 后接 `Hello world\r\n  troy-mode  trial\r\n`，与记事本保存的一样。`linux.txt` 内容为 `Hello world\n  troy-mode  trial\n`。`mixed.txt` 内容为 `Wait -- what ... don't x--y 3.14 _\r\n日本語　テキスト 😀\n`，其中 `日本語` 和 `テキスト` 之间的空白是 U+3000。2. 记录每个文件的字节。3. 从文件所在文件夹以外的文件夹启动一个新的 Python 3.13 进程。4. 在该进程中导入 `troy_mode_trial`，以 `pathlib.Path` 形式的绝对路径对每个文件各调用一次 `troy_mode_trial.count_words`，并打印三个计数。所有步骤都在 Troy 的电脑上的 Windows 11 中执行。 | 进程以退出码 0 结束，并打印 `4`、`4` 和 `7`。每个文件的字节与第 2 步记录的相同。 |

## 3. 性能和压力用例

无。需求第 7.1 节没有设任何性能指标，所以 v0.1 没有性能或压力用例（R14）。

## 4. 设备

| 设备 | 操作系统 | 由谁运行 |
| --- | --- | --- |
| Troy 的电脑 | Windows 11，conda 环境 `troy-mode-trial` 中的 Python 3.13 | Claude |

Claude 运行的场景只在 Troy 电脑上的发布测试中运行，从不在 CI 中运行，所以 GitHub Actions 运行器不是这些场景的设备。v0.1 是一个没有用户界面的库，每个场景都从脚本调用 `count_words`。所以没有场景需要只有 Troy 才有的设备。

## 5. 验收记录

无。Troy 尚未验收 v0.1。

## 6. 修改记录

| 版本 | 日期 | 修改 |
| --- | --- | --- |
| 0.1 | 2026-11-08 | 初稿。 |
| 0.2 | 2026-11-08 | v0.1-S07 只在 Troy 电脑上的 Windows 11 中运行；第 4 节不再列出 GitHub Actions 运行器，因为版本测试从不在 CI 中运行。 |
