from dataclasses import dataclass
from typing import List, Self
import re


@dataclass(frozen=True)
class RunResult:
    """Represents the result of running a command-line process."""

    stdout: str
    stderr: str
    returncode: int
    command: List[str]

    def assert_success(self) -> Self:
        """Assert the command exited with code 0."""
        ERROR_MSG = (
            f"Expected exit code 0, got {self.returncode}\n"
            f"Command: {' '.join(self.command)}\n"
            f"stdout:\n{self.stdout}\n"
            f"stderr:\n{self.stderr}"
        )
        assert self.returncode == 0, ERROR_MSG
        return self

    def assert_stdout_contains(self, text: str) -> Self:
        """Assert stdout contains the given text."""
        ERROR_MSG = (
            f"Expected stdout to contain {text!r}\nActual stdout:\n{self.stdout}"
        )
        assert text in self.stdout, ERROR_MSG
        return self

    def assert_stdout_matches(self, pattern: str, flags: int = 0) -> Self:
        """Assert stdout matches a regex pattern."""
        ERROR_MSG = (
            f"Expected stdout to match pattern {pattern!r}\n"
            f"Actual stdout:\n{self.stdout}"
        )
        assert re.search(pattern, self.stdout, flags), ERROR_MSG
        return self
