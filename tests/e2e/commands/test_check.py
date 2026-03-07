from ..runner import BinaryRunner


def test_check_git(runner: BinaryRunner) -> None:
    """check git command output indicates git is installed and configured."""
    res = runner.run(["check", "git"])
    res.assert_success()
    res.assert_stdout_contains("Git is installed and configured")


def test_check_github(runner: BinaryRunner) -> None:
    """check github command output indicates Github CLI is installed and configured."""
    res = runner.run(["check", "github"])
    res.assert_success()
    res.assert_stdout_contains("Github CLI is installed and configured")
