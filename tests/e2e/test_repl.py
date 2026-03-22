from .result import RunResult
from .runner import BinaryRunner


def _run_repl(runner: BinaryRunner, stdin_text: str = "") -> RunResult:
    return runner.run([], stdin_text=stdin_text, timeout=10)


def test_repl_invocation(runner: BinaryRunner) -> None:
    """REPL starts, shows intro message and prompt."""
    result = _run_repl(runner, stdin_text="/exit\n")
    result.assert_success()
    result.assert_stdout_contains("Welcome to the Git-Mastery REPL!")
    result.assert_stdout_matches(r"gitmastery \[.+\]>")


def test_repl_shell_command(runner: BinaryRunner) -> None:
    """Shell commands are passed through and executed."""
    result = _run_repl(runner, stdin_text="echo hello_repl_test\n")
    result.assert_success()
    result.assert_stdout_contains("hello_repl_test")


def test_repl_slash_prefix_dispatches_gitmastery_command(runner: BinaryRunner) -> None:
    """/command syntax is converted to 'gitmastery command' by the REPL."""
    result = _run_repl(runner, stdin_text="/version\n")
    result.assert_success()
    result.assert_stdout_contains("Git-Mastery app is")
    result.assert_stdout_matches(r"v\d+\.\d+\.\d+")
