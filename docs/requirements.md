---
troy-doc: "requirements"
lang: "en"
version: "9.0"
updated: "2026-11-26"
status: "Approved by Troy on 2026-11-26"
mirror: "requirements.zh-CN.md"
---

# troy-mode-trial requirements

## 1. Goal

troy-mode-trial is a small Python library that counts things in UTF-8 text files. Troy calls it from Troy's own scripts, and runs its `wordcount` command in PowerShell. Version 0.1 counts the words of one file. Version 0.2 adds the `wordcount` command and also counts the lines of a file. Version 0.3 adds the `--lines`, `--chars`, `--longest`, and `--sentences` options, so `wordcount` can also print the lines, the characters, or the sentences of a file, or the length of its longest word, and the `--again` option, which runs `wordcount` with the option of its last run. Version 0.4 adds a library function that counts the paragraphs of a text; `wordcount` does not change.

## 2. Users

Troy is the only user. Troy runs the scripts that call the library on Windows 11 and on Linux, whenever a script needs a count.

## 3. How users interact with it

The library has functions, and one command-line program, `wordcount` (F04, with the `--lines` option of F05, the `--chars` option of F06, the `--longest` option of F07, the `--again` option of F08, and the `--sentences` option of F09).

1. Troy imports `troy_mode_trial` in a Python script or session.
2. Troy calls a counting function with the path of one UTF-8 text file.
3. The function reads the file and returns the count as an `int`.
4. If the file is missing or is not valid UTF-8, the function raises Python's own exception for that case.

To count the paragraphs of a text (F10), Troy calls `count_paragraphs(text)` with the text itself, a Python `str`, not a file's path. It returns the number of paragraphs as an `int`. It reads no file and raises no file error.

The function names in the prototypes show the flow. The Interface Designer fixes the final names and signatures in each feature's design.

To count words outside Python, Troy types `wordcount FILE` in PowerShell. The command prints the number of words in the file, counted as F03 counts them. If the file is missing, it prints an error that names the file and exits with a code that is not 0.

To count lines outside Python, Troy types `wordcount --lines FILE`. The command prints the number of lines in the file, counted as F02 counts them, instead of its words. A missing file gives the same error and exit code as without the option.

To count characters outside Python, Troy types `wordcount --chars FILE`. The command prints the number of characters of the file's decoded text, line ends included, instead of its words. A file error gives the same message and exit code as `wordcount FILE`.

To find the length of the longest word outside Python, Troy types `wordcount --longest FILE`. The command prints the length, in characters, of the longest word in the file, with words as F03 counts them, instead of the number of words. A file with no word prints 0. A file error gives the same message and exit code as `wordcount FILE`.

To count sentences outside Python, Troy types `wordcount --sentences FILE`. The command prints the number of sentences in the file instead of its words. A sentence is a run of text that ends in `.`, `!`, or `?`. A file error gives the same message and exit code as `wordcount FILE`.

To count a file with the option of the last run, Troy types `wordcount --again FILE`. Every run that prints a count keeps its option, or that it had none, in a settings file in Troy's data folder, and `--again` counts FILE with that option. Before any such run, `wordcount --again` prints an error and exits with code 2.

### 3.1 Prototypes

| Prototype | Feature | File |
| --- | --- | --- |
| Count the words of a file | F01 | `docs/prototypes/F01-count-words.md` |
| Count the lines of a file | F02 | `docs/prototypes/F02-count-lines.md` |
| Skip runs without a letter or digit | F03 | `docs/prototypes/F03-words-need-a-letter-or-digit.md` |
| Count words in PowerShell | F04 | `docs/prototypes/F04-word-count-command.md` |
| Count lines in PowerShell | F05 | `docs/prototypes/F05-line-count-option.md` |
| Count characters in PowerShell | F06 | `docs/prototypes/F06-character-count-option.md` |
| Find the longest word in PowerShell | F07 | `docs/prototypes/F07-longest-word-option.md` |
| Run again with the last option in PowerShell | F08 | `docs/prototypes/F08-remember-the-last-options.md` |
| Count sentences in PowerShell | F09 | `docs/prototypes/F09-count-sentences-option.md` |
| Count the paragraphs of a text | F10 | `docs/prototypes/F10-count-paragraphs-function.md` |

## 4. Features

