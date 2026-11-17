# F05 prototype: the line count option

A PowerShell session in Windows Terminal. `wordcount --lines` counts the lines of one UTF-8 text file the way F02 counts them, and prints the count. Without the option, `wordcount` still prints the words, as in F04.

## Count the lines of a file

`notes.txt` in the current folder is UTF-8 and holds the two lines `Hello world` and `  troy-mode  trial`.

```text
PS> wordcount --lines notes.txt
2
PS> wordcount notes.txt
4
```

## A missing file

```text
PS> wordcount --lines missing.txt
wordcount: missing.txt: no such file
PS> $LASTEXITCODE
2
```
