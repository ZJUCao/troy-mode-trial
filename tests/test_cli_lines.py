"""Tests for F05: the option `--lines` of the `wordcount` command and of `main`."""

import os
import pathlib
import shutil
import subprocess
import sys
import sysconfig

import pytest

from troy_mode_trial.cli import main

NOTES = b"Hello world\n  troy-mode  trial\n"
WINDOWS = b"Hello world\r\n  troy-mode  trial\r\n"
LATIN1 = "café au lait\n".encode("latin-1")
USAGE_LINES_ONLY = "usage: wordcount [--lines] FILE"
USAGE_BOTH = "usage: wordcount [--lines | --chars] FILE"
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


def _chars_landed_main(capsys: pytest.CaptureFixture[str]) -> bool:
    """Ask `main` whether F06's code is on the branch under test.

    Args:
        capsys: pytest's capture fixture. The output of the probe is thrown away.

    Returns:
        True if `--chars` works, false if it is an unknown option.
    """
    try:
        code = main(["--chars", "notes.txt"])
    except SystemExit as exit_info:
        capsys.readouterr()
        assert exit_info.code == 2
        return False
    capsys.readouterr()
    assert code == 0
    return True


def _usage_main(capsys: pytest.CaptureFixture[str]) -> str:
    """Find the usage line of the state of the branch, through `main`.

    Args:
        capsys: pytest's capture fixture.

    Returns:
        The expected first line of a usage error.
    """
    return USAGE_BOTH if _chars_landed_main(capsys) else USAGE_LINES_ONLY


def _assert_usage(result: tuple[int, str, str], usage: str, message: str | None) -> None:
    """Check that a result is a usage error.

    Args:
        result: The exit code, standard output, and standard error.
        usage: The exact first line.
        message: The exact second line, or None to check only its start.
    """
    code, out, err = result
    assert code == 2
    assert out == ""
    lines = err.split("\n")
    assert len(lines) == 3
    assert lines[2] == ""
    assert lines[0] == usage
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


def test_f05_t01_design_example(work: pathlib.Path, capsys: pytest.CaptureFixture[str]) -> None:
    """The line count and one line break on standard output, and code 0."""
    code = main(["--lines", "notes.txt"])
    captured = capsys.readouterr()
    assert code == 0
    assert type(code) is int
    assert captured.out == "2\n"
    assert captured.err == ""


