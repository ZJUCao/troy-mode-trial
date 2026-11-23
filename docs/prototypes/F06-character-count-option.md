# F06 prototype: the character count option

A PowerShell session in Windows Terminal. `wordcount --chars` counts the characters of one UTF-8 text file, its decoded text with the line ends, and prints the count. Without the option, `wordcount` still prints the words, as in F04.

## Count the characters of a file

`notes.txt` in the current folder is UTF-8 and holds the two lines `Hello world` and `  troy-mode  trial`, each ending with a Linux line end `\n`.

```text
PS> wordcount --chars notes.txt
31
PS> wordcount notes.txt
4
```

## Characters, not bytes

`hello.txt` in the current folder is UTF-8 and holds the one line `你好`, ending with a Windows line end `\r\n`. The file has 8 bytes, but 4 characters: `你`, `好`, `\r`, and `\n`.

```text
PS> wordcount --chars hello.txt
4
```

## A missing file

```text
PS> wordcount --chars missing.txt
wordcount: missing.txt: no such file
PS> $LASTEXITCODE
2
```
