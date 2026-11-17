"""Tests for F02 `count_lines`, one test per case of the F02 test plan."""

import contextlib
import gc
import os
import pathlib
import sys
import warnings

import pytest

import troy_mode_trial
from troy_mode_trial import count_lines, count_words

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


class _PathLike:
    """A test class that implements `__fspath__` and returns the given value."""

    def __init__(self, value: str | bytes) -> None:
        """Store the value that `__fspath__` returns.

        Args:
            value: The value to return from `__fspath__`.
        """
        self._value = value

    def __fspath__(self) -> str | bytes:
        """Return the stored value.

        Returns:
            The stored value.
        """
        return self._value


def test_f02_t01_design_example_counts_two_lines(tmp_path: pathlib.Path) -> None:
    """F02-T01: design example counts two lines."""
    path = _write(tmp_path, "notes.txt", _utf8("Hello world\n  troy-mode  trial"))
    result = count_lines(str(path))
    assert result == 2
    assert type(result) is int


def test_f02_t02_crlf_ends_one_line(tmp_path: pathlib.Path) -> None:
    """F02-T02: crlf ends one line."""
    first = _write(tmp_path, "windows.txt", _utf8("Hello world\r\n  troy-mode  trial"))
    second = _write(tmp_path, "windows2.txt", _utf8("Hello world\r\n  troy-mode  trial\r\n"))
    assert count_lines(first) == 2
    assert count_lines(second) == 2


@pytest.mark.parametrize("data", [b"", BOM])
def test_f02_t03_empty_and_bom_only_have_no_lines(tmp_path: pathlib.Path, data: bytes) -> None:
    """F02-T03: empty and bom only have no lines."""
    assert count_lines(_write(tmp_path, "case.txt", data)) == 0


@pytest.mark.parametrize("data", [b"\n", b"\r\n", b"\r"])
def test_f02_t04_one_line_break_is_one_line(tmp_path: pathlib.Path, data: bytes) -> None:
    """F02-T04: one line break is one line."""
    assert count_lines(_write(tmp_path, "case.txt", data)) == 1


@pytest.mark.parametrize(
    ("data", "expected"),
    [(b"a", 1), (b"a\n", 1), (b"a\nb", 2), (b"a\nb\n", 2)],
)
def test_f02_t05_last_line_without_break_counts(
    tmp_path: pathlib.Path, data: bytes, expected: int
) -> None:
    """F02-T05: last line without break counts."""
    assert count_lines(_write(tmp_path, "case.txt", data)) == expected


@pytest.mark.parametrize(
    ("data", "expected"),
    [(b"first\n\nthird\n", 3), (b"\n\n\n", 3), (b"\r\n\r\n", 2)],
)
def test_f02_t06_empty_line_counts(tmp_path: pathlib.Path, data: bytes, expected: int) -> None:
    """F02-T06: empty line counts."""
    assert count_lines(_write(tmp_path, "case.txt", data)) == expected


def test_f02_t07_all_three_breaks_in_one_file(tmp_path: pathlib.Path) -> None:
    """F02-T07: all three breaks in one file."""
    path = _write(tmp_path, "mixed.txt", b"one\rtwo\r\nthree\nfour")
    assert count_lines(path) == 4


@pytest.mark.parametrize(
    ("data", "expected"),
    [(b"\r\r\n", 2), (b"\n\r", 2), (b"\r\r", 2), (b"\r\n\n", 2), (b"a\r\rb", 3)],
)
def test_f02_t08_only_cr_followed_by_lf_joins(
    tmp_path: pathlib.Path, data: bytes, expected: int
) -> None:
    """F02-T08: only cr followed by lf joins."""
    assert count_lines(_write(tmp_path, "case.txt", data)) == expected


def test_f02_t09_design_file_is_one_line(tmp_path: pathlib.Path) -> None:
    """F02-T09: the design's file with other splitlines characters is one line."""
    design_file = _write(tmp_path, "design.txt", _utf8("a\u2028b\fc\x85d"))
    assert count_lines(design_file) == 1


@pytest.mark.parametrize("char", ["\v", "\f", "\x1c", "\x1d", "\x1e", "\x85", "\u2028", "\u2029"])
def test_f02_t09_other_splitlines_characters_are_ordinary(
    tmp_path: pathlib.Path, char: str
) -> None:
    """F02-T09: other splitlines characters are ordinary."""
    assert count_lines(_write(tmp_path, "case.txt", _utf8(f"a{char}b"))) == 1


def test_f02_t09_last_line_with_separator_counts(tmp_path: pathlib.Path) -> None:
    """F02-T09: a last line that holds a separator counts."""
    last = _write(tmp_path, "last.txt", _utf8("a\u2028b\nc\u2029"))
    assert count_lines(last) == 2


@pytest.mark.parametrize(
    "data",
    [
        b"alpha\nbeta\n\ngamma",
        b"alpha\r\nbeta\r\n\r\ngamma",
        b"alpha\rbeta\r\rgamma",
    ],
)
def test_f02_t10_same_text_same_count_for_each_break(tmp_path: pathlib.Path, data: bytes) -> None:
    """F02-T10: same text same count for each break."""
    assert count_lines(_write(tmp_path, "case.txt", data)) == 4


@pytest.mark.parametrize(
    ("data", "expected"),
    [
        (BOM + b"one\ntwo", 2),
        (BOM + b"\n", 1),
        (BOM + b"x", 1),
        (BOM + BOM, 1),
        (b"a\n" + BOM, 2),
    ],
)
def test_f02_t11_one_leading_bom_is_ignored(
    tmp_path: pathlib.Path, data: bytes, expected: int
) -> None:
    """F02-T11: one leading bom is ignored."""
    assert count_lines(_write(tmp_path, "case.txt", data)) == expected


