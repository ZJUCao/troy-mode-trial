"""Tests for F06: the library function `count_chars`."""

import gc
import os
import pathlib
import sys
import warnings

import pytest

import troy_mode_trial
from troy_mode_trial import count_chars, count_lines, count_words

NOTES = b"Hello world\n  troy-mode  trial\n"
BOM = b"\xef\xbb\xbf"
WINDOWS = BOM + b"Hello world\r\n  troy-mode  trial\r\n"
HELLO = "你好\r\n".encode()
LATIN1 = "café au lait\n".encode("latin-1")


def _write(directory: pathlib.Path, name: str, data: bytes) -> pathlib.Path:
    """Write a file in binary mode.

    Args:
        directory: The folder that receives the file.
        name: The file name.
        data: The exact bytes of the file.

    Returns:
        The path of the new file.
    """
    path = directory / name
    path.write_bytes(data)
    return path


class _PathLike:
    """A path-like object whose `__fspath__` returns a fixed value."""

    def __init__(self, value: object) -> None:
        """Store the value that `__fspath__` returns.

        Args:
            value: What `__fspath__` returns.
        """
        self._value = value

    def __fspath__(self) -> str:
        """Return the stored value.

        Returns:
            The stored value, as a `str` for the type checker.
        """
        return self._value  # type: ignore[return-value]


def test_f06_t01_design_example(tmp_path: pathlib.Path) -> None:
    """Every character of the decoded text, line ends included."""
    path = _write(tmp_path, "notes.txt", NOTES)
    result = count_chars(str(path))
    assert result == 31
    assert type(result) is int


def test_f06_t02_line_ends_count_as_held(tmp_path: pathlib.Path) -> None:
    """LF is 1, CR is 1, and CR LF is 2, with no translation."""
    cases = [
        (b"\n", 1),
        (b"\r", 1),
        (b"\r\n", 2),
        (b"\r\r\n\n", 4),
        (b"one\rtwo\r\nthree\nfour", 19),
        (WINDOWS, 33),
    ]
    for index, (data, expected) in enumerate(cases):
        path = _write(tmp_path, f"f{index}.txt", data)
        assert count_chars(path) == expected


def test_f06_t03_character_is_code_point(tmp_path: pathlib.Path) -> None:
    """A character is one code point, not one byte."""
    cases = [
        (HELLO, 4),
        ("日本語".encode(), 3),
        ("\xe9".encode(), 1),
        ("\U0001f600".encode(), 1),
        ("a\U0001f600b你c".encode(), 5),
    ]
    for index, (data, expected) in enumerate(cases):
        path = _write(tmp_path, f"f{index}.txt", data)
        assert count_chars(path) == expected


def test_f06_t04_every_code_point_counts(tmp_path: pathlib.Path) -> None:
    """Every code point counts once, and combined characters count for each part."""
    cases = [
        ("é".encode(), 2),
        ("\U0001f468‍\U0001f469‍\U0001f467".encode(), 5),
        ("a\tb　c\x00d\x0ce\x85f g".encode(), 13),
    ]
    for index, (data, expected) in enumerate(cases):
        path = _write(tmp_path, f"f{index}.txt", data)
        assert count_chars(path) == expected


def test_f06_t05_empty_and_bom_only(tmp_path: pathlib.Path) -> None:
    """An empty file and a file with only the byte order mark have 0 characters."""
    assert count_chars(_write(tmp_path, "empty.txt", b"")) == 0
    assert count_chars(_write(tmp_path, "bom.txt", BOM)) == 0


def test_f06_t06_only_one_bom_removed(tmp_path: pathlib.Path) -> None:
    """Only one byte order mark at the very start is removed."""
    cases = [
        (BOM + b"x", 1),
        (BOM + BOM + b"a", 2),
        (BOM + BOM, 1),
        ("a﻿".encode(), 2),
        ("a﻿b".encode(), 3),
    ]
    for index, (data, expected) in enumerate(cases):
        path = _write(tmp_path, f"f{index}.txt", data)
        assert count_chars(path) == expected


def test_f06_t07_large_file(tmp_path: pathlib.Path) -> None:
    """The count stays right in a file larger than any internal read."""
    data = BOM + b"abcde\r\n" * 100_000 + "你\r".encode() * 100_000 + b"z" * 100_000
    assert len(data) == 1_200_003
    path = _write(tmp_path, "large.txt", data)
    assert count_chars(path) == 1_000_000


def test_f06_t08_path_forms(tmp_path: pathlib.Path) -> None:
    """Each accepted form of the path gives the same count."""
    path = _write(tmp_path, "notes.txt", NOTES)
    assert count_chars(str(path.resolve())) == 31
    assert count_chars(path.resolve()) == 31
    assert count_chars(_PathLike(str(path.resolve()))) == 31  # type: ignore[arg-type]


