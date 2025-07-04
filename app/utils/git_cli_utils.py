import subprocess
from typing import Optional

from app.utils.cli_utils import get_stdout_stderr


def init(verbose: bool) -> None:
    stdout, stderr = get_stdout_stderr(verbose)
    subprocess.run(["git", "init"], stdout=stdout, stderr=stderr)


def add_all(verbose: bool) -> None:
    stdout, stderr = get_stdout_stderr(verbose)
    subprocess.run(["git", "add", "."], stdout=stdout, stderr=stderr)


def commit(message: str, verbose: bool) -> None:
    stdout, stderr = get_stdout_stderr(verbose)
    subprocess.run(["git", "commit", "-m", message], stdout=stdout, stderr=stderr)


def push(remote: str, branch: str, verbose: bool) -> None:
    stdout, stderr = get_stdout_stderr(verbose)
    subprocess.run(["git", "push", "-u", remote, branch], stdout=stdout, stderr=stderr)


def is_git_installed(verbose: bool) -> bool:
    result = subprocess.run(["git", "--version"], capture_output=True, text=True)
    if verbose:
        if result.returncode == 0:
            print(result.stdout)
        else:
            print(result.stderr)
    return result.returncode == 0


def get_git_config(key: str, verbose: bool) -> Optional[str]:
    result = subprocess.run(
        ["git", "config", "--global", "--get", key], capture_output=True, text=True
    )
    if result.returncode == 0 and result.stdout.strip():
        if verbose:
            print(result.stdout)
        return result.stdout.strip()
    else:
        if verbose:
            print(result.stderr)
        return None
