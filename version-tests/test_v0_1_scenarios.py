# ruff: noqa: S101
"""Version tests of v0.1, one test for each scenario of the v0.1 version test plan."""

import pathlib
import subprocess
import sys

import pytest

from troy_mode_trial import count_words

BOM = b"\xef\xbb\xbf"
MIXED_TEXT = "Wait -- what ... don't x--y 3.14 _\r\n日本語\u3000テキスト 😀\n"


def _write(directory: pathlib.Path, name: str, data: bytes) -> pathlib.Path:
    """Write exact bytes to a new file, so no line ending is changed.

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


def test_v0_1_s01_counts_words_of_a_file(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Scenario S01: the words of a file are counted and the result is an exact int."""
    _write(tmp_path, "notes.txt", b"Hello world\n  troy-mode  trial")
    monkeypatch.chdir(tmp_path)
    result = count_words("notes.txt")
    assert result == 4
    assert type(result) is int


def test_v0_1_s02_empty_file_has_no_words(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Scenario S02: an empty file has 0 words."""
    _write(tmp_path, "empty.txt", b"")
    monkeypatch.chdir(tmp_path)
    assert count_words("empty.txt") == 0


def test_v0_1_s03_missing_file_raises_file_not_found(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Scenario S03: a file that does not exist raises FileNotFoundError."""
    monkeypatch.chdir(tmp_path)
    with pytest.raises(FileNotFoundError):
        count_words("missing.txt")


def test_v0_1_s04_latin1_file_raises_unicode_decode_error(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Scenario S04: a file that is not valid UTF-8 raises UnicodeDecodeError."""
    data = "café au lait".encode("latin-1")
    assert data.startswith(bytes([0x63, 0x61, 0x66, 0xE9, 0x20]))
    _write(tmp_path, "latin1.txt", data)
    monkeypatch.chdir(tmp_path)
    with pytest.raises(UnicodeDecodeError):
        count_words("latin1.txt")


def test_v0_1_s05_runs_without_letter_or_digit_do_not_count(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Scenario S05: the runs `--`, `...`, and `_` are not words."""
    _write(tmp_path, "dashes.txt", b"Wait -- what ... don't x--y 3.14 _")
    monkeypatch.chdir(tmp_path)
    assert count_words("dashes.txt") == 5


def test_v0_1_s06_only_symbols_have_no_words(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Scenario S06: a file of runs without a letter or digit has 0 words."""
    _write(tmp_path, "only-symbols.txt", b"-- ... !!!")
    monkeypatch.chdir(tmp_path)
    assert count_words("only-symbols.txt") == 0


@pytest.mark.skipif(sys.platform != "win32", reason="S07 runs on Windows 11 on Troy's PC only")
@pytest.mark.skipif(sys.version_info[:2] != (3, 13), reason="S07 runs with Python 3.13")
def test_v0_1_s07_same_count_for_windows_and_linux_files(tmp_path: pathlib.Path) -> None:
    """Scenario S07: a new Python process counts the three files and leaves them unchanged."""
    files_dir = tmp_path / "files"
    files_dir.mkdir()
    run_dir = tmp_path / "elsewhere"
    run_dir.mkdir()
    paths = [
        _write(files_dir, "windows.txt", BOM + b"Hello world\r\n  troy-mode  trial\r\n"),
        _write(files_dir, "linux.txt", b"Hello world\n  troy-mode  trial\n"),
        _write(files_dir, "mixed.txt", MIXED_TEXT.encode("utf-8")),
    ]
    recorded = [path.read_bytes() for path in paths]
    script = (
        "import pathlib, sys\n"
        "import troy_mode_trial\n"
        "for name in sys.argv[1:]:\n"
        "    print(troy_mode_trial.count_words(pathlib.Path(name)))\n"
    )
    completed = subprocess.run(  # noqa: S603
        [sys.executable, "-c", script, *(str(path) for path in paths)],
        cwd=run_dir,
        capture_output=True,
        text=True,
        check=False,
    )
    assert completed.returncode == 0, completed.stderr
    assert completed.stdout.split() == ["4", "4", "7"]
    assert [path.read_bytes() for path in paths] == recorded