def test_f06_t09_relative_path(tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """A relative path is resolved against the working directory."""
    _write(tmp_path, "hello.txt", HELLO)
    monkeypatch.chdir(tmp_path)
    assert count_chars("hello.txt") == 4
    assert count_chars(pathlib.Path("hello.txt")) == 4


def test_f06_t10_missing_file(tmp_path: pathlib.Path) -> None:
    """A missing file, or the empty string, raises `FileNotFoundError`."""
    missing = tmp_path / "missing.txt"
    with pytest.raises(FileNotFoundError):
        count_chars(str(missing))
    with pytest.raises(FileNotFoundError):
        count_chars(missing)
    with pytest.raises(FileNotFoundError):
        count_chars("")


def test_f06_t11_folder(tmp_path: pathlib.Path) -> None:
    """A path that names a folder raises Python's own exception."""
    expected: type[OSError] | tuple[type[OSError], ...] = (
        (IsADirectoryError, PermissionError) if sys.platform == "win32" else IsADirectoryError
    )
    with pytest.raises(expected):
        count_chars(str(tmp_path))
    with pytest.raises(expected):
        count_chars(tmp_path)


@pytest.mark.skipif(sys.platform == "win32", reason="a portable test cannot remove read rights")
def test_f06_t12_unreadable_file(tmp_path: pathlib.Path) -> None:
    """A file the process may not read raises `PermissionError`."""
    if hasattr(os, "geteuid") and os.geteuid() == 0:
        pytest.skip("root can read the file anyway")
    path = _write(tmp_path, "secret.txt", b"one two")
    path.chmod(0o000)
    try:
        with pytest.raises(PermissionError):
            count_chars(path)
    finally:
        path.chmod(0o600)


def test_f06_t13_invalid_utf8(tmp_path: pathlib.Path) -> None:
    """Content that is not valid UTF-8 raises `UnicodeDecodeError` wherever it is."""
    cases = [
        LATIN1,
        b"a" * 100_000 + b"\xff",
        b"ok\nfine\n" + b"\xe6\x97",
        "hello\n".encode("utf-16"),
    ]
    for index, data in enumerate(cases):
        path = _write(tmp_path, f"f{index}.txt", data)
        with pytest.raises(UnicodeDecodeError):
            count_chars(path)


def test_f06_t14_other_path_types(tmp_path: pathlib.Path) -> None:
    """A path of any other type raises `TypeError`."""
    _write(tmp_path, "notes.txt", NOTES)
    data = _write(tmp_path, "data.txt", b"one two")
    with pytest.raises(TypeError):
        count_chars(b"notes.txt")  # type: ignore[arg-type]
    with data.open("rb") as handle, pytest.raises(TypeError):
        count_chars(handle.fileno())  # type: ignore[arg-type]
    with pytest.raises(TypeError):
        count_chars(None)  # type: ignore[arg-type]
    with pytest.raises(TypeError):
        count_chars(3.5)  # type: ignore[arg-type]
    with pytest.raises(TypeError):
        count_chars(_PathLike(b"notes.txt"))  # type: ignore[arg-type]


def test_f06_t15_closes_the_file(tmp_path: pathlib.Path) -> None:
    """The function closes the file before it returns and before it raises."""
    good = _write(tmp_path, "notes.txt", NOTES)
    bad = _write(tmp_path, "latin1.txt", LATIN1)
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always", ResourceWarning)
        assert count_chars(good) == 31
        with pytest.raises(UnicodeDecodeError):
            count_chars(bad)
        gc.collect()
    assert [w for w in caught if issubclass(w.category, ResourceWarning)] == []
    good.rename(tmp_path / "notes-renamed.txt")
    bad.rename(tmp_path / "latin1-renamed.txt")


def test_f06_t16_writes_nothing(tmp_path: pathlib.Path) -> None:
    """The function writes and stores nothing."""
    path = _write(tmp_path, "windows.txt", WINDOWS)
    before = (path.read_bytes(), path.stat().st_mtime_ns, sorted(tmp_path.iterdir()))
    assert count_chars(path) == 33
    assert count_chars(path) == 33
    after = (path.read_bytes(), path.stat().st_mtime_ns, sorted(tmp_path.iterdir()))
    assert after == before


def test_f06_t17_exports_with_siblings(tmp_path: pathlib.Path) -> None:
    """The package exports the three counting functions, which count one file."""
    path = _write(tmp_path, "windows.txt", WINDOWS)
    assert count_chars(path) == 33
    assert count_words(path) == 4
    assert count_lines(path) == 2
    for name in ("count_chars", "count_lines", "count_words"):
        assert name in troy_mode_trial.__all__
