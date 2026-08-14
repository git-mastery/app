from .runner import BinaryRunner


def test_version(runner: BinaryRunner) -> None:
    """Test the version command output."""
    res = runner.run(["version"])
    res.assert_success()
    res.assert_stdout_contains("Git-Mastery app is")
    res.assert_stdout_matches(r"v\d+\.\d+\.\d+")
