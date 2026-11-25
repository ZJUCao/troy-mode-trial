"""Tests for F07: the option `--longest` of the `wordcount` command and of `main`."""

import os
import pathlib
import shutil
import subprocess
import sys
import sysconfig

import pytest

from troy_mode_trial.cli import main

BOM = bytes.fromhex("EF BB BF")
NOTES = b"Hello world\n  troy-mode  trial\n"
WINDOWS = BOM + b"Hello world\r\n  troy-mode  trial\r\n"
GREETING = "你好 世界!\r\n".encode()
DASHES = b"-- ...\n"
LATIN1 = "caf\xe9 au lait\n".encode("latin-1")
USAGE = "usage: wordcount [--lines | --chars | --longest] FILE"
REQUIRED = "wordcount: error: the following arguments are required: FILE"
_NL = os.linesep.encode()


@pytest.fixture
def work(tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch) -> pathlib.Path:
    """Make `tmp_path` hold the standard files and be the working directory.

    Args:
        tmp_path: pytest's temporary folder.
        monkeypatch: pytest's monkeypatch fixture.

    Returns:
        The folder, which is now the working directory.
    """
    (tmp_path / "notes.txt").write_bytes(NOTES)
    (tmp_path / "windows.txt").write_bytes(WINDOWS)
    (tmp_path / "greeting.txt").write_bytes(GREETING)
    (tmp_path / "dashes.txt").write_bytes(DASHES)
    (tmp_path / "latin1.txt").write_bytes(LATIN1)
    (tmp_path / "sub").mkdir()
    monkeypatch.chdir(tmp_path)
    return tmp_path


