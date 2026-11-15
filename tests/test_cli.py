"""Tests for F04: the `wordcount` command and its function `main`."""

import os
import pathlib
import shutil
import subprocess
import sys
import sysconfig

import pytest

from troy_mode_trial.cli import main

NOTES = b"Hello world\n  troy-mode  trial"
LATIN1 = "café au lait\n".encode("latin-1")


def _make_files(directory: pathlib.Path) -> None:
    """Create the standard files of the test plan in a folder.

    Args:
        directory: The folder that receives `notes.txt`, `latin1.txt`, and `sub`.
    """
    (directory / "notes.txt").write_bytes(NOTES)
    (directory / "latin1.txt").write_bytes(LATIN1)
    (directory / "sub").mkdir()


@pytest.fixture
def work(tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch) -> pathlib.Path:
    """Make `tmp_path` hold the standard files and be the working directory.

    Args:
        tmp_path: pytest's temporary folder.
        monkeypatch: pytest's monkeypatch fixture.

    Returns:
        The folder, which is now the working directory.
    """
    _make_files(tmp_path)
    monkeypatch.chdir(tmp_path)
    return tmp_path


def _run(
    capsys: pytest.CaptureFixture[str],
    argv: list[str] | tuple[str, ...] | None,
    *,
    exits: bool = False,
) -> tuple[int, str, str]:
    """Call `main` once and read its output.

    Checks that `main` raised `SystemExit` if `exits` is true, and that it
    returned its code otherwise.

    Args:
        capsys: pytest's capture fixture.
        argv: The arguments for `main`.
        exits: Whether `main` must raise `SystemExit` (a usage error).

    Returns:
        The exit code, standard output, and standard error.
    """
    if exits:
        with pytest.raises(SystemExit) as info:
            main(argv)
        assert isinstance(info.value.code, int)
        code = info.value.code
    else:
        code = main(argv)
    captured = capsys.readouterr()
    return code, captured.out, captured.err


def _assert_usage(code: int, out: str, err: str) -> None:
    """Check that a result is a usage error.

    Args:
        code: The exit code.
        out: Standard output.
        err: Standard error.
    """
    assert code == 2
    assert out == ""
    lines = err.split("\n")
    assert len(lines) == 3
    assert lines[2] == ""
    assert lines[0] == "usage: wordcount FILE"
    assert lines[1].startswith("wordcount: error: ")


def _assert_file_error(result: tuple[int, str, str], name: str, reason: str) -> None:
    """Check that a result is the file error of one name.

    Args:
        result: The exit code, standard output, and standard error.
        name: The argument as typed.
        reason: The expected reason text.
    """
    assert result == (2, "", f"wordcount: {name}: {reason}\n")


def test_f04_t01_design_example(work: pathlib.Path, capsys: pytest.CaptureFixture[str]) -> None:
    """The count and one line break on standard output, and code 0."""
    code = main(["notes.txt"])
    captured = capsys.readouterr()
    assert code == 0
    assert type(code) is int
    assert captured.out == "4\n"
    assert captured.err == ""


def test_f04_t02_counts_as_f03(work: pathlib.Path, capsys: pytest.CaptureFixture[str]) -> None:
    """The command counts words as F03 counts them."""
    files = {
        "dashes.txt": (b"Wait -- what ... don't x--y 3.14 _", "5\n"),
        "only-symbols.txt": (b"-- ... !!!", "0\n"),
        "empty.txt": (b"", "0\n"),
    }
    for name, (data, expected) in files.items():
        (work / name).write_bytes(data)
        assert _run(capsys, [name]) == (0, expected, "")


def test_f04_t03_plain_decimal(work: pathlib.Path, capsys: pytest.CaptureFixture[str]) -> None:
    """The count has no sign, padding, or separator."""
    (work / "many.txt").write_bytes(b"a " * 12345)
    assert _run(capsys, ["many.txt"]) == (0, "12345\n", "")


def test_f04_t04_path_forms(
    work: pathlib.Path, capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch
) -> None:
    """FILE may be any path form the design allows."""
    for name in ("sub/notes.txt", "my notes.txt", "日本語.txt", "-notes.txt"):
        (work / name).write_bytes(NOTES)
    monkeypatch.chdir(work / "sub")
    assert _run(capsys, [str(work / "notes.txt")]) == (0, "4\n", "")
    monkeypatch.chdir(work)
    for argv in (["sub/notes.txt"], ["my notes.txt"], ["日本語.txt"], ["--", "-notes.txt"]):
        assert _run(capsys, argv) == (0, "4\n", "")