| ID | Feature | Hard dependencies | Soft dependencies | Version | Status |
| --- | --- | --- | --- | --- | --- |
| F01 | Count words | None | None | v0.1 | Usable on Troy's devices |
| F02 | Count lines | None | None | v0.2 | Usable on Troy's devices |
| F03 | Words need a letter or digit | F01 | None | v0.1 | Usable on Troy's devices |
| F04 | Word count command | F03 | None | v0.2 | Usable on Troy's devices |
| F05 | Line count option | F02, F04 | None | v0.3 | Ran for real on Troy's PC |
| F06 | Character count option | F04 | None | v0.3 | Ran for real on Troy's PC |
| F07 | Longest word option | F04 | None | v0.3 | Ran for real on Troy's PC |
| F08 | Remember the last options | F04 | None | v0.3 | Not started |
| F09 | Count sentences option | F04 | None | v0.3 | Not started |
| F10 | Count paragraphs function | F04 | None | v0.4 | Not started |

### 4.1 What each feature does

- **F01 Count words.** Counts the words in one UTF-8 text file. A word is a run of characters that are not white space.
- **F02 Count lines.** Counts the lines in one UTF-8 text file. A last line without a line break still counts.
- **F03 Words need a letter or digit.** Changes F01's word: a word is a run of characters that are not white space and that holds at least one letter or digit, that is, at least one character for which Python's `str.isalnum()` is true. A run of other characters only, such as `--` or `...`, is not a word. A run such as `don't`, `x--y`, or `3.14` is still one word.
- **F04 Word count command.** Gives Troy a `wordcount FILE` command in PowerShell. It prints the number of words in one UTF-8 text file, counted as F03 counts them, so Troy can count words outside Python. If the file is missing, it prints an error that names the file, and its exit code is not 0.
- **F05 Line count option.** Adds the `--lines` option to `wordcount`: `wordcount --lines FILE` prints the number of lines in one UTF-8 text file, counted as F02 counts them, instead of its words. `wordcount FILE` without the option still prints the words. A missing file gives the same error and exit code as `wordcount FILE`.
- **F06 Character count option.** Adds the `--chars` option to `wordcount`: `wordcount --chars FILE` prints the number of characters of one UTF-8 text file instead of its words. It counts the characters of the file's decoded text, line ends included: a character is one Unicode code point, so `你` is one character, not three bytes, and a Windows line end `\r\n` is two characters. A byte order mark at the start of the file is not counted (Q12). A missing file, or a file that is not valid UTF-8, gives the same error message and exit code as `wordcount FILE`.
- **F07 Longest word option.** Adds the `--longest` option to `wordcount`: `wordcount --longest FILE` prints the length, in characters, of the longest word of one UTF-8 text file instead of its number of words. A word is what F03 counts as a word, the whole run of characters that are not white space, so `don't,` is 6 characters long (Q15). A character is one Unicode code point, as for `--chars`, so `世界!` is 3 characters long. A file with no word, such as an empty file or a file of only `--` and `...`, prints 0. A byte order mark at the start of the file is not part of a word (Q5). A missing file, or a file that is not valid UTF-8, gives the same error message and exit code as `wordcount FILE`.
- **F08 Remember the last options.** Adds the `--again` option to `wordcount`. Every run of `wordcount` that prints a count writes its option, or that it had none, to one settings file in the user's data folder (Q17): on Windows `%APPDATA%\wordcount\settings.json`, on Linux `$XDG_DATA_HOME/wordcount/settings.json`, or `~/.local/share/wordcount/settings.json` when `XDG_DATA_HOME` is not set. The file holds only that option, never a file's name or text (Q18). `wordcount --again FILE` counts FILE with the saved option: after `wordcount --lines a.txt`, `wordcount --again b.txt` prints the lines of `b.txt`, and after `wordcount a.txt` it prints the words. A run that fails, such as one with a missing file or a usage error, leaves the settings as they were (Q19). `--again` with no saved option, or with a settings file it cannot read, prints an error that names the settings file and exits with code 2 (Q20). `--again` together with a counting option, such as `--again --lines`, is a usage error with exit code 2 (Q21). When the settings file cannot be written, the count still prints, a warning that names the settings file goes to the error output, and the exit code is 0 (Q22).
- **F09 Count sentences option.** Adds the `--sentences` option to `wordcount`: `wordcount --sentences FILE` prints the number of sentences in one UTF-8 text file instead of its words. A sentence is a run of text that ends in `.`, `!`, or `?`. A run of these marks, such as `...` or `?!`, ends one sentence (Q23). A sentence holds at least one letter or digit, as an F03 word does, so a file of only `-- ...` has 0 sentences (Q24). Text after the last mark is not a sentence, so `Done. Not yet` has 1 sentence (Q25). A mark ends a sentence wherever it stands, also inside a number or an abbreviation, so `Pi is 3.14.` has 2 sentences. Only `.`, `!`, and `?` end a sentence; the Chinese marks `。`, `！`, and `？` do not (Q26). A byte order mark at the start of the file is ignored (Q5). A missing file, or a file that is not valid UTF-8, gives the same error message and exit code as `wordcount FILE`. `--sentences` together with another counting option is a usage error with exit code 2, as for `--lines --chars` (Q13).
- **F10 Count paragraphs function.** Adds the library function `count_paragraphs(text)`, which returns the number of paragraphs in a text, a Python `str`. A paragraph is a run of lines that are not blank. A blank line is empty or holds only white space, the characters for which `str.isspace()` is true, as in Q1 (Q27). Lines end as F02's lines do: `\n`, `\r\n`, and `\r` each end one line (Q28). Any number of blank lines between two paragraphs separates them once, and blank lines at the start or the end count for nothing. An empty text, or a text of only blank lines, has 0 paragraphs. One `U+FEFF` byte order mark at the start of the text is ignored, as Q5 ignores it in a file (Q29). F10 adds no `wordcount` option, no message, and no file: `wordcount` prints exactly what it printed before.

