"""Tests for F06: the option `--chars` of the `wordcount` command and of `main`."""

import os
import pathlib
import re
import shutil
import subprocess
import sys
import sysconfig

import pytest

from troy_mode_trial.cli import main

NOTES = b"Hello world\n  troy-mode  trial\n"
HELLO = "你好\r\n".encode()
LATIN1 = "café au lait\n".encode("latin-1")
USAGE = re.compile(r"^usage: wordcount \[[^\]]*--chars[^\]]*\] FILE$")
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
    (tmp_path / "windows.txt").write_bytes(b"\xef\xbb\xbf" + NOTES.replace(b"\n", b"\r\n"))
    (tmp_path / "hello.txt").write_bytes(HELLO)
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


def _assert_usage(code: int, out: str, err: str, *, line: str = "\n") -> list[str]:
    """Check that a result is a usage error.

    Args:
        code: The exit code.
        out: Standard output.
        err: Standard error.
        line: The line break that ends the lines of `err`.

    Returns:
        The two lines of standard error.
    """
    assert code == 2
    assert out == ""
    lines = err.split(line)
    assert len(lines) == 3
    assert lines[2] == ""
    assert lines[0].startswith("usage: wordcount ")
    assert "--chars" in lines[0]
    assert lines[1].startswith("wordcount: error: ")
    return lines[:2]


def _assert_ok(result: tuple[int, str, str], out: str) -> None:
    """Check a successful result.

    Args:
        result: The exit code, standard output, and standard error.
        out: The expected standard output.
    """
    assert result == (0, out, "")
    assert type(result[0]) is int


def test_f06_t18_design_examples(work: pathlib.Path, capsys: pytest.CaptureFixture[str]) -> None:
    """With `--chars`, the character count and one line break, and code 0."""
    _assert_ok(_run(capsys, ["--chars", "notes.txt"]), "31\n")
    _assert_ok(_run(capsys, ["--chars", "hello.txt"]), "4\n")


def test_f06_t19_option_after_file(work: pathlib.Path, capsys: pytest.CaptureFixture[str]) -> None:
    """The option may come after the file, and given twice it counts once."""
    _assert_ok(_run(capsys, ["notes.txt", "--chars"]), "31\n")
    _assert_ok(_run(capsys, ["--chars", "--chars", "notes.txt"]), "31\n")


def _snapshot(directory: pathlib.Path) -> dict[str, bytes]:
    """Read the names and bytes of every file in a folder.

    Args:
        directory: The folder.

    Returns:
        A mapping of each file name to its bytes, and of each folder to empty bytes.
    """
    return {p.name: (p.read_bytes() if p.is_file() else b"") for p in sorted(directory.iterdir())}


