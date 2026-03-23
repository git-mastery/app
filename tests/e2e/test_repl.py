from .runner import BinaryRunner


def test_repl(runner: BinaryRunner) -> None:
    """REPL starts, handles shell commands, and dispatches /command syntax."""
    result = runner.run(
        [],
        stdin_text="echo hello_repl_test\n/version\n/exit\n",
        timeout=30,
    )
    result.assert_success()
    result.assert_stdout_contains("Welcome to the Git-Mastery REPL!")
    result.assert_stdout_matches(r"gitmastery \[.+\]>")
    result.assert_stdout_contains("hello_repl_test")
    result.assert_stdout_contains("Git-Mastery app is")
    result.assert_stdout_matches(r"v\d+\.\d+\.\d+")
