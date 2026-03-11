from ..runner import BinaryRunner


def test_check_git(runner: BinaryRunner) -> None:
    """Test the check git command output."""
    res = runner.run(["check", "git"])
    res.assert_success()
    res.assert_stdout_contains("Git is installed")


def test_check_github(runner: BinaryRunner) -> None:
    """Test the check gh command output."""
    res = runner.run(["check", "github"])
    res.assert_success()
    res.assert_stdout_contains("Github CLI is installed")
