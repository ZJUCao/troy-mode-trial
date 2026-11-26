# F08 prototype: remember the last options

A PowerShell session in Windows Terminal. Every run of `wordcount` that prints a count keeps its option, or that it had none, in the settings file `%APPDATA%\wordcount\settings.json`. `wordcount --again FILE` counts FILE with that option. The settings file holds only the option, never a file's name or text.

In these sections the user's folder is `C:\Users\me`, so the settings file is `C:\Users\me\AppData\Roaming\wordcount\settings.json`. The exact wording of the error is the design's; it names the settings file.

## Before any run

The data folder holds no `wordcount` folder yet. `notes.txt` in the current folder is UTF-8 and holds the two lines `Hello world` and `  troy-mode  trial`, each ending with a Linux line end `\n`.

```text
PS> wordcount --again notes.txt
wordcount: no saved options to run again: C:\Users\me\AppData\Roaming\wordcount\settings.json
PS> $LASTEXITCODE
2
```

## Run again with the last option

`notes.txt` is as in the section before. `greeting.txt` in the current folder is UTF-8 and holds the one line `你好 世界!`, ending with a Windows line end `\r\n`. After `--lines`, `--again` counts the lines of `greeting.txt`.

```text
PS> wordcount --lines notes.txt
2
PS> wordcount --again greeting.txt
1
```

## No option is an option too

The files are as in the section before. After a run without an option, `--again` counts words.

```text
PS> wordcount notes.txt
4
PS> wordcount --again greeting.txt
2
```

## A failed run keeps the settings

The files are as in the section before. The run on the missing file prints no count, so the saved option stays `--longest`.

```text
PS> wordcount --longest notes.txt
9
PS> wordcount --longest missing.txt
wordcount: missing.txt: no such file
PS> wordcount --again greeting.txt
3
```
