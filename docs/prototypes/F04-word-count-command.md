# F04 prototype: the word count command

A PowerShell session in Windows Terminal. `wordcount` counts the words of one UTF-8 text file the way F03 counts them, and prints the count.

## Count a file

`notes.txt` in the current folder is UTF-8 and holds the two lines `Hello world` and `  troy-mode  trial`.

```text
PS> wordcount notes.txt
4
```

## A missing file

```text
PS> wordcount missing.txt
wordcount: missing.txt: no such file
PS> $LASTEXITCODE
2
```
