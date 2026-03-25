from .result import RunResult


def test_version(check_results: RunResult) -> None:
    """Test the version command output."""
    check_results.assert_stdout_contains("Git-Mastery app is")
    check_results.assert_stdout_matches(r"v\d+\.\d+\.\d+")
