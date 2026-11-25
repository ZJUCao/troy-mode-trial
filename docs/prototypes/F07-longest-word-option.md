# F07 prototype: the longest word option

A PowerShell session in Windows Terminal. `wordcount --longest` finds the longest word of one UTF-8 text file, with words as F03 counts them, and prints its length in characters. Without the option, `wordcount` still prints the words, as in F04.

## Find the longest word of a file

`notes.txt` in the current folder is UTF-8 and holds the two lines `Hello world` and `  troy-mode  trial`, each ending with a Linux line end `\n`. Its words are `Hello`, `world`, `troy-mode`, and `trial`; the longest, `troy-mode`, has 9 characters.

```text
PS> wordcount --longest notes.txt
9
PS> wordcount notes.txt
4
```

## Characters, and the whole word

`greeting.txt` in the current folder is UTF-8 and holds the one line `你好 世界!`, ending with a Windows line end `\r\n`. Its words are `你好` and `世界!`. The exclamation mark belongs to the word, as F03 counts it, so the longest word has 3 characters, not 9 bytes.

```text
PS> wordcount --longest greeting.txt
3
```

## A file with no word

`dashes.txt` in the current folder is UTF-8 and holds the one line `-- ...`. Neither run holds a letter or digit, so the file has no word.

```text
PS> wordcount --longest dashes.txt
0
```

## A missing file

```text
PS> wordcount --longest missing.txt
wordcount: missing.txt: no such file
PS> $LASTEXITCODE
2
```
