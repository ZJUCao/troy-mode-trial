---
troy-doc: "ADR-0001"
lang: "en"
version: "1.0"
updated: "2026-11-14"
status: "Approved by Troy on 2026-11-14"
mirror: "ADR-0001-wordcount-command-module.zh-CN.md"
---

# ADR-0001: The `wordcount` command lives in its own module, cli

## 1. Status

Proposed

## 2. Context

Requirements 4.0 add F04, a `wordcount FILE` command that Troy runs in PowerShell. It prints the number of words in one UTF-8 text file, counted as F03 counts them. For a missing file it prints `wordcount: missing.txt: no such file` and exits with code 1 (prototype `docs/prototypes/F04-word-count-command.md`).

Architecture 1.0 has one module, counting. It owns `src/troy_mode_trial/**`, counts the words of a text, and has one external interface, `src/troy_mode_trial/__init__.py`. It says nothing about a program that Troy starts from a shell: how the program is installed, what it writes to standard output and standard error, which exit codes it uses, or where Python exceptions turn into messages. The library side follows Q4: it lets Python's own exceptions reach the caller.

The forces:

- The library must stay usable from Troy's scripts exactly as it is. F01, F02, and F03 do not change.
- ruff's T20 rule forbids `print()` in the package, and the library must keep that guard.
- R07 checks imports against the module table. troy-check gives a file to the first module whose Owns matches it, so overlapping Owns patterns depend on row order.
- Requirements 7 allow the standard library only, and a Windows 11 and Linux run.

## 3. Decision

1. A new module, **cli**, owns `src/troy_mode_trial/cli.py`. Its only job is the command line: read the arguments, call counting, write the result or an error, and return an exit code. Its external interface is `src/troy_mode_trial/cli.py`, which no other module imports; the console script is its only caller. cli may depend on counting, and only through `src/troy_mode_trial/__init__.py`.
2. counting's Owns becomes the explicit list `src/troy_mode_trial/__init__.py` and `src/troy_mode_trial/counting.py`, so the two modules do not overlap and R07 does not depend on row order. `src/troy_mode_trial/__init__.py` never imports cli. A design that adds a file under `src/troy_mode_trial/` names the module that owns it, and the architecture's module table adds it in the same change flow.
3. `pyproject.toml` gets the table `[project.scripts]` with `wordcount = "troy_mode_trial.cli:main"`. The installer (uv or pip) makes the `wordcount` program from it, `wordcount.exe` on Windows, in the environment's scripts folder. No new dependency: hatchling, already the build backend, supports the table, and the argument parsing uses the standard library's `argparse`.
4. Error handling at the command line: cli catches only the exceptions that counting documents for a file (`OSError` and its subclasses, and `UnicodeDecodeError`), writes one line `wordcount: <FILE as typed>: <reason>` to standard error, and returns 1. A wrong command line, such as no file or two files, exits with code 2 and a usage line on standard error, as `argparse` does. Any other exception is a bug and is not caught. On success, cli returns 0. Standard output holds only the count and a line break. The F04 design fixes the reason texts and the exact `main` signature.
5. cli writes with `sys.stdout.write` and `sys.stderr.write`, not `print()`, so ruff's T20 rule stays on for the whole package with no per-file exemption.

## 4. Options considered

| Option | Pros | Cons |
| --- | --- | --- |
| A new module cli, with counting's Owns narrowed to its two files (chosen) | Counting stays a library with no output and no exit codes. R07 stops cli from reaching counting's internals and stops counting from importing cli. The command's rules have one place. | The architecture changes. counting's Owns lists files one by one, so a new file in the package needs the table updated. |
| Put the command in the module counting, in `src/troy_mode_trial/cli.py`, and only add `[project.scripts]` | No change to the module table: counting already owns `src/troy_mode_trial/**`. | Counting's job becomes counting and running a program. R07 cannot keep the library from importing command-line code. The architecture still needs rules for output and exit codes, so it changes anyway. |
| A new module cli, with counting keeping `src/troy_mode_trial/**` and cli's row put first | Counting's Owns stays one pattern. | Correct only while cli's row stays above counting's, because troy-check gives a file to the first matching row. A reordered table would silently move `cli.py` into counting. |
| A PowerShell script or function, `wordcount.ps1`, that runs `python -c` | No change to `pyproject.toml`. | Works in PowerShell only, adds a second language, has to find the right Python, and troy-mode's checks do not cover it. |

## 5. Consequences

- Troy installs the project into the `troy-mode-trial` environment once more after F04 lands (`uv pip install -e . --no-deps`), so that the installer makes `wordcount`. The command is found in PowerShell only while that environment is active, or when its scripts folder is on `PATH`.
- `pyproject.toml` changes in F04's implementation PR. CI flags every change to a dependency file (R16); this change adds no dependency.
- The module table must list each new file under `src/troy_mode_trial/`. The Architect checks this in each design review.
- F04's tests can call `main` in the process with a list of arguments and check standard output, standard error, and the returned code. A test that runs the installed `wordcount` program needs the editable install, which CI already does.
- Counting does not change. F02's `count_lines` stays in counting.

## 6. Related

- Features: F04, F03, F02
- Rules: R07, R16
- Architecture: version 1.1, the tech stack, the module table, the dependency rules, the error handling, the naming and coding rules, and the decision records
