"""Tests for F07: the function `count_longest`."""

import gc
import os
import pathlib
import sys
import warnings

import pytest

import troy_mode_trial
from troy_mode_trial import count_chars, count_lines, count_longest, count_words

BOM = bytes.fromhex("EF BB BF")
NOTES = b"Hello world\n  troy-mode  trial\n"
WINDOWS = BOM + b"Hello world\r\n  troy-mode  trial\r\n"
GREETING = "你好 世界!\r\n".encode()
DASHES = b"-- ...\n"
LATIN1 = "caf\xe9 au lait\n".encode("latin-1")


@pytest.fixture
def work(tmp_path: pathlib.Path) -> pathlib.Path:
    """Make `tmp_path` hold the standard files.

    Args:
        tmp_path: pytest's temporary folder.

    Returns:
        The folder.
    """
    (tmp_path / "notes.txt").write_bytes(NOTES)
    (tmp_path / "windows.txt").write_bytes(WINDOWS)
    (tmp_path / "greeting.txt").write_bytes(GREETING)
    (tmp_path / "dashes.txt").write_bytes(DASHES)
    (tmp_path / "latin1.txt").write_bytes(LATIN1)
    (tmp_path / "sub").mkdir()
    return tmp_path


def _longest_of(work: pathlib.Path, contents: list[str | bytes]) -> list[int]:
    """Write each content to its own file and count its longest word.

    Args:
        work: The folder for the files.
        contents: The text of each file, encoded as UTF-8, or its exact bytes.

    Returns:
        The result of `count_longest` for each file, as a `pathlib.Path`.
    """
    results = []
    for index, content in enumerate(contents):
        path = work / f"case{index}.txt"
        path.write_bytes(content if isinstance(content, bytes) else content.encode())
        results.append(count_longest(path))
    return results


def test_f07_t01_design_example(work: pathlib.Path) -> None:
    """The length of the longest word, in characters."""
    result = count_longest(str(work / "notes.txt"))
    assert result == 9
    assert type(result) is int


def test_f07_t02_word_with_punctuation(work: pathlib.Path) -> None:
    """The whole run that F03 counts is the word, punctuation included."""
    contents: list[str | bytes] = [
        "don't, he said.",
        "----a ......",
        "x--y",
        "see https://example.com/a now",
        "3.14",
        "____ b",
    ]
    assert _longest_of(work, contents) == [6, 5, 4, 21, 4, 1]


def test_f07_t03_run_without_letter_or_digit(work: pathlib.Path) -> None:
    """A run with no letter or digit is not a word, however long it is."""
    contents: list[str | bytes] = [
        DASHES,
        "ab ------------",
        "!!!!!!!!!! a",
        "\U0001f600\U0001f600 !!",
    ]
    assert _longest_of(work, contents) == [0, 2, 1, 0]


def test_f07_t04_white_space_separates(work: pathlib.Path) -> None:
    """Every `str.isspace()` character separates words, and nothing else does."""
    contents: list[str | bytes] = [
        "a\tbb\rccc\r\ndd",
        "x　yy",
        "a\x0bbb\x0cccc\x85dddd\xa0e",
        "a\u200bb",
    ]
    assert _longest_of(work, contents) == [3, 2, 4, 3]


def test_f07_t05_line_ends(work: pathlib.Path) -> None:
    """Windows and Linux line ends give the same result."""
    assert count_longest(work / "notes.txt") == 9
    assert count_longest(work / "windows.txt") == 9


def test_f07_t06_code_points(work: pathlib.Path) -> None:
    """The length counts code points, not bytes."""
    contents: list[str | bytes] = [
        GREETING,
        "日本語",
        "\U0001f600a",
        "é",
        "\xe9",
        "\U0001f468‍\U0001f469‍\U0001f467 a",
    ]
    assert _longest_of(work, contents) == [3, 3, 2, 2, 1, 1]


def test_f07_t07_no_word(work: pathlib.Path) -> None:
    """A file with no word returns 0."""
    assert _longest_of(work, [b"", BOM, b"  \r\n\t\n"]) == [0, 0, 0]


def test_f07_t08_byte_order_mark(work: pathlib.Path) -> None:
    """Only one byte order mark at the very start is removed."""
    contents: list[str | bytes] = [
        BOM + b"abc",
        BOM + BOM + b"abc",
        BOM + b"-- abcd",
        "ab﻿c",
        BOM + BOM,
    ]
    assert _longest_of(work, contents) == [3, 4, 4, 4, 0]


def test_f07_t09_position_and_ties(work: pathlib.Path) -> None:
    """The longest word is found wherever it stands."""
    contents: list[str | bytes] = ["abc xyz", "a bb ccc", "cccc bb a", "word"]
    assert _longest_of(work, contents) == [3, 3, 4, 4]


def test_f07_t10_large_file(work: pathlib.Path) -> None:
    """The result stays right in a large file."""
    unit = "你好世 ab\r\n".encode()
    assert len(unit) == 14
    data = BOM + unit * 150_000 + b"x" * 70_000 + b"\n" + b"-" * 100_000
    assert len(data) == 2_270_004
    path = work / "large.txt"
    path.write_bytes(data)
    assert count_longest(path) == 70_000


class _PathLike:
    """An object that implements `__fspath__` and returns a `str`."""

    def __init__(self, path: str) -> None:
        """Keep the path.

        Args:
            path: The path to return.
        """
        self._path = path

    def __fspath__(self) -> str:
        """Return the path.

        Returns:
            The path as a `str`.
        """
        return self._path


