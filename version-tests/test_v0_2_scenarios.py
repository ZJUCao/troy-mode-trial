# ruff: noqa: S101
"""Version tests of v0.2, one test for each scenario of the v0.2 version test plan.

Scenario v0.2-S18 is run by Troy in Windows Terminal and has no test.
"""

import pathlib
import shutil
import subprocess
import sys

import pytest

from troy_mode_trial import count_lines

BOM = b"\xef\xbb\xbf"
MIXED_TEXT = "Wait -- what ... don't x--y 3.14 _\r\n日本語　テキスト 😀\n"
NOTES = b"Hello world\n  troy-mode  trial"
LATIN1 = "café au lait\n".encode("latin-1")


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


def _write_three(directory: pathlib.Path) -> list[pathlib.Path]:
    """Write the three files of scenarios S09 and S15.

    Args:
        directory: The folder that receives the files.

    Returns:
        The paths of `windows.txt`, `linux.txt`, and `mixed.txt`, in this order.
    """
    return [
        _write(directory, "windows.txt", BOM + b"Hello world\r\n  troy-mode  trial\r\n"),
        _write(directory, "linux.txt", b"Hello world\n  troy-mode  trial\n"),
        _write(directory, "mixed.txt", MIXED_TEXT.encode("utf-8")),
    ]


def _wordcount(cwd: pathlib.Path, *args: str) -> tuple[str, str, int]:
    """Run the `wordcount` that is on PATH as a new process.

    Args:
        cwd: The working directory of the process.
        *args: The command-line arguments.

    Returns:
        Standard output and standard error, with CRLF read as LF, and the exit code.
    """
    exe = shutil.which("wordcount")
    assert exe is not None, "no wordcount on PATH"
    completed = subprocess.run(  # noqa: S603
        [exe, *args],
        cwd=cwd,
        capture_output=True,
        check=False,
    )
    out = completed.stdout.decode("utf-8").replace("\r\n", "\n")
    err = completed.stderr.decode("utf-8").replace("\r\n", "\n")
    return out, err, completed.returncode


