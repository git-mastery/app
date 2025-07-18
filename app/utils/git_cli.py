from typing import Optional

from app.utils.command import run


def init(verbose: bool) -> None:
    run(["git", "init", "--initial-branch=main"], verbose)


def add_all(verbose: bool) -> None:
    run(["git", "add", "."], verbose)


def commit(message: str, verbose: bool) -> None:
    run(["git", "commit", "-m", message], verbose)


def empty_commit(message: str, verbose: bool) -> None:
    run(["git", "commit", "-m", message, "--allow-empty"], verbose)


def push(remote: str, branch: str, verbose: bool) -> None:
    run(["git", "push", "-u", remote, branch], verbose)


def is_git_installed(verbose: bool) -> bool:
    # If git is not installed yet, we should expect a 127 exit code
    # 127 indicating that the command not found: https://stackoverflow.com/questions/1763156/127-return-code-from
    result = run(["git", "--version"], verbose)
    return result.is_success()


def remove_remote(remote: str, verbose: bool) -> None:
    run(["git", "remote", "remove", remote], verbose)


def add_remote(remote: str, url: str, verbose: bool) -> None:
    run(["git", "remote", "add", remote, url], verbose)


def get_git_config(key: str, verbose: bool) -> Optional[str]:
    result = run(["git", "config", "--global", "--get", key], verbose)
    if result.is_success() and result.stdout:
        return result.stdout
    else:
        return None
