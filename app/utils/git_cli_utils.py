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


def empty_commit(message: str, verbose: bool) -> None:
    stdout, stderr = get_stdout_stderr(verbose)
    subprocess.run(
        ["git", "commit", "-m", message, "--allow-empty"], stdout=stdout, stderr=stderr
    )


def push(remote: str, branch: str, verbose: bool) -> None:
    stdout, stderr = get_stdout_stderr(verbose)
    subprocess.run(["git", "push", "-u", remote, branch], stdout=stdout, stderr=stderr)


def is_git_installed(verbose: bool) -> bool:
    # If git is not installed yet, we should expect a 127 exit code
    # 127 indicating that the command not found: https://stackoverflow.com/questions/1763156/127-return-code-from
    result = subprocess.run(["git", "--version"], capture_output=True, text=True)
    if verbose:
        if result.returncode == 0:
            print(result.stdout)
        else:
            print(result.stderr)
    return result.returncode == 0


def remove_remote(remote: str, verbose: bool) -> None:
    stdout, stderr = get_stdout_stderr(verbose)
    subprocess.run(["git", "remote", "remove", remote], stdout=stdout, stderr=stderr)


def add_remote(remote: str, url: str, verbose: bool) -> None:
    stdout, stderr = get_stdout_stderr(verbose)
    subprocess.run(["git", "remote", "add", remote, url], stdout=stdout, stderr=stderr)


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
