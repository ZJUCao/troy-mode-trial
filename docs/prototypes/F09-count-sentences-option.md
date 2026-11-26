# F09 prototype: the count sentences option

A PowerShell session in Windows Terminal. `wordcount --sentences` prints the number of sentences of one UTF-8 text file. A sentence is a run of text that ends in `.`, `!`, or `?` and holds at least one letter or digit. Without the option, `wordcount` still prints the words, as in F04.

## Count the sentences of a file

`story.txt` in the current folder is UTF-8 and holds the two lines `It rains. Does it stop? Yes!!` and `Wait...`, each ending with a Linux line end `\n`. Its sentences are `It rains.`, `Does it stop?`, `Yes!!`, and `Wait...`: a run of marks such as `!!` or `...` ends one sentence.

```text
PS> wordcount --sentences story.txt
4
PS> wordcount story.txt
7
```

## Text after the last mark

`draft.txt` in the current folder is UTF-8 and holds the one line `Done. Not yet`, ending with a Windows line end `\r\n`. `Not yet` ends in no mark, so it is not a sentence.

```text
PS> wordcount --sentences draft.txt
1
```

## A mark inside a number

`pi.txt` in the current folder is UTF-8 and holds the one line `Pi is 3.14.`, ending with `\n`. The point inside `3.14` ends a sentence too, so the file has the sentences `Pi is 3.` and `14.`.

```text
PS> wordcount --sentences pi.txt
2
```

## A file with no sentence

`dashes.txt` in the current folder is UTF-8 and holds the one line `-- ...`. It ends in marks, but holds no letter or digit, so it has no sentence.

```text
PS> wordcount --sentences dashes.txt
0
```

## A missing file

```text
PS> wordcount --sentences missing.txt
wordcount: missing.txt: no such file
PS> $LASTEXITCODE
2
```