def test_f04_t05_missing_file(
    tmp_path: pathlib.Path, capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch
) -> None:
    """The design's example of a missing file."""
    monkeypatch.chdir(tmp_path)
    _assert_file_error(_run(capsys, ["missing.txt"]), "missing.txt", "no such file")


def test_f04_t06_no_such_file_cases(work: pathlib.Path, capsys: pytest.CaptureFixture[str]) -> None:
    """Every case of no such file gets that reason, with the argument as typed."""
    for name in (
        "",
        "missing-folder/notes.txt",
        "notes.txt/inner.txt",
        "sub/../missing.txt",
        "缺失.txt",
    ):
        _assert_file_error(_run(capsys, [name]), name, "no such file")


def test_f04_t07_not_valid_utf8(work: pathlib.Path, capsys: pytest.CaptureFixture[str]) -> None:
    """A file that is not valid UTF-8 gets the reason `not valid UTF-8`."""
    (work / "broken.txt").write_bytes(bytes.fromhex("6F 6B 20 FF FE"))
    for name in ("latin1.txt", "broken.txt"):
        _assert_file_error(_run(capsys, [name]), name, "not valid UTF-8")


def test_f04_t08_folder(work: pathlib.Path, capsys: pytest.CaptureFixture[str]) -> None:
    """A folder gets the reason `is a folder` on both systems."""
    for name in ("sub", "."):
        _assert_file_error(_run(capsys, [name]), name, "is a folder")


@pytest.mark.skipif(
    sys.platform == "win32", reason="a test cannot remove its read right on Windows"
)
@pytest.mark.skipif(
    sys.platform != "win32" and os.geteuid() == 0, reason="root can read the file anyway"
)
def test_f04_t09_permission_denied(work: pathlib.Path, capsys: pytest.CaptureFixture[str]) -> None:
    """A file the process may not read gets the reason `permission denied`."""
    secret = work / "secret.txt"
    secret.write_bytes(b"one two")
    secret.chmod(0o000)
    try:
        result = _run(capsys, ["secret.txt"])
    finally:
        secret.chmod(0o600)
    _assert_file_error(result, "secret.txt", "permission denied")


def test_f04_t10_cannot_read_file(work: pathlib.Path, capsys: pytest.CaptureFixture[str]) -> None:
    """Any other error while the file is opened gets the reason `cannot read file`."""
    names = ["a" * 300 + ".txt"]
    if sys.platform == "win32":
        names.append("a?b.txt")
    for name in names:
        _assert_file_error(_run(capsys, [name]), name, "cannot read file")


def test_f04_t11_missing_argument(work: pathlib.Path, capsys: pytest.CaptureFixture[str]) -> None:
    """The design's example of a missing argument."""
    code, out, err = _run(capsys, [], exits=True)
    _assert_usage(code, out, err)
    assert err.split("\n")[1] == "wordcount: error: the following arguments are required: FILE"


