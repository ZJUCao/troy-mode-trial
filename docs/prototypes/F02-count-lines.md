# F02 prototype: count the lines of a file

A Python session on Linux. `notes.txt` is UTF-8 and holds the two lines `Hello world` and `  troy-mode  trial`, the second without a line break at the end. `windows.txt` holds the same text with `\r\n` line breaks. The name `count_lines` shows the flow. The Interface Designer fixes the final name in F02's design.

```pycon
>>> from troy_mode_trial import count_lines
>>> count_lines("notes.txt")
2
>>> count_lines("windows.txt")
2
>>> count_lines("empty.txt")
0
>>> count_lines("missing.txt")
Traceback (most recent call last):
  ...
FileNotFoundError: [Errno 2] No such file or directory: 'missing.txt'
```