class _BytesPathLike:
    """An object whose `__fspath__` returns `bytes`."""

    def __fspath__(self) -> bytes:
        """Return a path as `bytes`.

        Returns:
            Some bytes.
        """
        return b"notes.txt"


def test_f07_t11_path_forms(work: pathlib.Path) -> None:
    """Each accepted form of `path` gives the same result."""
    absolute = str(work / "notes.txt")
    assert count_longest(absolute) == 9
    assert count_longest(pathlib.Path(absolute)) == 9
    assert count_longest(_PathLike(absolute)) == 9


def test_f07_t12_relative_path(work: pathlib.Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """A relative path is resolved against the current working directory."""
    monkeypatch.chdir(work)
    assert count_longest("greeting.txt") == 3
    assert count_longest(pathlib.Path("greeting.txt")) == 3


def test_f07_t13_missing_file(work: pathlib.Path) -> None:
    """A missing file, or the empty string, raises `FileNotFoundError`."""
    missing = work / "missing.txt"
    with pytest.raises(FileNotFoundError):
        count_longest(str(missing))
    with pytest.raises(FileNotFoundError):
        count_longest(missing)
    with pytest.raises(FileNotFoundError):
        count_longest("")


def test_f07_t14_folder(work: pathlib.Path) -> None:
    """A path that names a folder raises Python's own exception."""
    expected: type[OSError] | tuple[type[OSError], ...] = (
        (IsADirectoryError, PermissionError) if sys.platform == "win32" else IsADirectoryError
    )
    with pytest.raises(expected):
        count_longest(str(work))
    with pytest.raises(expected):
        count_longest(work)


@pytest.mark.skipif(
    sys.platform == "win32", reason="a test cannot remove its read right on Windows"
)
@pytest.mark.skipif(
    sys.platform != "win32" and os.geteuid() == 0, reason="root can read the file anyway"
)
def test_f07_t15_permission_denied(work: pathlib.Path) -> None:
    """A file the process may not read raises `PermissionError`."""
    secret = work / "secret.txt"
    secret.write_bytes(b"one two")
    secret.chmod(0o000)
    try:
        with pytest.raises(PermissionError):
            count_longest(secret)
    finally:
        secret.chmod(0o600)


def test_f07_t16_not_valid_utf8(work: pathlib.Path) -> None:
    """Content that is not valid UTF-8 raises `UnicodeDecodeError`."""
    (work / "long.txt").write_bytes(b"a" * 100_000 + b"\xff")
    (work / "cut.txt").write_bytes(b"ok fine\n" + bytes.fromhex("E6 97"))
    (work / "utf16.txt").write_bytes("hello\n".encode("utf-16"))
    for name in ("latin1.txt", "long.txt", "cut.txt", "utf16.txt"):
        with pytest.raises(UnicodeDecodeError):
            count_longest(work / name)


def test_f07_t17_other_types(work: pathlib.Path) -> None:
    """A `path` of any other type raises `TypeError`."""
    (work / "two.txt").write_bytes(b"one two")
    with (work / "two.txt").open("rb") as handle:
        descriptor = handle.fileno()
        with pytest.raises(TypeError):
            count_longest(descriptor)  # type: ignore[arg-type]
    for value in (b"notes.txt", None, 3.5, _BytesPathLike()):
        with pytest.raises(TypeError):
            count_longest(value)  # type: ignore[arg-type]


def _entries(directory: pathlib.Path) -> set[str]:
    """List the entry names of a folder.

    Args:
        directory: The folder.

    Returns:
        The names.
    """
    return {path.name for path in directory.iterdir()}


def test_f07_t18_closes_and_writes_nothing(work: pathlib.Path) -> None:
    """The function closes the file before it returns or raises, and writes nothing."""
    windows = work / "windows.txt"
    latin1 = work / "latin1.txt"
    stat_before = windows.stat().st_mtime_ns
    bytes_before = windows.read_bytes()
    entries_before = _entries(work)
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always", ResourceWarning)
        assert count_longest(windows) == 9
        assert count_longest(windows) == 9
        with pytest.raises(UnicodeDecodeError):
            count_longest(latin1)
        gc.collect()
        assert windows.read_bytes() == bytes_before
        assert windows.stat().st_mtime_ns == stat_before
        assert _entries(work) == entries_before
        assert not [item for item in caught if issubclass(item.category, ResourceWarning)]
        windows.rename(work / "windows-renamed.txt")
        latin1.rename(work / "latin1-renamed.txt")


def test_f07_t19_export_and_word_rule(work: pathlib.Path) -> None:
    """The package exports `count_longest`, which agrees with `count_words` on words."""
    notes = work / "notes.txt"
    assert count_longest(notes) == 9
    assert count_words(notes) == 4
    assert count_chars(notes) == 31
    assert count_lines(notes) == 2
    for name in ("count_chars", "count_lines", "count_longest", "count_words"):
        assert name in troy_mode_trial.__all__
    contents: list[str | bytes] = [
        b"",
        BOM,
        DASHES,
        "\U0001f600 !!",
        "x",
        "don't, he said.",
        GREETING,
    ]
    longest = _longest_of(work, contents)
    assert longest == [0, 0, 0, 0, 1, 6, 3]
    words = [count_words(work / f"case{index}.txt") for index in range(len(contents))]
    assert words[:4] == [0, 0, 0, 0]
    assert all(count > 0 for count in words[4:])