def test_f05_t02_option_position_and_twice(
    work: pathlib.Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """The option may come after the file, and given twice it counts once."""
    for argv in (
        ["notes.txt", "--lines"],
        ["--lines", "--lines", "notes.txt"],
        ["notes.txt", "--lines", "--lines"],
    ):
        assert _run(capsys, argv) == (0, "2\n", "")


def test_f05_t03_counts_as_f02(work: pathlib.Path, capsys: pytest.CaptureFixture[str]) -> None:
    """Line ends are counted as F02 counts them."""
    files = [
        ("one-break.txt", b"\n", "1\n"),
        ("no-end.txt", b"Hello world\n  troy-mode  trial", "2\n"),
        ("windows.txt", WINDOWS, "2\n"),
        ("blank.txt", b"first\n\nthird\n", "3\n"),
        ("mixed.txt", b"one\rtwo\r\nthree\nfour", "4\n"),
        ("cr-crlf.txt", b"\r\r\n", "2\n"),
        ("lf-cr.txt", b"\n\r", "2\n"),
        ("other-breaks.txt", "a b\fc\x85d".encode(), "1\n"),
        ("unicode-breaks.txt", "a\vb c d".encode(), "1\n"),
    ]
    for name, data, expected in files:
        (work / name).write_bytes(data)
        assert _run(capsys, ["--lines", name]) == (0, expected, "")


def test_f05_t04_empty_and_bom(work: pathlib.Path, capsys: pytest.CaptureFixture[str]) -> None:
    """An empty file has 0 lines, and one byte order mark is ignored."""
    files = [
        ("empty.txt", b"", "0\n"),
        ("bom-only.txt", bytes.fromhex("EF BB BF"), "0\n"),
        ("bom.txt", bytes.fromhex("EF BB BF") + b"a\nb", "2\n"),
    ]
    for name, data, expected in files:
        (work / name).write_bytes(data)
        assert _run(capsys, ["--lines", name]) == (0, expected, "")


def test_f05_t05_plain_decimal(work: pathlib.Path, capsys: pytest.CaptureFixture[str]) -> None:
    """The count has no sign, padding, or separator."""
    (work / "many.txt").write_bytes(b"\n" * 12345)
    assert _run(capsys, ["--lines", "many.txt"]) == (0, "12345\n", "")


def test_f05_t06_path_forms(
    work: pathlib.Path, capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch
) -> None:
    """FILE may be any path form, and after `--` the text `--lines` is a file name."""
    for name in ("sub/notes.txt", "my notes.txt", "日本語.txt", "-notes.txt", "--lines"):
        (work / name).write_bytes(NOTES)
    monkeypatch.chdir(work / "sub")
    assert _run(capsys, ["--lines", str(work / "notes.txt")]) == (0, "2\n", "")
    monkeypatch.chdir(work)
    for argv in (
        ["--lines", "sub/notes.txt"],
        ["--lines", "my notes.txt"],
        ["--lines", "日本語.txt"],
        ["--lines", "--", "-notes.txt"],
        ["--lines", "--", "--lines"],
    ):
        assert _run(capsys, argv) == (0, "2\n", "")
    assert _run(capsys, ["--", "--lines"]) == (0, "4\n", "")


def test_f05_t07_missing_file(
    tmp_path: pathlib.Path, capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch
) -> None:
    """A missing file gives the same message and code as without the option."""
    monkeypatch.chdir(tmp_path)
    expected = _file_error("missing.txt", "no such file")
    assert _run(capsys, ["--lines", "missing.txt"]) == expected
    assert _run(capsys, ["missing.txt"]) == expected


def test_f05_t08_no_such_file_cases(work: pathlib.Path, capsys: pytest.CaptureFixture[str]) -> None:
    """Every case of no such file gets that reason, with the argument as typed."""
    calls = [
        (["--lines", ""], ""),
        (["--lines", "missing-folder/notes.txt"], "missing-folder/notes.txt"),
        (["--lines", "notes.txt/inner.txt"], "notes.txt/inner.txt"),
        (["--lines", "缺失.txt"], "缺失.txt"),
        (["missing.txt", "--lines"], "missing.txt"),
    ]
    for argv, name in calls:
        assert _run(capsys, argv) == _file_error(name, "no such file")


def test_f05_t09_not_valid_utf8(work: pathlib.Path, capsys: pytest.CaptureFixture[str]) -> None:
    """A file that is not valid UTF-8 gets that reason, also after whole lines."""
    (work / "broken.txt").write_bytes(bytes.fromhex("6F 6B 20 FF FE"))
    (work / "late.txt").write_bytes(b"one\ntwo\n\xff")
    for name in ("latin1.txt", "broken.txt", "late.txt"):
        assert _run(capsys, ["--lines", name]) == _file_error(name, "not valid UTF-8")


def test_f05_t10_folder(work: pathlib.Path, capsys: pytest.CaptureFixture[str]) -> None:
    """A folder gets the reason `is a folder` on both systems."""
    for name in ("sub", "."):
        assert _run(capsys, ["--lines", name]) == _file_error(name, "is a folder")


@pytest.mark.skipif(
    sys.platform == "win32", reason="a test cannot remove its read right on Windows"
)
@pytest.mark.skipif(
    sys.platform != "win32" and os.geteuid() == 0, reason="root can read the file anyway"
)
def test_f05_t11_permission_denied(work: pathlib.Path, capsys: pytest.CaptureFixture[str]) -> None:
    """A file the process may not read gets the reason `permission denied`."""
    secret = work / "secret.txt"
    secret.write_bytes(b"one\ntwo\n")
    secret.chmod(0o000)
    try:
        result = _run(capsys, ["--lines", "secret.txt"])
    finally:
        secret.chmod(0o600)
    assert result == _file_error("secret.txt", "permission denied")


def test_f05_t12_cannot_read_file(work: pathlib.Path, capsys: pytest.CaptureFixture[str]) -> None:
    """Any other error while the file is opened gets the reason `cannot read file`."""
    names = ["a" * 300 + ".txt"]
    if sys.platform == "win32":
        names.append("a?b.txt")
    for name in names:
        assert _run(capsys, ["--lines", name]) == _file_error(name, "cannot read file")


def test_f05_t13_both_options(work: pathlib.Path, capsys: pytest.CaptureFixture[str]) -> None:
    """`--lines` with `--chars` is a usage error, in any order and at any place."""
    landed = _chars_landed_main(capsys)
    usage = USAGE_BOTH if landed else USAGE_LINES_ONLY
    not_chars = "wordcount: error: argument --chars: not allowed with argument --lines"
    not_lines = "wordcount: error: argument --lines: not allowed with argument --chars"
    unknown = "wordcount: error: unrecognized arguments: --chars"
    required = "wordcount: error: the following arguments are required: FILE"
    calls = [
        (["--lines", "--chars", "notes.txt"], not_chars if landed else unknown),
        (["--chars", "--lines", "notes.txt"], not_lines if landed else unknown),
        (["--lines", "notes.txt", "--chars"], not_chars if landed else unknown),
        (["--lines", "--chars"], not_chars if landed else required),
    ]
    for argv, message in calls:
        _assert_usage(_run(capsys, argv, exits=True), usage, message)


def test_f05_t14_other_wrong_command_lines(
    work: pathlib.Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """Every other wrong command line with `--lines` is a usage error."""
    usage = _usage_main(capsys)
    calls = [
        (["--lines"], "wordcount: error: the following arguments are required: FILE"),
        (["-l", "notes.txt"], "wordcount: error: unrecognized arguments: -l"),
        (["--line", "notes.txt"], "wordcount: error: unrecognized arguments: --line"),
        (["--li", "notes.txt"], "wordcount: error: unrecognized arguments: --li"),
        (["--lines", "-h", "notes.txt"], "wordcount: error: unrecognized arguments: -h"),
        (
            ["--lines", "notes.txt", "notes.txt"],
            "wordcount: error: unrecognized arguments: notes.txt",
        ),
        (["--lines=x", "notes.txt"], None),
    ]
    for argv, message in calls:
        result = _run(capsys, argv, exits=True)
        _assert_usage(result, usage, message)
        assert "wordcount: notes.txt: " not in result[2]


def test_f05_t15_usage_line_and_program_name(
    work: pathlib.Path, capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch
) -> None:
    """Every usage error shows the usage line, and the program name is `wordcount`."""
    monkeypatch.setattr(sys, "argv", ["other-name.py"])
    usage = _usage_main(capsys)
    required = "wordcount: error: the following arguments are required: FILE"
    _assert_usage(_run(capsys, [], exits=True), usage, required)
    assert _run(capsys, ["--lines", "missing.txt"]) == _file_error("missing.txt", "no such file")


def test_f05_t16_reads_sys_argv(
    work: pathlib.Path, capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch
) -> None:
    """With no argument, `main` reads `sys.argv[1:]`."""
    monkeypatch.setattr(sys, "argv", ["wordcount", "--lines", "notes.txt"])
    assert _run(capsys, None) == (0, "2\n", "")
    code = main()
    captured = capsys.readouterr()
    assert (code, captured.out, captured.err) == (0, "2\n", "")


def test_f05_t17_tuple_argv(work: pathlib.Path, capsys: pytest.CaptureFixture[str]) -> None:
    """`argv` may be a tuple."""
    assert _run(capsys, ("--lines", "notes.txt")) == (0, "2\n", "")


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


def test_f05_t18_keeps_no_state(work: pathlib.Path, capsys: pytest.CaptureFixture[str]) -> None:
    """`main` keeps no state between calls, writes no file, and still counts words."""
    before = _snapshot(work)
    cwd = pathlib.Path.cwd()
    argv = list(sys.argv)
    steps = [
        (["--lines", "notes.txt"], (0, "2\n", "")),
        (["notes.txt"], (0, "4\n", "")),
        (["--lines", "missing.txt"], _file_error("missing.txt", "no such file")),
        (["--lines", "latin1.txt"], _file_error("latin1.txt", "not valid UTF-8")),
        (["notes.txt"], (0, "4\n", "")),
        (["--lines", "notes.txt"], (0, "2\n", "")),
    ]
    for args, want in steps:
        assert _run(capsys, args) == want
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


def _outcome(done: subprocess.CompletedProcess[bytes]) -> tuple[int, bytes, bytes]:
    """Reduce a finished process to its code and output.

    Args:
        done: The finished process.

    Returns:
        The exit code, standard output, and standard error.
    """
    return (done.returncode, done.stdout, done.stderr)


def test_f05_t19_program_counts(work: pathlib.Path) -> None:
    """The installed program counts lines with the option and words without it."""
    assert _outcome(_program(work, ["--lines", "notes.txt"])) == (0, b"2" + _NL, b"")
    assert _outcome(_program(work, ["notes.txt"])) == (0, b"4" + _NL, b"")


def test_f05_t20_program_position_and_windows(work: pathlib.Path) -> None:
    """The program takes the option after the file and counts Windows line ends."""
    assert _outcome(_program(work, ["notes.txt", "--lines"])) == (0, b"2" + _NL, b"")
    assert _outcome(_program(work, ["--lines", "windows.txt"])) == (0, b"2" + _NL, b"")


def test_f05_t21_program_missing_file(tmp_path: pathlib.Path) -> None:
    """The program reports a missing file with code 2."""
    done = _program(tmp_path, ["--lines", "missing.txt"])
    expected = b"wordcount: missing.txt: no such file" + _NL
    assert _outcome(done) == (2, b"", expected)


def test_f05_t22_program_not_utf8_and_folder(work: pathlib.Path) -> None:
    """The program reports a file that is not valid UTF-8 and a folder with code 2."""
    done = _program(work, ["--lines", "latin1.txt"])
    assert _outcome(done) == (2, b"", b"wordcount: latin1.txt: not valid UTF-8" + _NL)
    done = _program(work, ["--lines", "sub"])
    assert _outcome(done) == (2, b"", b"wordcount: sub: is a folder" + _NL)


def test_f05_t23_program_usage(work: pathlib.Path) -> None:
    """A wrong command line exits with code 2 and the usage line of the state."""
    probe = _program(work, ["--chars", "notes.txt"])
    assert probe.returncode in (0, 2)
    landed = probe.returncode == 0
    usage = USAGE_BOTH if landed else USAGE_LINES_ONLY
    both = (
        "wordcount: error: argument --chars: not allowed with argument --lines"
        if landed
        else "wordcount: error: unrecognized arguments: --chars"
    )
    runs = [
        (["--lines", "--chars", "notes.txt"], both),
        (["-l", "notes.txt"], "wordcount: error: unrecognized arguments: -l"),
        (["--lines"], "wordcount: error: the following arguments are required: FILE"),
    ]
    for args, message in runs:
        done = _program(work, args)
        expected = f"{usage}\n{message}\n".replace("\n", os.linesep).encode()
        assert _outcome(done) == (2, b"", expected)


def test_f05_t24_program_arguments(work: pathlib.Path) -> None:
    """The arguments reach the program as Troy types them."""
    for name in ("my notes.txt", "日本語.txt", "-notes.txt"):
        (work / name).write_bytes(NOTES)
    runs = [
        (work / "sub", ["--lines", str(work / "notes.txt")]),
        (work, ["--lines", "my notes.txt"]),
        (work, ["--lines", "日本語.txt"]),
        (work, ["--lines", "--", "-notes.txt"]),
    ]
    for cwd, args in runs:
        assert _outcome(_program(cwd, args)) == (0, b"2" + _NL, b"")