def test_v0_2_s01_counts_lines_without_final_break(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Scenario S01: two lines, the last without a line break, give an exact int 2."""
    _write(tmp_path, "notes.txt", NOTES)
    monkeypatch.chdir(tmp_path)
    result = count_lines("notes.txt")
    assert result == 2
    assert type(result) is int


def test_v0_2_s02_windows_breaks_end_one_line_each(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Scenario S02: each CRLF ends one line."""
    _write(tmp_path, "windows.txt", b"Hello world\r\n  troy-mode  trial")
    monkeypatch.chdir(tmp_path)
    assert count_lines("windows.txt") == 2


def test_v0_2_s03_empty_file_has_no_lines(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Scenario S03: an empty file has 0 lines."""
    _write(tmp_path, "empty.txt", b"")
    monkeypatch.chdir(tmp_path)
    assert count_lines("empty.txt") == 0


def test_v0_2_s04_missing_file_raises_file_not_found(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Scenario S04: a file that does not exist raises FileNotFoundError."""
    monkeypatch.chdir(tmp_path)
    with pytest.raises(FileNotFoundError):
        count_lines("missing.txt")


def test_v0_2_s05_latin1_file_raises_unicode_decode_error(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Scenario S05: a file that is not valid UTF-8 raises UnicodeDecodeError."""
    assert LATIN1.startswith(bytes([0x63, 0x61, 0x66, 0xE9, 0x20]))
    _write(tmp_path, "latin1.txt", LATIN1)
    monkeypatch.chdir(tmp_path)
    with pytest.raises(UnicodeDecodeError):
        count_lines("latin1.txt")


def test_v0_2_s06_one_line_break_is_one_line(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Scenario S06: a file of one line break has 1 line."""
    _write(tmp_path, "one-break.txt", b"\n")
    monkeypatch.chdir(tmp_path)
    assert count_lines("one-break.txt") == 1


def test_v0_2_s07_empty_lines_count_and_final_break_does_not_add(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Scenario S07: an empty middle line counts, the final break starts no new line."""
    _write(tmp_path, "blank-lines.txt", b"first\n\nthird\n")
    monkeypatch.chdir(tmp_path)
    assert count_lines("blank-lines.txt") == 3


def test_v0_2_s08_mixed_line_breaks(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Scenario S08: CR, CRLF, and LF each end one line."""
    _write(tmp_path, "mixed-breaks.txt", b"one\rtwo\r\nthree\nfour")
    monkeypatch.chdir(tmp_path)
    assert count_lines("mixed-breaks.txt") == 4


@pytest.mark.skipif(sys.platform != "win32", reason="S09 runs on Windows 11 on Troy's PC only")
@pytest.mark.skipif(sys.version_info[:2] != (3, 13), reason="S09 runs with Python 3.13")
def test_v0_2_s09_same_counts_for_windows_and_linux_files(tmp_path: pathlib.Path) -> None:
    """Scenario S09: a new Python process counts lines and words and leaves the files unchanged."""
    files_dir = tmp_path / "files"
    files_dir.mkdir()
    run_dir = tmp_path / "elsewhere"
    run_dir.mkdir()
    paths = _write_three(files_dir)
    recorded = [path.read_bytes() for path in paths]
    script = (
        "import pathlib, sys\n"
        "import troy_mode_trial\n"
        "for name in sys.argv[1:]:\n"
        "    path = pathlib.Path(name)\n"
        "    lines = troy_mode_trial.count_lines(path)\n"
        "    words = troy_mode_trial.count_words(path)\n"
        "    print(lines, words)\n"
    )
    completed = subprocess.run(  # noqa: S603
        [sys.executable, "-c", script, *(str(path) for path in paths)],
        cwd=run_dir,
        capture_output=True,
        text=True,
        check=False,
    )
    assert completed.returncode == 0, completed.stderr
    assert completed.stdout.split("\n") == ["2 4", "2 4", "2 7", ""] or (
        completed.stdout.split("\r\n") == ["2 4", "2 4", "2 7", ""]
    )
    assert [path.read_bytes() for path in paths] == recorded


def test_v0_2_s10_command_counts_words(tmp_path: pathlib.Path) -> None:
    """Scenario S10: `wordcount notes.txt` prints 4 and exits with 0."""
    _write(tmp_path, "notes.txt", NOTES)
    assert _wordcount(tmp_path, "notes.txt") == ("4\n", "", 0)


def test_v0_2_s11_command_reports_missing_file(tmp_path: pathlib.Path) -> None:
    """Scenario S11: a missing file gives the error line and exit code 2."""
    out, err, code = _wordcount(tmp_path, "missing.txt")
    assert out == ""
    assert err == "wordcount: missing.txt: no such file\n"
    assert code == 2


def test_v0_2_s12_command_reports_invalid_utf8(tmp_path: pathlib.Path) -> None:
    """Scenario S12: a Latin-1 file gives one error line and exit code 2."""
    assert LATIN1.startswith(bytes([0x63, 0x61, 0x66, 0xE9, 0x20]))
    _write(tmp_path, "latin1.txt", LATIN1)
    out, err, code = _wordcount(tmp_path, "latin1.txt")
    assert out == ""
    assert err.startswith("wordcount: latin1.txt: ")
    assert err.endswith("\n")
    assert err.count("\n") == 1
    assert code == 2


def test_v0_2_s13_command_counts_words_as_f03(tmp_path: pathlib.Path) -> None:
    """Scenario S13: runs without a letter or digit are not words."""
    _write(tmp_path, "dashes.txt", b"Wait -- what ... don't x--y 3.14 _")
    _write(tmp_path, "only-symbols.txt", b"-- ... !!!")
    assert _wordcount(tmp_path, "dashes.txt") == ("5\n", "", 0)
    assert _wordcount(tmp_path, "only-symbols.txt") == ("0\n", "", 0)


def test_v0_2_s14_command_counts_empty_file(tmp_path: pathlib.Path) -> None:
    """Scenario S14: an empty file has 0 words."""
    _write(tmp_path, "empty.txt", b"")
    assert _wordcount(tmp_path, "empty.txt") == ("0\n", "", 0)


def test_v0_2_s15_command_same_counts_for_windows_and_linux_files(
    tmp_path: pathlib.Path,
) -> None:
    """Scenario S15: absolute paths from another folder give 4, 4, and 7, files unchanged."""
    files_dir = tmp_path / "files"
    files_dir.mkdir()
    run_dir = tmp_path / "elsewhere"
    run_dir.mkdir()
    paths = _write_three(files_dir)
    recorded = [path.read_bytes() for path in paths]
    results = [_wordcount(run_dir, str(path)) for path in paths]
    assert results == [("4\n", "", 0), ("4\n", "", 0), ("7\n", "", 0)]
    assert [path.read_bytes() for path in paths] == recorded


def test_v0_2_s16_wrong_command_line_gets_usage(tmp_path: pathlib.Path) -> None:
    """Scenario S16: no argument and two arguments both give a usage line and exit code 2."""
    _write(tmp_path, "notes.txt", NOTES)
    for args in ([], ["notes.txt", "notes.txt"]):
        out, err, code = _wordcount(tmp_path, *args)
        assert out == ""
        assert err.startswith("usage:")
        assert code == 2


@pytest.mark.skipif(sys.platform != "win32", reason="S17 runs in Windows PowerShell only")
def test_v0_2_s17_powershell_finds_command_and_exit_codes(tmp_path: pathlib.Path) -> None:
    """Scenario S17: PowerShell runs `wordcount` in a folder with a space and sets the exit code."""
    folder = tmp_path / "my notes"
    folder.mkdir()
    notes = _write(folder, "notes.txt", NOTES)
    commands = "; ".join(
        [
            "wordcount notes.txt",
            'Write-Output "exit $LASTEXITCODE"',
            "wordcount missing.txt",
            'Write-Output "exit $LASTEXITCODE"',
            f"wordcount '{notes}'",
            'Write-Output "exit $LASTEXITCODE"',
        ]
    )
    completed = subprocess.run(  # noqa: S603
        ["powershell.exe", "-NoProfile", "-NonInteractive", "-Command", commands],  # noqa: S607
        cwd=folder,
        capture_output=True,
        text=True,
        check=False,
    )
    lines = completed.stdout.replace("\r\n", "\n").split("\n")[:-1]
    assert lines == ["4", "exit 0", "exit 2", "4", "exit 0"], completed.stderr
    assert "missing.txt" in completed.stderr
