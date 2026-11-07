# F01 prototype: count the words of a file

A Python session on Windows 11. `notes.txt` is UTF-8 and holds the two lines `Hello world` and `  troy-mode  trial`, the second without a line break at the end. The name `count_words` shows the flow. The Interface Designer fixes the final name in F01's design.

```pycon
>>> from troy_mode_trial import count_words
>>> count_words("notes.txt")
4
>>> count_words("empty.txt")
0
>>> count_words("missing.txt")
Traceback (most recent call last):
  ...
FileNotFoundError: [Errno 2] No such file or directory: 'missing.txt'
>>> count_words("latin1.txt")
Traceback (most recent call last):
  ...
UnicodeDecodeError: 'utf-8' codec can't decode byte 0xe9 in position 3: invalid continuation byte
```