def _run(
    capsys: pytest.CaptureFixture[str],
    argv: list[str] | tuple[str, ...] | None,
    *,
    exits: bool = False,
) -> tuple[int, str, str]:
    """Call `main` once and read its output.

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


def _assert_usage(result: tuple[int, str, str], message: str | None) -> None:
    """Check that a result is a usage error with the F07 usage line.

    Args:
        result: The exit code, standard output, and standard error.
        message: The exact second line, or None to check only its start.
    """
    code, out, err = result
    assert code == 2
    assert out == ""
    lines = err.split("\n")
    assert len(lines) == 3
    assert lines[2] == ""
    assert lines[0] == USAGE
    if message is None:
        assert lines[1].startswith("wordcount: error: ")
    else:
        assert lines[1] == message


def _file_error(name: str, reason: str) -> tuple[int, str, str]:
    """Build the expected result of a file error.

    Args:
        name: The argument as typed.
        reason: The reason text.

    Returns:
        The expected exit code, standard output, and standard error.
    """
    return (2, "", f"wordcount: {name}: {reason}\n")


def test_f07_t20_design_examples(work: pathlib.Path, capsys: pytest.CaptureFixture[str]) -> None:
    """The length and one line break on standard output, and code 0."""
    for name, expected in (("notes.txt", "9\n"), ("greeting.txt", "3\n"), ("dashes.txt", "0\n")):
        code = main(["--longest", name])
        captured = capsys.readouterr()
        assert code == 0
        assert type(code) is int
        assert captured.out == expected
        assert captured.err == ""


def test_f07_t21_position_and_twice(work: pathlib.Path, capsys: pytest.CaptureFixture[str]) -> None:
    """The option may come after the file, and given twice it works as given once."""
    for argv in (
        ["notes.txt", "--longest"],
        ["--longest", "--longest", "notes.txt"],
        ["notes.txt", "--longest", "--longest"],
    ):
        assert _run(capsys, argv) == (0, "9\n", "")


def test_f07_t22_plain_decimal(work: pathlib.Path, capsys: pytest.CaptureFixture[str]) -> None:
    """The printed number is what `count_longest` returns, as a plain decimal."""
    (work / "empty.txt").write_bytes(b"")
    (work / "bom.txt").write_bytes(BOM)
    (work / "said.txt").write_bytes(b"don't, he said.")
    (work / "many.txt").write_bytes(b"a" * 12345 + b"\n")
    cases = [
        ("windows.txt", "9\n"),
        ("empty.txt", "0\n"),
        ("bom.txt", "0\n"),
        ("said.txt", "6\n"),
        ("many.txt", "12345\n"),
    ]
    for name, expected in cases:
        assert _run(capsys, ["--longest", name]) == (0, expected, "")


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


def test_f07_t23_keeps_no_state(work: pathlib.Path, capsys: pytest.CaptureFixture[str]) -> None:
    """The option changes only what is printed, and `main` keeps no state."""
    before = _snapshot(work)
    cwd = pathlib.Path.cwd()
    argv = list(sys.argv)
    steps = [
        (["--longest", "notes.txt"], (0, "9\n", "")),
        (["notes.txt"], (0, "4\n", "")),
        (["--longest", "missing.txt"], _file_error("missing.txt", "no such file")),
        (["--longest", "latin1.txt"], _file_error("latin1.txt", "not valid UTF-8")),
        (["--chars", "notes.txt"], (0, "31\n", "")),
        (["--lines", "notes.txt"], (0, "2\n", "")),
        (["--longest", "notes.txt"], (0, "9\n", "")),
    ]
    for args, want in steps:
        assert _run(capsys, args) == want
    assert _snapshot(work) == before
    assert pathlib.Path.cwd() == cwd
    assert sys.argv == argv


def test_f07_t24_path_forms(
    work: pathlib.Path, capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch
) -> None:
    """FILE may be any path form, and after `--` the text `--longest` is a file name."""
    for name in ("sub/notes.txt", "my notes.txt", "日本語.txt", "-notes.txt"):
        (work / name).write_bytes(NOTES)
    (work / "--longest").write_bytes(NOTES)
    monkeypatch.chdir(work / "sub")
    assert _run(capsys, ["--longest", str(work / "notes.txt")]) == (0, "9\n", "")
    monkeypatch.chdir(work)
    for argv in (
        ["--longest", "sub/notes.txt"],
        ["--longest", "my notes.txt"],
        ["--longest", "日本語.txt"],
        ["--longest", "--", "-notes.txt"],
        ["--longest", "--", "--longest"],
    ):
        assert _run(capsys, argv) == (0, "9\n", "")
    assert _run(capsys, ["--", "--longest"]) == (0, "4\n", "")


def test_f07_t25_no_such_file(work: pathlib.Path, capsys: pytest.CaptureFixture[str]) -> None:
    """Every case of no such file gives the line of `wordcount FILE`."""
    missing = "缺失.txt"
    calls = [
        (["--longest", "missing.txt"], "missing.txt"),
        (["missing.txt"], "missing.txt"),
        (["--longest", ""], ""),
        (["--longest", "missing-folder/notes.txt"], "missing-folder/notes.txt"),
        (["--longest", "notes.txt/inner.txt"], "notes.txt/inner.txt"),
        (["--longest", missing], missing),
        (["missing.txt", "--longest"], "missing.txt"),
    ]
    for argv, name in calls:
        assert _run(capsys, argv) == _file_error(name, "no such file")


def test_f07_t26_not_valid_utf8(work: pathlib.Path, capsys: pytest.CaptureFixture[str]) -> None:
    """A file that is not valid UTF-8 gets that reason, also after valid words."""
    (work / "broken.txt").write_bytes(bytes.fromhex("6F 6B 20 FF FE"))
    (work / "late.txt").write_bytes(b"a longword\n" * 100_000 + b"\xff")
    for name in ("latin1.txt", "broken.txt", "late.txt"):
        assert _run(capsys, ["--longest", name]) == _file_error(name, "not valid UTF-8")


def test_f07_t27_folder(work: pathlib.Path, capsys: pytest.CaptureFixture[str]) -> None:
    """A folder gets the reason `is a folder` on both systems."""
    for name in ("sub", "."):
        assert _run(capsys, ["--longest", name]) == _file_error(name, "is a folder")


@pytest.mark.skipif(
    sys.platform == "win32", reason="a test cannot remove its read right on Windows"
)
@pytest.mark.skipif(
    sys.platform != "win32" and os.geteuid() == 0, reason="root can read the file anyway"
)
def test_f07_t28_permission_denied(work: pathlib.Path, capsys: pytest.CaptureFixture[str]) -> None:
    """A file the process may not read gets the reason `permission denied`."""
    secret = work / "secret.txt"
    secret.write_bytes(b"one two")
    secret.chmod(0o000)
    try:
        result = _run(capsys, ["--longest", "secret.txt"])
    finally:
        secret.chmod(0o600)
    assert result == _file_error("secret.txt", "permission denied")


def test_f07_t29_cannot_read_file(work: pathlib.Path, capsys: pytest.CaptureFixture[str]) -> None:
    """Any other error while the file is opened gets the reason `cannot read file`."""
    names = ["a" * 300 + ".txt"]
    if sys.platform == "win32":
        names.append("a?b.txt")
    for name in names:
        assert _run(capsys, ["--longest", name]) == _file_error(name, "cannot read file")


def test_f07_t30_combined_with_other_options(
    work: pathlib.Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """`--longest` with `--lines` or `--chars` is a usage error, in any order."""
    longest_lines = "wordcount: error: argument --lines: not allowed with argument --longest"
    calls = [
        (
            ["--lines", "--longest", "notes.txt"],
            "wordcount: error: argument --longest: not allowed with argument --lines",
        ),
        (
            ["--longest", "notes.txt", "--chars"],
            "wordcount: error: argument --chars: not allowed with argument --longest",
        ),
        (
            ["--longest", "--chars", "notes.txt"],
            "wordcount: error: argument --chars: not allowed with argument --longest",
        ),
        (
            ["--chars", "--longest", "notes.txt"],
            "wordcount: error: argument --longest: not allowed with argument --chars",
        ),
        (["--longest", "--lines", "notes.txt"], longest_lines),
        (["--longest", "--lines"], longest_lines),
        (
            ["--lines", "--chars", "notes.txt"],
            "wordcount: error: argument --chars: not allowed with argument --lines",
        ),
    ]
    for argv, message in calls:
        _assert_usage(_run(capsys, argv, exits=True), message)


def test_f07_t31_other_wrong_command_lines(
    work: pathlib.Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """Every other wrong command line with the option is a usage error."""
    calls = [
        (["--longest"], REQUIRED),
        (["-L", "notes.txt"], "wordcount: error: unrecognized arguments: -L"),
        (["--long", "notes.txt"], "wordcount: error: unrecognized arguments: --long"),
        (["--lo", "notes.txt"], "wordcount: error: unrecognized arguments: --lo"),
        (["--LONGEST", "notes.txt"], "wordcount: error: unrecognized arguments: --LONGEST"),
        (["--longest", "-h", "notes.txt"], "wordcount: error: unrecognized arguments: -h"),
        (
            ["--longest", "notes.txt", "notes.txt"],
            "wordcount: error: unrecognized arguments: notes.txt",
        ),
        (["--longest=5", "notes.txt"], None),
    ]
    for argv, message in calls:
        result = _run(capsys, argv, exits=True)
        _assert_usage(result, message)
        assert "wordcount: notes.txt: " not in result[2]


def test_f07_t32_usage_line_and_program_name(
    work: pathlib.Path, capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch
) -> None:
    """Every usage error shows the F07 usage line, and the program name is `wordcount`."""
    monkeypatch.setattr(sys, "argv", ["other-name.py"])
    _assert_usage(_run(capsys, [], exits=True), REQUIRED)
    unknown = "wordcount: error: unrecognized arguments: --long"
    _assert_usage(_run(capsys, ["--long", "notes.txt"], exits=True), unknown)
    assert _run(capsys, ["--longest", "missing.txt"]) == _file_error("missing.txt", "no such file")


def test_f07_t33_reads_sys_argv(
    work: pathlib.Path, capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch
) -> None:
    """With no argument, `main` reads `sys.argv[1:]`, and `argv` may be a tuple."""
    monkeypatch.setattr(sys, "argv", ["wordcount", "--longest", "notes.txt"])
    code = main()
    assert (code, capsys.readouterr().out) == (0, "9\n")
    code = main(None)
    assert (code, capsys.readouterr().out) == (0, "9\n")
    code = main(("--longest", "notes.txt"))
    assert (code, capsys.readouterr().out) == (0, "9\n")


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


def _outcome(done: subprocess.CompletedProcess[bytes]) -> tuple[int, bytes, bytes]:
    """Reduce a finished process to its code and output.

    Args:
        done: The finished process.

    Returns:
        The exit code, standard output, and standard error.
    """
    return (done.returncode, done.stdout, done.stderr)


def test_f07_t34_program_counts(work: pathlib.Path) -> None:
    """The installed program finds the longest word, and still counts words."""
    runs = [
        (["--longest", "notes.txt"], b"9"),
        (["notes.txt", "--longest"], b"9"),
        (["--longest", "greeting.txt"], b"3"),
        (["--longest", "dashes.txt"], b"0"),
        (["notes.txt"], b"4"),
    ]
    for args, number in runs:
        assert _outcome(_program(work, args)) == (0, number + _NL, b"")


def test_f07_t35_program_file_errors(work: pathlib.Path) -> None:
    """The installed program reports a file error with `--longest` with code 2."""
    done = _program(work, ["--longest", "missing.txt"])
    assert _outcome(done) == (2, b"", b"wordcount: missing.txt: no such file" + _NL)
    done = _program(work, ["--longest", "latin1.txt"])
    assert _outcome(done) == (2, b"", b"wordcount: latin1.txt: not valid UTF-8" + _NL)


def test_f07_t36_program_usage(work: pathlib.Path) -> None:
    """A wrong command line exits with code 2 and the F07 usage line."""
    runs = [
        (
            ["--lines", "--longest", "notes.txt"],
            "wordcount: error: argument --longest: not allowed with argument --lines",
        ),
        (["--long", "notes.txt"], "wordcount: error: unrecognized arguments: --long"),
        (["-L", "notes.txt"], "wordcount: error: unrecognized arguments: -L"),
        (["--longest"], REQUIRED),
    ]
    for args, message in runs:
        expected = f"{USAGE}\n{message}\n".replace("\n", os.linesep).encode()
        assert _outcome(_program(work, args)) == (2, b"", expected)


def test_f07_t37_program_arguments(work: pathlib.Path) -> None:
    """The arguments reach the program as Troy types them."""
    for name in ("my notes.txt", "日本語.txt", "-notes.txt"):
        (work / name).write_bytes(NOTES)
    runs = [
        (work / "sub", ["--longest", str(work / "notes.txt")]),
        (work, ["--longest", "my notes.txt"]),
        (work, ["--longest", "日本語.txt"]),
        (work, ["--longest", "--", "-notes.txt"]),
    ]
    for cwd, args in runs:
        assert _outcome(_program(cwd, args)) == (0, b"9" + _NL, b"")
