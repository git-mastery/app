from .runner import BinaryRunner


def test_version(runner: BinaryRunner) -> None:
    """Test the version command output."""
    res = runner.run(["version"])
    res.assert_success()
    res.assert_stdout_contains("Git-Mastery app is")
    res.assert_stdout_matches(r"v\d+\.\d+\.\d+")


def test_version_unreachable_release_check(runner: BinaryRunner) -> None:
    """Commands still succeed when the latest release cannot be fetched."""
    # Route the release check through a closed port so it cannot connect.
    # NO_PROXY is cleared because an inherited value would bypass the proxy.
    res = runner.run(
        ["version"],
        env={
            "HTTP_PROXY": "http://127.0.0.1:1",
            "HTTPS_PROXY": "http://127.0.0.1:1",
            "NO_PROXY": "",
        },
    )
    res.assert_success()
    res.assert_stdout_contains("Unable to verify the latest version release")
    res.assert_stdout_contains("Git-Mastery app is")
