"""Tests for F03: `count_words` counts only runs that hold a letter or digit."""

import pathlib

import pytest

from troy_mode_trial import count_words


def _count_bytes(directory: pathlib.Path, name: str, data: bytes) -> int:
    """Write raw bytes to a new file and count its words.

    Args:
        directory: The folder that receives the file.
        name: The file name.
        data: The bytes to write.

    Returns:
        The result of `count_words` for the file.
    """
    path = directory / name
    path.write_bytes(data)
    return count_words(str(path))


def _count(directory: pathlib.Path, name: str, text: str) -> int:
    """Write text as UTF-8 bytes to a new file and count its words.

    Args:
        directory: The folder that receives the file.
        name: The file name.
        text: The text to write, encoded as UTF-8.

    Returns:
        The result of `count_words` for the file.
    """
    return _count_bytes(directory, name, text.encode("utf-8"))


def test_f03_t01_design_example(tmp_path: pathlib.Path) -> None:
    """Runs without a letter or digit do not count; the others count once."""
    result = _count(tmp_path, "dashes.txt", "Wait -- what ... don't x--y 3.14 _")
    assert result == 5
    assert type(result) is int


def test_f03_t02_only_symbols_is_zero(tmp_path: pathlib.Path) -> None:
    """A file with only runs without a letter or digit returns 0."""
    assert _count(tmp_path, "only-symbols.txt", "-- ... !!!") == 0


@pytest.mark.parametrize("text", ["--", "...", "_", "!@#$%^&*()", "\"'", "+-*/=<>"])
def test_f03_t03_ascii_punctuation_run_is_not_a_word(tmp_path: pathlib.Path, text: str) -> None:
    """One run of ASCII punctuation or symbols is not a word."""
    assert _count(tmp_path, "w.txt", text) == 0


def test_f03_t04_symbol_runs_across_white_space(tmp_path: pathlib.Path) -> None:
    """Symbol runs between several kinds of white space give 0."""
    assert _count(tmp_path, "w.txt", "--\r\n...\n\t_ \v!!!\f") == 0


def test_f03_t05_letter_or_digit_anywhere_counts_once(tmp_path: pathlib.Path) -> None:
    """A run with one letter or digit counts once, wherever it stands."""
    assert _count(tmp_path, "w.txt", "don't x--y 3.14 --a-- !1! _x --") == 6


def test_f03_t06_non_ascii_words_and_emoji(tmp_path: pathlib.Path) -> None:
    """Non-ASCII words count once each, and an emoji alone is not a word."""
    text = (
        "caf\u00e9 na\u00efve \u65e5\u672c\u8a9e \U0001f600 "
        "\u0395\u03bb\u03bb\u03b7\u03bd\u03b9\u03ba\u03ac"
    )
    assert _count(tmp_path, "w.txt", text) == 4


def test_f03_t07_unicode_symbol_runs_are_not_words(tmp_path: pathlib.Path) -> None:
    """Unicode symbols and punctuation without a letter or digit do not count."""
    text = "\U0001f600 \u2014 \u00ab\u00bb \u20ac \u00a9 \u2192 \u3002\u3001 \u2026"
    assert _count(tmp_path, "w.txt", text) == 0


def test_f03_t08_isalnum_numerals_count(tmp_path: pathlib.Path) -> None:
    """Words with a character for which `str.isalnum()` is true count."""
    text = "\u00b2 \u00bd \u216b \u0663 \u00df -- \u2026"
    assert _count(tmp_path, "w.txt", text) == 5


@pytest.mark.parametrize(
    ("data", "expected"),
    [
        ("a \ufeff b".encode(), 2),
        (b"\xef\xbb\xbf\xef\xbb\xbf", 0),
        ("a\ufeffb \ufeff".encode(), 1),
    ],
    ids=["lone-mark-between", "two-leading-marks", "joined-and-lone"],
)
def test_f03_t09_inner_bom_is_not_white_space(
    tmp_path: pathlib.Path, data: bytes, expected: int
) -> None:
    """A U+FEFF after the first character is not white space and not a letter."""
    assert _count_bytes(tmp_path, "w.txt", data) == expected


def test_f03_t10_large_file(tmp_path: pathlib.Path) -> None:
    """The count stays right in a file larger than 1 MiB."""
    text = (
        "-" * 100_000
        + "x"
        + " "
        + "." * 100_000
        + "\n"
        + "7"
        + "_" * 100_000
        + " "
        + "ab -- " * 200_000
    )
    assert len(text.encode("utf-8")) > 1024 * 1024
    assert _count(tmp_path, "big.txt", text) == 200_002
