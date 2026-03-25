from ..result import RunResult


def test_check_git(check_results: RunResult) -> None:
    """check git command output indicates git is installed and configured."""
    check_results.assert_stdout_contains("Git is installed and configured")


def test_check_github(check_results: RunResult) -> None:
    """check github command output indicates Github CLI is installed and configured."""
    check_results.assert_stdout_contains("Github CLI is installed and configured")
