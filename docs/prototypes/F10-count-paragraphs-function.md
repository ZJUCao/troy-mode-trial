# F10 prototype: count the paragraphs of a text

A Python session on Linux. `count_paragraphs` takes the text itself, not a file's path. A paragraph is a run of lines that are not blank, and a blank line is empty or holds only white space. The name `count_paragraphs` shows the flow. The Interface Designer fixes the final name in F10's design. `wordcount` does not change: it has no option for paragraphs.

```pycon
>>> from troy_mode_trial import count_paragraphs
>>> count_paragraphs("First line\nstill the first paragraph\n\nSecond paragraph\n")
2
>>> count_paragraphs("One\r\n  \t\r\nTwo\r\n\r\n\r\nThree")
3
>>> count_paragraphs("\n\n   \n")
0
>>> count_paragraphs("")
0
```
