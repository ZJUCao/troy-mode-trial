"""The command line of the wordcount program."""

import argparse
import pathlib
import sys
from collections.abc import Callable, Sequence

from troy_mode_trial import count_chars, count_lines, count_longest, count_words


def _reason(error: Exception, path: str) -> str:
    """Maps an exception from counting to the reason text of the error line.

    Args:
        error: An `OSError` or a `UnicodeDecodeError`.
        path: The file argument as typed. On Windows, a `PermissionError` for
            a path that names a folder is reported as a folder.

    Returns:
        One of the fixed reason texts.
    """
    if isinstance(error, UnicodeDecodeError):
        return "not valid UTF-8"
    if isinstance(error, FileNotFoundError | NotADirectoryError):
        return "no such file"
    if isinstance(error, IsADirectoryError):
        return "is a folder"
    if isinstance(error, PermissionError):
        return "is a folder" if pathlib.Path(path).is_dir() else "permission denied"
    return "cannot read file"


def _build_parser() -> argparse.ArgumentParser:
    """Builds the argument parser of the command.

    Returns:
        A parser named `wordcount` with the options `--lines`, `--chars`, and
        `--longest`, in a group that excludes them together, one positional
        argument, and no help option. Option names are not shortened. Its
        usage line is `usage: wordcount [--lines | --chars | --longest] FILE`.
    """
    parser = argparse.ArgumentParser(prog="wordcount", add_help=False, allow_abbrev=False)
    counting = parser.add_mutually_exclusive_group()
    counting.add_argument("--lines", action="store_true")
    counting.add_argument("--chars", action="store_true")
    counting.add_argument("--longest", action="store_true")
    parser.add_argument("FILE")
    return parser


def _count_function(lines: bool, chars: bool, longest: bool) -> Callable[[str], int]:
    """Picks the counting function for the command line.

    Args:
        lines: True when the arguments hold `--lines`.
        chars: True when the arguments hold `--chars`.
        longest: True when the arguments hold `--longest`.

    Returns:
        `count_lines` if `lines` is true, `count_chars` if `chars` is true,
        `count_longest` if `longest` is true, otherwise `count_words`.
    """
    if lines:
        return count_lines
    if chars:
        return count_chars
    return count_longest if longest else count_words


def main(argv: Sequence[str] | None = None) -> int:
    """Runs the `wordcount` command once.

    Reads the arguments, counts the words of the file through `count_words`,
    its lines through `count_lines` when the arguments hold `--lines`, its
    characters through `count_chars` when they hold `--chars`, or the length
    of its longest word through `count_longest` when they hold `--longest`,
    writes the
    result to standard output or an error to standard error, and returns the
    exit code. It writes with `sys.stdout.write` and `sys.stderr.write`, not
    with `print()`, and changes no global state.

    Args:
        argv: The command-line arguments after the program name, for example
            `["--lines", "notes.txt"]`, `["--chars", "notes.txt"]`,
            `["--longest", "notes.txt"]`, or `["notes.txt"]`. `None` means
            `sys.argv[1:]`, which is what the console script passes. One of
            the options `--lines`, `--chars`, or `--longest` may come before
            or after the file, but not two of them together. Exactly
            one file is expected: the path of an existing, readable UTF-8
            text file.

    Returns:
        The exit code. `0` after the count and one line break were written to
        standard output. `2` after one line `wordcount: <FILE>: <reason>` was
        written to standard error. The reason is one of `no such file`,
        `is a folder`, `permission denied`, `not valid UTF-8`, or
        `cannot read file`.

    Raises:
        SystemExit: With code 2 when the arguments are wrong, for example
            when two counting options are given. argparse writes the usage line
            `usage: wordcount [--lines | --chars | --longest] FILE` and its message to
            standard error first.

    Any other exception, apart from `OSError` and `UnicodeDecodeError`, is a
    bug and reaches the caller.
    """
    args = _build_parser().parse_args(sys.argv[1:] if argv is None else list(argv))
    path: str = args.FILE
    try:
        count = _count_function(args.lines, args.chars, args.longest)(path)
    except (OSError, UnicodeDecodeError) as error:
        sys.stderr.write(f"wordcount: {path}: {_reason(error, path)}\n")
        return 2
    sys.stdout.write(f"{count}\n")
    return 0
