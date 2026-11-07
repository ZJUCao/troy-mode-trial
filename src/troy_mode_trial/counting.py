"""Word counting for UTF-8 text files."""

import os
from pathlib import Path


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
    text_path = _checked_path(path)
    with Path(text_path).open(encoding="utf-8-sig") as handle:
        return len(handle.read().split())


def _checked_path(path: object) -> str:
    """Return `path` as a `str`, or raise `TypeError` for any other type.

    Args:
        path: The value the caller passed as a path.

    Returns:
        The path as a `str`.

    Raises:
        TypeError: `path` is neither a `str` nor an `os.PathLike[str]`.
    """
    if not isinstance(path, (str, os.PathLike)):
        raise TypeError(f"path must be str or os.PathLike, not {type(path).__name__}")
    text_path = os.fspath(path)
    if not isinstance(text_path, str):
        raise TypeError("path must be str or os.PathLike[str], not bytes")
    return text_path
