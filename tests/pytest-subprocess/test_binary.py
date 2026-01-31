import os
import subprocess
import pytest


class BinaryRunner:
    def __init__(self, binary_path):
        """
        Initialize the binary runner.

        Args:
            binary_path: Path to binary or command like "python main.py"
        """
        self.binary_path = binary_path
        self.is_python_module = "python" in binary_path.lower()

    def run(self, args, cwd=None, env=None, timeout=30, check=False):
        """
        Run the binary with given arguments.

        Args:
            args: List of arguments to pass to the binary
            cwd: Working directory to run from
            env: Environment variables
            timeout: Timeout in seconds
            check: Whether to raise exception on non-zero exit

        Returns:
            subprocess.CompletedProcess with stdout, stderr, returncode
        """
        if self.is_python_module:
            # Split "python main.py" into command parts
            cmd = self.binary_path.split() + args
        else:
            cmd = [self.binary_path] + args

        # Merge with current environment if custom env provided
        run_env = os.environ.copy()
        if env:
            run_env.update(env)

        result = subprocess.run(
            cmd,
            cwd=cwd,
            env=run_env,
            capture_output=True,
            text=True,
            timeout=timeout,
            check=check,
        )

        return result


@pytest.fixture
def binary():
    """Get the binary runner"""
    binary_path = os.environ.get("GITMASTERY_BINARY", "python main.py")
    return BinaryRunner(binary_path)


class TestBinaryBasics:
    """Minimal tests for the compiled binary"""

    def test_binary_help_contains_main_commands(self, binary):
        result = binary.run(["--help"])

        assert result.returncode == 0
        for command in ["check", "download", "progress", "setup", "verify", "version"]:
            assert command in result.stdout

    def test_binary_version_command(self, binary):
        result = binary.run(["version"])

        assert result.returncode == 0
        assert "Git-Mastery app is" in result.stdout
