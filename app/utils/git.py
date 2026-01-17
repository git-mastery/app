import re
from typing import Optional

from app.utils.command import run
from app.utils.version import Version

MIN_GIT_VERSION = Version(2, 28, 0)


def init() -> None:
    run(["git", "init", "--initial-branch=main"])


def add_all() -> None:
    run(["git", "add", "."])


def commit(message: str) -> None:
    run(["git", "commit", "-m", message])


def empty_commit(message: str) -> None:
    run(["git", "commit", "-m", message, "--allow-empty"])


def push(remote: str, branch: str) -> None:
    run(["git", "push", "-u", remote, branch])


def get_git_version() -> Optional[Version]:
    """Get the installed git version.

    Returns None if git is not installed or version cannot be parsed.
    """
    # If git is not installed yet, we should expect a 127 exit code
    # 127 indicating that the command not found: https://stackoverflow.com/questions/1763156/127-return-code-from
    result = run(["git", "--version"])
    if not result.is_success():
        return None

    match = re.search(r"^git version (\d+\.\d+\.\d+)", result.stdout)
    if not match:
        return None

    return Version.parse(match.group(1))


def remove_remote(remote: str) -> None:
    run(["git", "remote", "remove", remote])


def add_remote(remote: str, url: str) -> None:
    run(["git", "remote", "add", remote, url])


def get_git_config(key: str) -> Optional[str]:
    result = run(["git", "config", "--global", "--get", key])
    if result.is_success() and result.stdout:
        return result.stdout
    else:
        return None