def test_f06_t20_keeps_no_state(
    work: pathlib.Path,
    capsys: pytest.CaptureFixture[str],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The option changes only what is counted, and `main` keeps no state."""
    monkeypatch.setattr(sys, "argv", ["wordcount", "unchanged"])
    before = _snapshot(work)
    cwd = pathlib.Path.cwd()
    calls = [
        (["--chars", "notes.txt"], (0, "31\n", "")),
        (["notes.txt"], (0, "4\n", "")),
        (["--chars", "missing.txt"], (2, "", "wordcount: missing.txt: no such file\n")),
        (["--chars", "latin1.txt"], (2, "", "wordcount: latin1.txt: not valid UTF-8\n")),
        (["--chars", "notes.txt"], (0, "31\n", "")),
    ]
    for argv, want in calls:
        assert _run(capsys, argv) == want
    assert _snapshot(work) == before
    assert pathlib.Path.cwd() == cwd
    assert sys.argv == ["wordcount", "unchanged"]


def test_f06_t21_plain_decimal(work: pathlib.Path, capsys: pytest.CaptureFixture[str]) -> None:
    """The printed count is what `count_chars` counts, as a plain decimal number."""
    (work / "empty.txt").write_bytes(b"")
    (work / "bom.txt").write_bytes(b"\xef\xbb\xbf")
    (work / "mixed.txt").write_bytes(b"one\rtwo\r\nthree\nfour")
    (work / "many.txt").write_bytes(b"a" * 12_345)
    cases = [
        ("windows.txt", "33\n"),
        ("empty.txt", "0\n"),
        ("bom.txt", "0\n"),
        ("mixed.txt", "19\n"),
        ("many.txt", "12345\n"),
    ]
    for name, out in cases:
        _assert_ok(_run(capsys, ["--chars", name]), out)


def test_f06_t22_file_forms(
    work: pathlib.Path,
    capsys: pytest.CaptureFixture[str],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """`FILE` may be any allowed path form, and after `--` the text `--chars` is a name."""
    for name in ("sub/notes.txt", "my notes.txt", "日本語.txt", "-notes.txt", "--chars"):
        (work / name).write_bytes(NOTES)
    monkeypatch.chdir(work / "sub")
    _assert_ok(_run(capsys, ["--chars", str(work / "notes.txt")]), "31\n")
    monkeypatch.chdir(work)
    calls = [
        ["--chars", "sub/notes.txt"],
        ["--chars", "my notes.txt"],
        ["--chars", "日本語.txt"],
        ["--chars", "--", "-notes.txt"],
        ["--chars", "--", "--chars"],
    ]
    for argv in calls:
        _assert_ok(_run(capsys, argv), "31\n")


def test_f06_t23_no_such_file(work: pathlib.Path, capsys: pytest.CaptureFixture[str]) -> None:
    """Every case of "no such file" gives the line of `wordcount FILE`."""
    for name in ("missing.txt", "", "missing-folder/notes.txt", "notes.txt/inner.txt"):
        assert _run(capsys, ["--chars", name]) == (
            2,
            "",
            f"wordcount: {name}: no such file\n",
        )


def test_f06_t24_not_utf8(work: pathlib.Path, capsys: pytest.CaptureFixture[str]) -> None:
    """A file that is not valid UTF-8 gives its reason, and no count."""
    (work / "broken.txt").write_bytes(b"ok \xff\xfe")
    (work / "late.txt").write_bytes(b"a" * 100_000 + b"\xff")
    for name in ("latin1.txt", "broken.txt", "late.txt"):
        assert _run(capsys, ["--chars", name]) == (
            2,
            "",
            f"wordcount: {name}: not valid UTF-8\n",
        )


def test_f06_t25_folder(work: pathlib.Path, capsys: pytest.CaptureFixture[str]) -> None:
    """A folder gives the reason `is a folder`."""
    for name in ("sub", "."):
        assert _run(capsys, ["--chars", name]) == (2, "", f"wordcount: {name}: is a folder\n")


@pytest.mark.skipif(sys.platform == "win32", reason="a portable test cannot remove read rights")
def test_f06_t26_permission_denied(work: pathlib.Path, capsys: pytest.CaptureFixture[str]) -> None:
    """A file the process may not read gives the reason `permission denied`."""
    if hasattr(os, "geteuid") and os.geteuid() == 0:
        pytest.skip("root can read the file anyway")
    secret = work / "secret.txt"
    secret.write_bytes(b"one two")
    secret.chmod(0o000)
    try:
        result = _run(capsys, ["--chars", "secret.txt"])
    finally:
        secret.chmod(0o600)
    assert result == (2, "", "wordcount: secret.txt: permission denied\n")


def test_f06_t27_cannot_read(work: pathlib.Path, capsys: pytest.CaptureFixture[str]) -> None:
    """Any other error while opening the file gives `cannot read file`."""
    names = ["a" * 300 + ".txt"]
    if sys.platform == "win32":
        names.append("a?b.txt")
    for name in names:
        assert _run(capsys, ["--chars", name]) == (
            2,
            "",
            f"wordcount: {name}: cannot read file\n",
        )


def test_f06_t28_no_file(work: pathlib.Path, capsys: pytest.CaptureFixture[str]) -> None:
    """`--chars` with no file shows the new usage line."""
    first, second = _assert_usage(*_run(capsys, ["--chars"], exits=True))
    assert USAGE.match(first)
    assert second == "wordcount: error: the following arguments are required: FILE"


def test_f06_t29_wrong_command_lines(
    work: pathlib.Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """Every other wrong command line with the option is a usage error."""
    calls = [
        ["--char", "notes.txt"],
        ["--ch", "notes.txt"],
        ["--c", "notes.txt"],
        ["-c", "notes.txt"],
        ["--CHARS", "notes.txt"],
        ["--chars=5", "notes.txt"],
        ["--chars", "notes.txt", "notes.txt"],
        ["--chars", "-h"],
        ["--lines", "--chars", "notes.txt"],
    ]
    seconds = []
    for argv in calls:
        seconds.append(_assert_usage(*_run(capsys, argv, exits=True))[1])
    assert seconds[0] == "wordcount: error: unrecognized arguments: --char"
    assert seconds[3] == "wordcount: error: unrecognized arguments: -c"


def test_f06_t30_program_name(
    work: pathlib.Path,
    capsys: pytest.CaptureFixture[str],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The program name in every message is `wordcount`, whatever `sys.argv[0]` holds."""
    monkeypatch.setattr(sys, "argv", ["other-name.py"])
    _assert_usage(*_run(capsys, ["--char", "notes.txt"], exits=True))
    assert _run(capsys, ["--chars", "missing.txt"]) == (
        2,
        "",
        "wordcount: missing.txt: no such file\n",
    )


def test_f06_t31_reads_sys_argv(
    work: pathlib.Path,
    capsys: pytest.CaptureFixture[str],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """With no argument, `main` reads `sys.argv[1:]`, and `argv` may be a tuple."""
    monkeypatch.setattr(sys, "argv", ["wordcount", "--chars", "notes.txt"])
    code = main()
    captured = capsys.readouterr()
    assert (code, captured.out, captured.err) == (0, "31\n", "")
    _assert_ok(_run(capsys, None), "31\n")
    _assert_ok(_run(capsys, ("--chars", "notes.txt")), "31\n")


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


def test_f06_t32_program_counts(work: pathlib.Path) -> None:
    """The installed program counts characters, and still counts words without the option."""
    cases = [
        (["--chars", "notes.txt"], b"31"),
        (["notes.txt", "--chars"], b"31"),
        (["--chars", "hello.txt"], b"4"),
        (["notes.txt"], b"4"),
    ]
    for args, out in cases:
        done = _program(work, args)
        assert (done.returncode, done.stdout, done.stderr) == (0, out + _NL, b"")


def test_f06_t33_program_file_errors(tmp_path: pathlib.Path) -> None:
    """The installed program reports a file error with `--chars` with code 2."""
    done = _program(tmp_path, ["--chars", "missing.txt"])
    assert (done.returncode, done.stdout, done.stderr) == (
        2,
        b"",
        b"wordcount: missing.txt: no such file" + _NL,
    )
    (tmp_path / "latin1.txt").write_bytes(LATIN1)
    done = _program(tmp_path, ["--chars", "latin1.txt"])
    assert (done.returncode, done.stdout, done.stderr) == (
        2,
        b"",
        b"wordcount: latin1.txt: not valid UTF-8" + _NL,
    )


def test_f06_t34_program_usage_errors(work: pathlib.Path) -> None:
    """A wrong command line with the option exits with code 2 and the new usage line."""
    line = os.linesep
    for index, args in enumerate([["--char", "notes.txt"], ["--chars"], ["-c", "notes.txt"]]):
        done = _program(work, args)
        assert done.returncode == 2
        assert done.stdout == b""
        first, second = _assert_usage(done.returncode, "", done.stderr.decode(), line=line)
        assert USAGE.match(first)
        if index == 0:
            assert second == "wordcount: error: unrecognized arguments: --char"


def test_f06_t35_program_arguments(work: pathlib.Path) -> None:
    """The arguments reach the program as Troy types them, with `--chars`."""
    for name in ("my notes.txt", "日本語.txt", "-notes.txt"):
        (work / name).write_bytes(NOTES)
    cases = [
        ["--chars", "my notes.txt"],
        ["--chars", "日本語.txt"],
        ["--chars", "--", "-notes.txt"],
    ]
    for args in cases:
        done = _program(work, args)
        assert (done.returncode, done.stdout, done.stderr) == (0, b"31" + _NL, b"")