def test_f04_t12_other_wrong_command_lines(
    work: pathlib.Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """Every other wrong command line is a usage error."""
    calls = [
        ["notes.txt", "notes.txt"],
        ["missing.txt", "other.txt"],
        ["-h"],
        ["--help"],
        ["-x", "notes.txt"],
        ["--"],
    ]
    for index, argv in enumerate(calls):
        code, out, err = _run(capsys, argv, exits=True)
        _assert_usage(code, out, err)
        if index == 0:
            assert err.split("\n")[1] == "wordcount: error: unrecognized arguments: notes.txt"
        for line in err.split("\n"):
            assert not line.startswith("wordcount: ") or line.startswith("wordcount: error: ")


def test_f04_t13_program_name(
    work: pathlib.Path, capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch
) -> None:
    """The program name in every message is `wordcount`, whatever `sys.argv[0]` holds."""
    monkeypatch.setattr(sys, "argv", ["other-name.py"])
    code, out, err = _run(capsys, [], exits=True)
    _assert_usage(code, out, err)
    assert err.split("\n")[0] == "usage: wordcount FILE"
    _assert_file_error(_run(capsys, ["missing.txt"]), "missing.txt", "no such file")


def test_f04_t14_reads_sys_argv(
    work: pathlib.Path, capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch
) -> None:
    """With no argument, `main` reads `sys.argv[1:]`."""
    monkeypatch.setattr(sys, "argv", ["wordcount", "notes.txt"])
    assert _run(capsys, None) == (0, "4\n", "")
    code = main()
    captured = capsys.readouterr()
    assert (code, captured.out, captured.err) == (0, "4\n", "")


def test_f04_t15_tuple_argv(work: pathlib.Path, capsys: pytest.CaptureFixture[str]) -> None:
    """`argv` may be a tuple."""
    assert _run(capsys, ("notes.txt",)) == (0, "4\n", "")


def _snapshot(directory: pathlib.Path) -> dict[str, bytes]:
    """Record the names and bytes of every file under a folder.

    Args:
        directory: The folder to record.

    Returns:
        A map from relative path to bytes. A folder maps to empty bytes.
    """
    return {
        path.relative_to(directory).as_posix(): path.read_bytes() if path.is_file() else b""
        for path in directory.rglob("*")
    }


def test_f04_t16_keeps_no_state(work: pathlib.Path, capsys: pytest.CaptureFixture[str]) -> None:
    """`main` keeps no state between calls, and writes no file."""
    before = _snapshot(work)
    cwd = pathlib.Path.cwd()
    argv = list(sys.argv)
    expected = [
        (0, "4\n", ""),
        (2, "", "wordcount: missing.txt: no such file\n"),
        (2, "", "wordcount: latin1.txt: not valid UTF-8\n"),
        (0, "4\n", ""),
    ]
    for name, want in zip(
        ["notes.txt", "missing.txt", "latin1.txt", "notes.txt"], expected, strict=True
    ):
        assert _run(capsys, [name]) == want
    assert _snapshot(work) == before
    assert pathlib.Path.cwd() == cwd
    assert sys.argv == argv


def _program(work: pathlib.Path, args: list[str]) -> subprocess.CompletedProcess[bytes]:
    """Run the installed `wordcount` program as a new process.

    Fails the test if the program is not in the scripts folder of this Python.

    Args:
        work: The working directory of the process.
        args: The command-line arguments.

    Returns:
        The finished process, with output captured as bytes.
    """
    found = shutil.which("wordcount", path=sysconfig.get_path("scripts"))
    if found is None:
        pytest.fail("the wordcount program is not installed in the scripts folder")
    return subprocess.run(  # noqa: S603  # fixed program, no shell, arguments from the test
        [found, *args], cwd=work, capture_output=True, check=False
    )


_NL = os.linesep.encode()


def test_f04_t17_program_counts(work: pathlib.Path) -> None:
    """The installed program counts a file."""
    done = _program(work, ["notes.txt"])
    assert (done.returncode, done.stdout, done.stderr) == (0, b"4" + _NL, b"")


def test_f04_t18_program_missing_file(tmp_path: pathlib.Path) -> None:
    """The installed program reports a missing file with code 2."""
    done = _program(tmp_path, ["missing.txt"])
    expected = b"wordcount: missing.txt: no such file" + _NL
    assert (done.returncode, done.stdout, done.stderr) == (2, b"", expected)


def test_f04_t19_program_not_utf8(work: pathlib.Path) -> None:
    """The installed program reports a file that is not valid UTF-8 with code 2."""
    done = _program(work, ["latin1.txt"])
    expected = b"wordcount: latin1.txt: not valid UTF-8" + _NL
    assert (done.returncode, done.stdout, done.stderr) == (2, b"", expected)


def test_f04_t20_program_folder(work: pathlib.Path) -> None:
    """The installed program reports a folder with code 2."""
    done = _program(work, ["sub"])
    expected = b"wordcount: sub: is a folder" + _NL
    assert (done.returncode, done.stdout, done.stderr) == (2, b"", expected)


def test_f04_t21_program_usage(work: pathlib.Path) -> None:
    """A wrong command line exits with code 2 and a usage line."""
    for args in ([], ["notes.txt", "notes.txt"], ["-h"]):
        done = _program(work, args)
        assert done.returncode == 2
        assert done.stdout == b""
        lines = done.stderr.decode("utf-8").splitlines()
        assert len(lines) == 2
        assert lines[0] == "usage: wordcount FILE"
        assert lines[1].startswith("wordcount: error: ")
        assert not any(line.startswith("wordcount: notes.txt: ") for line in lines)


def test_f04_t22_program_arguments(work: pathlib.Path) -> None:
    """The arguments reach the program as Troy types them."""
    for name in ("my notes.txt", "日本語.txt", "-notes.txt"):
        (work / name).write_bytes(NOTES)
    runs = [
        (work / "sub", [str(work / "notes.txt")]),
        (work, ["my notes.txt"]),
        (work, ["日本語.txt"]),
        (work, ["--", "-notes.txt"]),
    ]
    for cwd, args in runs:
        done = _program(cwd, args)
        assert (done.returncode, done.stdout, done.stderr) == (0, b"4" + _NL, b"")
