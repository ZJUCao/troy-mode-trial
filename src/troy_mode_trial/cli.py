"""The command line of the wordcount program."""

from collections.abc import Sequence


def main(argv: Sequence[str] | None = None) -> int:
    """Runs the `wordcount` command once.

    Reads the arguments, counts the words of the file through `count_words`,
    writes the result to standard output or an error to standard error, and
    returns the exit code. It writes with `sys.stdout.write` and
    `sys.stderr.write`, not with `print()`, and changes no global state.

    Args:
        argv: The command-line arguments after the program name, for example
            `["notes.txt"]`. `None` means `sys.argv[1:]`, which is what the
            console script passes. Exactly one item is expected: the path of
            an existing, readable UTF-8 text file.

    Returns:
        The exit code. `0` after the count and one line break were written to
        standard output. `2` after one line `wordcount: <FILE>: <reason>` was
        written to standard error. The reason is one of `no such file`,
        `is a folder`, `permission denied`, `not valid UTF-8`, or
        `cannot read file`.

    Raises:
        SystemExit: With code 2 when the arguments are wrong. argparse writes
            the usage line `usage: wordcount FILE` and its message to
            standard error first.
    """
    raise NotImplementedError
