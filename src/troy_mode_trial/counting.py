"""Word counting for UTF-8 text files."""

import os


def count_words(path: str | os.PathLike[str]) -> int:
    """Count the words in one UTF-8 text file.

    A word is a run of one or more characters for which `str.isspace()` is
    false. Every character for which `str.isspace()` is true separates words,
    including Unicode white space such as U+3000. Line breaks are white space,
    so LF, CR LF, and CR give the same count. One byte order mark
    (U+FEFF) at the start of the file is ignored. A U+FEFF anywhere else is
    part of a word.

    Args:
        path: The path of the file to count, absolute or relative to the
            current working directory. It names one existing, readable,
            regular file whose content is valid UTF-8. `bytes` paths are not
            accepted.

    Returns:
        The number of words in the file, 0 or more. A file that is empty or
        holds only white space returns 0.

    Raises:
        FileNotFoundError: No file exists at `path`.
        IsADirectoryError: `path` names a folder (Linux).
        PermissionError: `path` names a folder (Windows), or the process may
            not read the file.
        UnicodeDecodeError: The file content is not valid UTF-8.
        TypeError: `path` is neither a `str` nor an `os.PathLike[str]`.
    """
    raise NotImplementedError
