"""Word counting for UTF-8 text files."""

import errno
import os
from pathlib import Path


def count_chars(path: str | os.PathLike[str]) -> int:
    """Count the characters in one UTF-8 text file.

    A character is one Unicode code point of the decoded text, line ends
    included. The function decodes the whole file and removes one byte order
    mark (U+FEFF) at the start of the file. Line ends count as the file holds
    them: LF is one character, CR is one, and CR LF is two. A U+FEFF anywhere
    else counts as one character.

    Args:
        path: The path of the file to count, absolute or relative to the
            current working directory. It names one existing, readable,
            regular file whose content is valid UTF-8. `bytes` paths are not
            accepted.

    Returns:
        The number of characters in the file, 0 or more. A file that is empty,
        or holds only the byte order mark, returns 0.

    Raises:
        FileNotFoundError: No file exists at `path`, or `path` is empty.
        IsADirectoryError: `path` names a folder (Linux).
        PermissionError: `path` names a folder (Windows), or the process may
            not read the file.
        UnicodeDecodeError: Any byte of the file is not valid UTF-8.
        TypeError: `path` is neither a `str` nor an `os.PathLike[str]`.
    """
    text_path = _checked_path(path)
    if text_path == "":
        # Path("") becomes Path("."), the current folder; an empty path names no file.
        raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), text_path)
    # newline="" turns line-end translation off, so CR LF stays two characters.
    with Path(text_path).open(encoding="utf-8-sig", newline="") as handle:
        return len(handle.read())


def count_lines(path: str | os.PathLike[str]) -> int:
    """Count the lines in one UTF-8 text file.

    Only LF, CR LF, and a lone CR end a line. A CR directly followed by LF is
    one line break. No other character ends a line, so the function must not
    count with `str.splitlines()`. A last line without a line break
    still counts. One byte order mark (U+FEFF) at the start of the file is
    ignored.

    Args:
        path: The path of the file to count, absolute or relative to the
            current working directory. It names one existing, readable,
            regular file whose content is valid UTF-8. `bytes` paths are not
            accepted.

    Returns:
        The number of lines in the file, 0 or more. A file that is empty, or
        holds only the byte order mark, returns 0. A file that holds only one
        line break returns 1.

    Raises:
        FileNotFoundError: No file exists at `path`, or `path` is empty.
        IsADirectoryError: `path` names a folder (Linux).
        PermissionError: `path` names a folder (Windows), or the process may
            not read the file.
        UnicodeDecodeError: The file content is not valid UTF-8.
        TypeError: `path` is neither a `str` nor an `os.PathLike[str]`.
    """
    text_path = _checked_path(path)
    if text_path == "":
        # Path("") becomes Path("."), the current folder; an empty path names no file.
        raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), text_path)
    # Default newline mode turns LF, CR LF, and a lone CR into LF, and nothing else.
    with Path(text_path).open(encoding="utf-8-sig") as handle:
        text = handle.read()
    breaks = text.count("\n")
    return breaks + (1 if text and not text.endswith("\n") else 0)


def count_longest(path: str | os.PathLike[str]) -> int:
    """Find the length of the longest word in one UTF-8 text file.

    The function decodes the whole file and removes one byte order mark
    (U+FEFF) at the start of the file. It splits the text into words exactly as
    `count_words` does, with the same word rule and the same file reading. The
    length counts Unicode code points, so a word that is several code points
    counts once for each, and punctuation in a word counts. A run with no
    letter or digit, such as `--`, is not a word, and its length never counts.
    A U+FEFF anywhere else is part of the run it is in.

    Args:
        path: The path of the file to read, absolute or relative to the
            current working directory. It names one existing, readable,
            regular file whose content is valid UTF-8. `bytes` paths are not
            accepted.

    Returns:
        The greatest length, in code points, of a word in the file, 0 or more.
        A file with no word returns 0, so `count_words(path)` is 0 exactly when
        this is 0.

    Raises:
        FileNotFoundError: No file exists at `path`, or `path` is empty.
        IsADirectoryError: `path` names a folder (Linux).
        PermissionError: `path` names a folder (Windows), or the process may
            not read the file.
        UnicodeDecodeError: Any byte of the file is not valid UTF-8.
        TypeError: `path` is neither a `str` nor an `os.PathLike[str]`.
    """
    return max((len(run) for run in _read_words(path)), default=0)


def count_words(path: str | os.PathLike[str]) -> int:
    """Count the words in one UTF-8 text file.

    A word is a run of one or more characters for which `str.isspace()` is
    false, and at least one character in the run is one for which
    `str.isalnum()` is true. A run with no letter or digit, such as `--`,
    `...`, `_`, or a lone U+FEFF, is not a word. Every character for which
    `str.isspace()` is true separates words, including Unicode white space
    such as U+3000. Line breaks are white space,
    so LF, CR LF, and CR give the same count. One byte order mark
    (U+FEFF) at the start of the file is ignored. A U+FEFF anywhere else is
    part of the run it is in.

    Args:
        path: The path of the file to count, absolute or relative to the
            current working directory. It names one existing, readable,
            regular file whose content is valid UTF-8. `bytes` paths are not
            accepted.

    Returns:
        The number of words in the file, 0 or more. A file that is empty,
        holds only white space, or holds only runs without a letter or digit
        returns 0.

    Raises:
        FileNotFoundError: No file exists at `path`, or `path` is empty.
        IsADirectoryError: `path` names a folder (Linux).
        PermissionError: `path` names a folder (Windows), or the process may
            not read the file.
        UnicodeDecodeError: The file content is not valid UTF-8.
        TypeError: `path` is neither a `str` nor an `os.PathLike[str]`.
    """
    return len(_read_words(path))


def _read_words(path: str | os.PathLike[str]) -> list[str]:
    """Read one UTF-8 text file and return its words.

    Args:
        path: The path of the file to read, as for `count_words`.

    Returns:
        The words of the file in order, each a run of characters for which
        `str.isspace()` is false and `str.isalnum()` is true for at least one.
        One byte order mark (U+FEFF) at the start of the file is removed.

    Raises:
        FileNotFoundError: No file exists at `path`, or `path` is empty.
        IsADirectoryError: `path` names a folder (Linux).
        PermissionError: `path` names a folder (Windows), or the process may
            not read the file.
        UnicodeDecodeError: The file content is not valid UTF-8.
        TypeError: `path` is neither a `str` nor an `os.PathLike[str]`.
    """
    text_path = _checked_path(path)
    if text_path == "":
        # Path("") becomes Path("."), the current folder; an empty path names no file.
        raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), text_path)
    with Path(text_path).open(encoding="utf-8-sig") as handle:
        return [run for run in handle.read().split() if _has_letter_or_digit(run)]


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
        msg = f"path must be str or os.PathLike, not {type(path).__name__}"
        raise TypeError(msg)
    text_path = os.fspath(path)
    if not isinstance(text_path, str):
        raise TypeError("path must be str or os.PathLike[str], not bytes")
    return text_path


def _has_letter_or_digit(run: str) -> bool:
    """Tell whether a run of non-white-space characters is a word.

    Args:
        run: A run of one or more characters for which `str.isspace()` is false.

    Returns:
        True if at least one character of `run` has `str.isalnum()` true.
    """
    return any(char.isalnum() for char in run)
