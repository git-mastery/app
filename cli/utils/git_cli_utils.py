import subprocess

from cli.utils.cli_utils import get_stdout_stderr


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