## 5. Dependency graph and order

F03 changes F01's word, so F03 has a hard dependency on F01. F04 counts words as F03 counts them, so F04 has a hard dependency on F03. F02 depends on none of them. F05 adds an option to F04's command and counts lines as F02 counts them, so F05 has a hard dependency on F02 and on F04. F06 adds an option to F04's command and needs no other feature, so F06 has a hard dependency on F04 only. F07 adds an option to F04's command and finds words as F04 counts them, so F07 has a hard dependency on F04 only. F08 adds an option to F04's command that repeats the last run's option, so F08 has a hard dependency on F04 only. F09 adds an option to F04's command and needs no other feature, so F09 has a hard dependency on F04 only. F05 to F09 do not depend on each other. The new features come after the accepted ones in the order, F08 before F09, so F09's design makes `--again` remember `--sentences` too (Troy's choice on 2026-11-26). F10 has a hard dependency on F04 only, as Troy asked on 2026-11-26, and comes last in the order, after every feature that is accepted or under way.

```mermaid
flowchart LR
  F01 --> F03
  F03 --> F04
  F04 --> F05
  F02 --> F05
  F04 --> F06
  F04 --> F07
  F04 --> F08
  F04 --> F09
  F04 --> F10
```

Topological order: F01, F03, F04, F07, F06, F02, F05, F08, F09, F10

## 6. Version plan

| Version | Features | What makes it usable on its own |
| --- | --- | --- |
| v0.1 | F01, F03 | Troy's scripts can count the words of a UTF-8 text file, where a word holds at least one letter or digit. |
| v0.2 | F04, F02 | Troy can count the words of a UTF-8 text file with the `wordcount` command in PowerShell, and Troy's scripts can also count the lines of a UTF-8 text file. |
| v0.3 | F05, F06, F07, F08, F09 | Troy can count the lines of a UTF-8 text file with `wordcount --lines`, count its characters with `wordcount --chars`, find the length of its longest word with `wordcount --longest`, count its sentences with `wordcount --sentences`, and count another file with the option of the last run with `wordcount --again`, in PowerShell. |
| v0.4 | F10 | Troy's scripts can count the paragraphs of a text with `count_paragraphs`. |

## 7. Non-functional requirements

- The library runs on Python 3.13.
- The library uses the Python standard library only. It has no third-party runtime dependency.
- The library runs on Windows 11 and on Linux, and gives the same counts for the same file on both.
- The library reads files only. The `wordcount` command writes one file, its settings file in the user's data folder (F08), which holds only the last run's option. Nothing is sent anywhere.
- The library reads text as UTF-8 only.

### 7.1 Performance targets

None

## 8. Out of scope

- Encodings other than UTF-8.
- Counting a folder of files, or several files in one call.
- Any command-line program other than `wordcount`, any `wordcount` option other than `--lines`, `--chars`, `--longest`, `--sentences`, and `--again`, two counting options in one command, printing the longest word itself, and a second file argument.
- Keeping anything but the last run's option, such as the files of earlier runs or more than one run.
- Telling numbers and abbreviations apart from sentence ends, and sentence marks other than `.`, `!`, and `?`.
- Counting the paragraphs of a file, and a `wordcount` option or message for paragraphs.

## 9. Open questions

Troy decided these questions in advance for troy-mode's trial. Each decision is the recommended answer.

| ID | Question | Proposal | Decision |
| --- | --- | --- | --- |
| Q1 | Which characters are white space for F01? | The characters for which Python's `str.isspace()` is true, so Unicode white space such as U+3000 also separates words. | Decided by Troy in advance for this trial: as proposed. |
| Q2 | Which line breaks does F02 accept? | `\n`, `\r\n`, and `\r` each end one line. A file from Windows and the same file from Linux give the same count. | Decided by Troy in advance for this trial: as proposed. |
| Q3 | What do the functions return for an empty file? | 0 words and 0 lines. A file that holds only one line break has 1 line and 0 words. | Decided by Troy in advance for this trial: as proposed. |
| Q4 | What happens when the file is missing or is not valid UTF-8? | The function raises Python's own exception, such as `FileNotFoundError` or `UnicodeDecodeError`. It defines no exception of its own. | Decided by Troy in advance for this trial: as proposed. |
| Q5 | Does a UTF-8 byte order mark at the start of the file count as text? | No. The function ignores one byte order mark at the start of the file, so the mark never counts as a word. | Decided by Troy in advance for this trial: as proposed. |
| Q6 | The architecture 1.0 says that the module `counting` counts the words of a text. Does F02 need an architecture change? | No. `counting` owns `src/troy_mode_trial/**`, and counting lines is counting too. F02 fits the module as it is. | Decided by Troy in advance for this trial: as proposed. |
| Q7 | Does F05's option also get a short form, such as `-l`? | No. Only `--lines`, as Troy asked; a short form can come later as its own change. | Decided by Troy on 2026-11-17: as proposed ("全按推荐"). |
| Q8 | What does `wordcount --lines` print for a missing file, or a file that is not valid UTF-8? | The same error message and exit code as `wordcount FILE` gives for that file. | Decided by Troy on 2026-11-17: as proposed ("全按推荐"). |
| Q9 | When is F05 built? | After v0.2 is released, so the v0.2 release holds only F02 and F04. | Decided by Troy on 2026-11-17: as proposed ("全按推荐"). |
| Q10 | Does F06's option also get a short form, such as `-c`? | No. Only `--chars`, as for `--lines` (Q7). | Decided by Troy on 2026-11-23: as proposed ("全按推荐"). |
| Q11 | How many characters is a Windows line end `\r\n`? | Two, as the file holds them. `wordcount --chars` counts the decoded text as it is, with no line-end translation, so the same file gives the same count on Windows and on Linux. | Decided by Troy on 2026-11-23: as proposed ("全按推荐"). |
| Q12 | Does a byte order mark at the start of the file count as a character? | No, as for words (Q5). | Decided by Troy on 2026-11-23: as proposed ("全按推荐"). |
| Q13 | What does `wordcount --lines --chars FILE` do? | A usage error with exit code 2, as for any other wrong command line: one command prints one count. | Decided by Troy on 2026-11-23: as proposed ("全按推荐"). |
| Q14 | Does F07's option also get a short form, such as `-L`? | No. Only `--longest`, as for `--lines` and `--chars` (Q7, Q10). | Decided by Troy on 2026-11-25: as proposed ("全按推荐"). |
| Q15 | Does punctuation that touches a word count toward its length, as the comma in `don't,` does? | Yes. The word is the whole run that F03 counts, so `wordcount --longest` and `wordcount` agree on what a word is. | Decided by Troy on 2026-11-25: as proposed ("全按推荐"). |
| Q16 | What does `wordcount --longest` together with `--lines` or `--chars` do? | A usage error with exit code 2, as for `--lines --chars` (Q13). | Decided by Troy on 2026-11-25: as proposed ("全按推荐"). |
| Q17 | Where is F08's settings file? | On Windows `%APPDATA%\wordcount\settings.json`; on Linux `$XDG_DATA_HOME/wordcount/settings.json`, or `~/.local/share/wordcount/settings.json` without `XDG_DATA_HOME`. These are the usual data folders of each system. | Decided by Troy on 2026-11-26: as proposed ("全按推荐"). |
| Q18 | What does the settings file keep? | Only the last run's option, or that it had none. Never a file's name or text, so the file says nothing about Troy's files. | Decided by Troy on 2026-11-26: as proposed ("全按推荐"). |
| Q19 | Does a failed run, such as one with a missing file, change the settings? | No. Only a run that prints a count keeps its option. | Decided by Troy on 2026-11-26: as proposed ("全按推荐"). |
| Q20 | What does `wordcount --again` do before any option is saved, or when the settings file cannot be read? | An error that names the settings file, with exit code 2. | Decided by Troy on 2026-11-26: as proposed ("全按推荐"). |
| Q21 | What does `--again` together with a counting option, such as `--again --lines`, do? | A usage error with exit code 2, as for two counting options (Q13). | Decided by Troy on 2026-11-26: as proposed ("全按推荐"). |
| Q22 | What happens when the settings file cannot be written? | The count still prints, a warning that names the settings file goes to the error output, and the exit code is 0: the count Troy asked for matters more. | Decided by Troy on 2026-11-26: as proposed ("全按推荐"). |
| Q23 | Does a run of marks, such as `...` or `?!`, end one sentence or several? | One. | Decided by Troy on 2026-11-26: as proposed ("全按推荐"). |
| Q24 | Must a sentence hold a letter or digit? | Yes, as an F03 word must, so marks alone, such as `-- ...`, are no sentence. | Decided by Troy on 2026-11-26: as proposed ("全按推荐"). |
| Q25 | Is text after the last mark, such as `Not yet` in `Done. Not yet`, a sentence? | No, as Troy's definition says: a sentence ends in a mark. | Decided by Troy on 2026-11-26: as proposed ("全按推荐"). |
| Q26 | Do the Chinese marks `。`, `！`, and `？` end a sentence? | No. Only `.`, `!`, and `?`, as Troy asked; the Chinese marks can come later as their own change. | Decided by Troy on 2026-11-26: as proposed ("全按推荐"). |
| Q27 | Is a line of only spaces or tabs blank, so that it separates two paragraphs? | Yes. A blank line is empty or holds only white space, as Q1 defines white space: a line that looks empty is empty. | Decided by Troy on 2026-11-26: as proposed ("全按推荐"). |
| Q28 | Which line breaks does F10 accept? | `\n`, `\r\n`, and `\r`, as F02 (Q2), so a text from Windows and the same text from Linux give the same count. | Decided by Troy on 2026-11-26: as proposed ("全按推荐"). |
| Q29 | Does a byte order mark at the start of the text count as text? | No. One `U+FEFF` at the start is ignored, as in a file (Q5), so a text read with a mark gives the same count as without it. | Decided by Troy on 2026-11-26: as proposed ("全按推荐"). |

## 10. Change log

| Version | Date | Change |
| --- | --- | --- |
| 0.1 | 2026-11-07 | First draft. |
| 1.1 | 2026-11-07 | F01 accepted: its status is now Passes tests on main. |
| 1.2 | 2026-11-07 | A word must hold at least one letter or digit (`str.isalnum()`). F01 is accepted, so the change is the new feature F03, with a hard dependency on F01. The Feature cells of F01 and F02 hold only their short names; section 4.1 describes each feature. |
| 2.1 | 2026-11-08 | F02 moves to the new version v0.2, so v0.1 holds F01 and F03. The version plan adds v0.2. F02's behavior does not change, and F01 and F03 do not change. |
| 3.0 | 2026-11-08 | Approved by Troy. |
| 3.1 | 2026-11-08 | F03 accepted: its status is now Passes tests on main. |
| 3.2 | 2026-11-08 | Troy accepted v0.1.0 on Troy's PC: F01 and F03 are now Usable on Troy's devices. |
| 3.3 | 2026-11-14 | The new feature F04, Word count command: a `wordcount FILE` command in PowerShell that prints the words of one UTF-8 text file, counted as F03 counts them. F04 has a hard dependency on F03, comes before F02 in the order (F01, F03, F04, F02), and is in v0.2 with F02. Its prototype is `docs/prototypes/F04-word-count-command.md`. Sections 1, 3, and 8 no longer rule out a command-line program. F01, F02, and F03 do not change. |
| 4.0 | 2026-11-14 | Approved by Troy. |
| 4.1 | 2026-11-15 | F04 accepted: its status is now Ran for real on Troy's PC. |
| 4.2 | 2026-11-17 | F02 accepted: its status is now Passes tests on main. F02 is a library function with no command of its own to run for real. |
| 4.3 | 2026-11-17 | The new feature F05, Line count option: `wordcount --lines FILE` prints the lines of one UTF-8 text file, counted as F02 counts them. F02 and F04 are accepted and do not change, so F05 is a new feature with a hard dependency on both, last in the order (F01, F03, F04, F02, F05), in the new version v0.3. Its prototype is `docs/prototypes/F05-line-count-option.md`. Section 8 allows the `--lines` option. New questions Q7 to Q9. From Troy's idea #51. |
| 5.0 | 2026-11-17 | Approved by Troy. |
| 5.1 | 2026-11-17 | Troy accepted v0.2.0 on Troy's PC: F02 and F04 are now Usable on Troy's devices. |
| 5.2 | 2026-11-23 | The new feature F06, Character count option: `wordcount --chars FILE` prints the characters of one UTF-8 text file, its decoded text with line ends included. F04 is accepted and does not change, so F06 is a new feature with a hard dependency on F04 only, right after F04 in the order (F01, F03, F04, F06, F02, F05), in v0.3 beside F05. Its prototype is `docs/prototypes/F06-character-count-option.md`. Section 8 allows the `--chars` option. New questions Q10 to Q13. F01 to F05 do not change. |
| 6.0 | 2026-11-23 | Approved by Troy. |
| 6.1 | 2026-11-23 | F06 accepted: its status is now Ran for real on Troy's PC. |
| 6.2 | 2026-11-23 | F05 accepted: its status is now Ran for real on Troy's PC. |
| 6.3 | 2026-11-25 | The new feature F07, Longest word option: `wordcount --longest FILE` prints the length, in characters, of the longest word of one UTF-8 text file, with words as F03 counts them, and 0 for a file with no word. F04 is accepted and does not change, so F07 is a new feature with a hard dependency on F04 only, right after F04 in the order (F01, F03, F04, F07, F06, F02, F05), in v0.3 beside F05 and F06. Its prototype is `docs/prototypes/F07-longest-word-option.md`. Section 8 allows the `--longest` option. New questions Q14 to Q16. F01 to F06 do not change. |
| 7.0 | 2026-11-25 | Approved by Troy. |
| 7.1 | 2026-11-25 | F07 accepted: its status is now Ran for real on Troy's PC. |
| 7.2 | 2026-11-26 | Two new features in v0.3 beside F05 to F07, each with a hard dependency on F04 only: F08, Remember the last options (`wordcount --again FILE` counts with the option of the last run, kept in a settings file in the user's data folder), and F09, Count sentences option (`wordcount --sentences FILE` prints the number of sentences). F04 is accepted and does not change. The order is F01, F03, F04, F07, F06, F02, F05, F08, F09. Their prototypes are `docs/prototypes/F08-remember-the-last-options.md` and `docs/prototypes/F09-count-sentences-option.md`. Section 7 lets the command write its settings file, and section 8 allows the two options. New questions Q17 to Q26. F01 to F07 do not change. |
| 8.0 | 2026-11-26 | Approved by Troy. |
| 8.1 | 2026-11-26 | The new feature F10, Count paragraphs function: the library function `count_paragraphs(text)` returns the number of paragraphs in a text, where a paragraph is a run of lines that are not blank. It has a hard dependency on F04 only, as Troy asked, comes last in the order (F01, F03, F04, F07, F06, F02, F05, F08, F09, F10), and is the only feature of the new version v0.4. It adds no `wordcount` option, message, or file. Its prototype is `docs/prototypes/F10-count-paragraphs-function.md`. Section 8 rules out paragraphs in files and in `wordcount`. New questions Q27 to Q29. F01 to F09 do not change. |
| 9.0 | 2026-11-26 | Approved by Troy. |
