"""Tests for F01 `count_words`, one test per case of the F01 test plan."""

import contextlib
import gc
import os
import pathlib
import sys
import warnings

import pytest

from troy_mode_trial import count_words

BOM = b"\xef\xbb\xbf"


def _write(directory: pathlib.Path, name: str, data: bytes) -> pathlib.Path:
    """Write exact bytes to a new file.

    Args:
        directory: The folder that receives the file.
        name: The file name.
        data: The exact bytes to write.

    Returns:
        The path of the new file.
    """
    path = directory / name
    path.write_bytes(data)
    return path


def _utf8(text: str) -> bytes:
    """Encode text as UTF-8.

    Args:
        text: The text to encode.

    Returns:
        The UTF-8 bytes.
    """
    return text.encode("utf-8")


class _FsPath:
    """A minimal object that implements `__fspath__` and returns a value as given."""

    def __init__(self, value: str | bytes) -> None:
        """Keep the value that `__fspath__` returns.

        Args:
            value: The value to return from `__fspath__`.
        """
        self._value = value

    def __fspath__(self) -> str | bytes:
        """Return the stored value.

        Returns:
            The value given to the constructor.
        """
        return self._value


def test_f01_t01_design_example(tmp_path: pathlib.Path) -> None:
    """Count the design's example and check the result type."""
    path = _write(tmp_path, "notes.txt", _utf8("Hello world\n  troy-mode  trial"))
    result = count_words(str(path))
    assert result == 4
    assert type(result) is int


def test_f01_t02_empty_file(tmp_path: pathlib.Path) -> None:
    """An empty file has no words."""
    assert count_words(_write(tmp_path, "e.txt", b"")) == 0


@pytest.mark.parametrize("data", [b"   ", b"\n", b"\t \r\n \x0b\x0c\r"])
def test_f01_t03_white_space_only(tmp_path: pathlib.Path, data: bytes) -> None:
    """A file of white space only has no words."""
    assert count_words(_write(tmp_path, "w.txt", data)) == 0


@pytest.mark.parametrize("text", ["a", "troy-mode", "x=1,y=2;"])
def test_f01_t04_single_run_is_one_word(tmp_path: pathlib.Path, text: str) -> None:
    """One run without white space is one word."""
    assert count_words(_write(tmp_path, "w.txt", _utf8(text))) == 1


def test_f01_t05_ascii_white_space_separates(tmp_path: pathlib.Path) -> None:
    """Each ASCII white space character separates words."""
    data = _utf8("\tone  two\t\tthree\x0bfour\x0cfive \n six  ")
    assert count_words(_write(tmp_path, "w.txt", data)) == 6


def test_f01_t06_unicode_white_space_separates(tmp_path: pathlib.Path) -> None:
    """Unicode white space separates words."""
    text = "\u7532\u3000\u4e59\u00a0\u4e19\u2003\u4e01\u2028\u620a\u0085\u5df1"
    assert count_words(_write(tmp_path, "w.txt", _utf8(text))) == 6


def test_f01_t07_non_space_blank_characters_join(tmp_path: pathlib.Path) -> None:
    """Zero width space and word joiner do not separate words."""
    data = _utf8("a\u200bb c\u2060d")
    assert count_words(_write(tmp_path, "w.txt", data)) == 2


@pytest.mark.parametrize(
    "text",
    [
        "one two\nthree\nfour",
        "one two\r\nthree\r\nfour",
        "one two\rthree\rfour",
        "one two three four\r\n",
    ],
)
def test_f01_t08_line_breaks_agree(tmp_path: pathlib.Path, text: str) -> None:
    """LF, CR LF, and CR give the same count."""
    assert count_words(_write(tmp_path, "w.txt", _utf8(text))) == 4


def test_f01_t09_non_ascii_words(tmp_path: pathlib.Path) -> None:
    """Words with multi-byte characters each count once."""
    text = (
        "caf\u00e9 na\u00efve \u65e5\u672c\u8a9e \U0001f600 "
        "\u0395\u03bb\u03bb\u03b7\u03bd\u03b9\u03ba\u03ac"
    )
    assert count_words(_write(tmp_path, "w.txt", _utf8(text))) == 5


@pytest.mark.parametrize(
    ("data", "expected"),
    [
        (BOM + b"one two", 2),
        (BOM, 0),
        (BOM + b" word", 1),
        (BOM + b"\n", 0),
    ],
)
def test_f01_t10_leading_bom_ignored(tmp_path: pathlib.Path, data: bytes, expected: int) -> None:
    """One byte order mark at the start is ignored."""
    assert count_words(_write(tmp_path, "w.txt", data)) == expected


@pytest.mark.parametrize(
    ("text", "expected"),
    [("a \ufeff b", 3), ("a\ufeffb", 1), ("\ufeff\ufeff", 1)],
)
def test_f01_t11_inner_bom_is_word_part(tmp_path: pathlib.Path, text: str, expected: int) -> None:
    """A U+FEFF that is not the first character is part of a word."""
    assert count_words(_write(tmp_path, "w.txt", _utf8(text))) == expected


