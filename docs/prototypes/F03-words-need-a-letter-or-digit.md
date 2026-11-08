# F03 prototype: skip runs without a letter or digit

A Python session on Windows 11. `dashes.txt` is UTF-8 and holds the line `Wait -- what ... don't x--y 3.14 _`. The runs `--`, `...`, and `_` hold no letter or digit, so they are not words. The name `count_words` is F01's function; F03 changes what it counts.

```pycon
>>> from troy_mode_trial import count_words
>>> count_words("dashes.txt")
5
>>> count_words("only-symbols.txt")
0
```

`only-symbols.txt` holds `-- ... !!!` and nothing else.