def test_f02_t12_large_file_with_split_line_breaks(tmp_path: pathlib.Path) -> None:
    """F02-T12: large file with split line breaks."""
    data = b"abcde\r\n" * 100_000 + b"x\r" * 100_000 + b"y\n" * 100_000 + b"z" * 100_000
    assert len(data) == 1_200_000
    assert count_lines(_write(tmp_path, "large.txt", data)) == 300_001


def test_f02_t13_each_accepted_path_form(tmp_path: pathlib.Path) -> None:
    """F02-T13: each accepted path form."""
    path = _write(tmp_path, "three.txt", b"a\nb\nc")
    assert count_lines(str(path.absolute())) == 3
    assert count_lines(path.absolute()) == 3
    assert count_lines(_PathLike(str(path.absolute()))) == 3  # type: ignore[arg-type]


def test_f02_t14_relative_path_uses_working_directory(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """F02-T14: relative path uses working directory."""
    _write(tmp_path, "lines.txt", b"alpha\nbeta")
    monkeypatch.chdir(tmp_path)
    assert count_lines("lines.txt") == 2
    assert count_lines(pathlib.Path("lines.txt")) == 2


def test_f02_t15_missing_file_or_empty_path(tmp_path: pathlib.Path) -> None:
    """F02-T15: missing file or empty path."""
    missing = tmp_path / "missing.txt"
    with pytest.raises(FileNotFoundError):
        count_lines(str(missing))
    with pytest.raises(FileNotFoundError):
        count_lines(missing)
    with pytest.raises(FileNotFoundError):
        count_lines("")


def test_f02_t16_folder_raises(tmp_path: pathlib.Path) -> None:
    """F02-T16: folder raises."""
    expected: tuple[type[OSError], ...] = (IsADirectoryError,)
    if sys.platform == "win32":
        expected = (IsADirectoryError, PermissionError)
    with pytest.raises(expected):
        count_lines(str(tmp_path))
    with pytest.raises(expected):
        count_lines(tmp_path)


@pytest.mark.skipif(sys.platform != "linux", reason="Linux only: mode 0o000 needs POSIX")
def test_f02_t17_unreadable_file_raises(tmp_path: pathlib.Path) -> None:
    """F02-T17: unreadable file raises."""
    if os.geteuid() == 0:
        pytest.skip("root can read the file anyway")
    path = _write(tmp_path, "locked.txt", b"one\ntwo")
    path.chmod(0o000)
    try:
        with pytest.raises(PermissionError):
            count_lines(path)
    finally:
        path.chmod(0o600)


@pytest.mark.parametrize(
    "data",
    [
        "café au lait\n".encode("latin-1"),
        b"ok\nfine\n\xe6\x97",
        "hello\n".encode("utf-16"),
    ],
    ids=["latin1", "cut-off", "utf16"],
)
def test_f02_t18_invalid_utf8_raises(tmp_path: pathlib.Path, data: bytes) -> None:
    """F02-T18: invalid utf8 raises."""
    with pytest.raises(UnicodeDecodeError):
        count_lines(_write(tmp_path, "bad.txt", data))


def test_f02_t19_other_path_types_raise_type_error(tmp_path: pathlib.Path) -> None:
    """F02-T19: other path types raise type error."""
    path = _write(tmp_path, "fd.txt", b"one\ntwo")
    descriptor = os.open(path, os.O_RDONLY)
    try:
        with pytest.raises(TypeError):
            count_lines(b"lines.txt")  # type: ignore[arg-type]
        with pytest.raises(TypeError):
            count_lines(descriptor)  # type: ignore[arg-type]
        with pytest.raises(TypeError):
            count_lines(None)  # type: ignore[arg-type]
        with pytest.raises(TypeError):
            count_lines(3.5)  # type: ignore[arg-type]
        with pytest.raises(TypeError):
            count_lines(_PathLike(b"lines.txt"))  # type: ignore[arg-type]
    finally:
        with contextlib.suppress(OSError):
            os.close(descriptor)


def test_f02_t20_file_is_closed_before_return_and_raise(tmp_path: pathlib.Path) -> None:
    """F02-T20: file is closed before return and raise."""
    good = _write(tmp_path, "good.txt", b"one\ntwo")
    bad = _write(tmp_path, "bad.txt", b"\xff\xfe\xfa")
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always", ResourceWarning)
        assert count_lines(good) == 2
        with pytest.raises(UnicodeDecodeError):
            count_lines(bad)
        gc.collect()
    assert [w for w in caught if issubclass(w.category, ResourceWarning)] == []
    good.rename(tmp_path / "good-renamed.txt")
    bad.rename(tmp_path / "bad-renamed.txt")


def test_f02_t21_function_writes_and_stores_nothing(tmp_path: pathlib.Path) -> None:
    """F02-T21: function writes and stores nothing."""
    path = _write(tmp_path, "data.txt", b"one\ntwo\r\n")
    data = path.read_bytes()
    mtime = path.stat().st_mtime_ns
    entries = sorted(entry.name for entry in tmp_path.iterdir())
    assert count_lines(path) == 2
    assert count_lines(path) == 2
    assert path.read_bytes() == data
    assert path.stat().st_mtime_ns == mtime
    assert sorted(entry.name for entry in tmp_path.iterdir()) == entries


def test_f02_t22_package_exports_both_functions(tmp_path: pathlib.Path) -> None:
    """F02-T22: package exports both functions."""
    path = _write(tmp_path, "both.txt", BOM + _utf8("Hello world\r\n  troy-mode  trial\r\n"))
    assert count_lines(path) == 2
    assert count_words(path) == 4
    assert "count_lines" in troy_mode_trial.__all__
    assert "count_words" in troy_mode_trial.__all__
