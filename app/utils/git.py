from typing import Optional

from app.utils.command import run


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


def is_git_installed() -> bool:
    # If git is not installed yet, we should expect a 127 exit code
    # 127 indicating that the command not found: https://stackoverflow.com/questions/1763156/127-return-code-from
    result = run(["git", "--version"])
    return result.is_success()


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