def test_f01_t12_large_file(tmp_path: pathlib.Path) -> None:
    """The count stays right in a file larger than 1 MiB."""
    parts = ["word" + ("\n" if i % 1000 == 0 else " ") for i in range(1, 200_001)]
    parts.append("x" * 100_000)
    parts.append("\u3000end")
    path = _write(tmp_path, "big.txt", _utf8("".join(parts)))
    assert path.stat().st_size > 1024 * 1024
    assert count_words(path) == 200_002


def test_f01_t13_accepted_path_forms(tmp_path: pathlib.Path) -> None:
    """A str, a Path, and a PathLike give the same count."""
    path = _write(tmp_path, "w.txt", b"one two three")
    assert count_words(str(path)) == 3
    assert count_words(path) == 3
    assert count_words(_FsPath(str(path))) == 3


def test_f01_t14_relative_path(tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """A relative path is resolved against the working directory."""
    _write(tmp_path, "words.txt", b"alpha beta")
    monkeypatch.chdir(tmp_path)
    assert count_words("words.txt") == 2
    assert count_words(pathlib.Path("words.txt")) == 2


def test_f01_t15_missing_file(tmp_path: pathlib.Path) -> None:
    """A missing file raises FileNotFoundError."""
    missing = tmp_path / "missing.txt"
    with pytest.raises(FileNotFoundError):
        count_words(str(missing))
    with pytest.raises(FileNotFoundError):
        count_words(missing)


def test_f01_t16_folder(tmp_path: pathlib.Path) -> None:
    """A folder raises IsADirectoryError or PermissionError."""
    with pytest.raises((IsADirectoryError, PermissionError)) as info:
        count_words(str(tmp_path))
    if sys.platform != "win32":
        assert isinstance(info.value, IsADirectoryError)


@pytest.mark.skipif(sys.platform == "win32", reason="Cannot remove read right portably on Windows")
def test_f01_t17_unreadable_file(tmp_path: pathlib.Path) -> None:
    """A file the process may not read raises PermissionError."""
    if hasattr(os, "geteuid") and os.geteuid() == 0:
        pytest.skip("root can read the file anyway")
    path = _write(tmp_path, "locked.txt", b"one two")
    path.chmod(0o000)
    try:
        with pytest.raises(PermissionError):
            count_words(path)
    finally:
        path.chmod(0o600)


@pytest.mark.parametrize(
    "data",
    [b"caf\xe9", b"ok \xe6\x97", "hello".encode("utf-16")],
    ids=["latin1", "cut-off", "utf16"],
)
def test_f01_t18_invalid_utf8(tmp_path: pathlib.Path, data: bytes) -> None:
    """Content that is not valid UTF-8 raises UnicodeDecodeError."""
    with pytest.raises(UnicodeDecodeError):
        count_words(_write(tmp_path, "bad.txt", data))


def test_f01_t19_wrong_path_types(tmp_path: pathlib.Path) -> None:
    """A path of any other type raises TypeError."""
    path = _write(tmp_path, "words.txt", b"one two")
    fd = os.open(path, os.O_RDONLY)
    try:
        for bad in (b"words.txt", fd, None, 3.5, _FsPath(b"words.txt")):
            with pytest.raises(TypeError):
                count_words(bad)  # type: ignore[arg-type]
    finally:
        with contextlib.suppress(OSError):
            os.close(fd)


def test_f01_t20_file_is_closed(tmp_path: pathlib.Path) -> None:
    """The file is closed before the function returns and before it raises."""
    good = _write(tmp_path, "good.txt", b"one two")
    bad = _write(tmp_path, "bad.txt", b"caf\xe9")
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always", ResourceWarning)
        count_words(good)
        with pytest.raises(UnicodeDecodeError):
            count_words(bad)
        gc.collect()
    assert not [w for w in caught if issubclass(w.category, ResourceWarning)]
    good.rename(tmp_path / "good2.txt")
    bad.rename(tmp_path / "bad2.txt")


def test_f01_t21_no_side_effects(tmp_path: pathlib.Path) -> None:
    """The function writes and stores nothing."""
    path = _write(tmp_path, "w.txt", b"one two")
    before = _snapshot(path)
    assert count_words(path) == 2
    assert count_words(path) == 2
    assert before == _snapshot(path)


def _snapshot(path: pathlib.Path) -> tuple[bytes, int, list[str]]:
    """Capture a file's content, modification time, and its folder's entries.

    Args:
        path: The file to capture.

    Returns:
        The bytes, the modification time in nanoseconds, and the sorted names in the folder.
    """
    return (
        path.read_bytes(),
        path.stat().st_mtime_ns,
        sorted(p.name for p in path.parent.iterdir()),
    )
