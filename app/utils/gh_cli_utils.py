import os
import subprocess
from typing import List

from app.utils.cli_utils import get_stdout_stderr
from app.utils.click_utils import error, info


def is_github_cli_installed(verbose: bool) -> bool:
    result = subprocess.run(["gh", "--version"], capture_output=True, text=True)
    # If git is not installed yet, we should expect a 127 exit code
    # 127 indicating that the command not found: https://stackoverflow.com/questions/1763156/127-return-code-from
    if verbose:
        if result.returncode == 0:
            print(result.stdout)
        else:
            print(result.stderr)
    return result.returncode == 0


def is_authenticated(verbose: bool) -> bool:
    stdout, stderr = get_stdout_stderr(verbose)
    return subprocess.call(["gh", "auth", "status"], stdout=stdout, stderr=stderr) == 0


def has_fork(fork_name: str, verbose: bool) -> bool:
    try:
        result = subprocess.run(
            ["gh", "repo", "view", fork_name, "--json", "isFork", "--jq", ".isFork"],
            check=True,
            capture_output=True,
            env=dict(os.environ, **{"GH_PAGER": "cat"}),
        )
        if verbose:
            print(result.stdout.strip())
        return result.stdout.strip().decode("utf-8") == "true"
    except subprocess.CalledProcessError as e:
        if verbose:
            print(e.stderr)
        return False


def fork(repository_name: str, fork_name: str, verbose: bool) -> None:
    stdout, stderr = get_stdout_stderr(verbose)
    subprocess.run(
        [
            "gh",
            "repo",
            "fork",
            repository_name,
            "--default-branch-only",
            "--fork-name",
            fork_name,
        ],
        stdout=stdout,
        stderr=stderr,
    )


def clone(repository_name: str, verbose: bool) -> None:
    stdout, stderr = get_stdout_stderr(verbose)
    subprocess.run(
        ["gh", "repo", "clone", repository_name], stdout=stdout, stderr=stderr
    )


def clone_with_custom_name(repository_name: str, name: str, verbose: bool) -> None:
    stdout, stderr = get_stdout_stderr(verbose)
    subprocess.run(
        ["gh", "repo", "clone", repository_name, name], stdout=stdout, stderr=stderr
    )


def delete_repo(repository_name: str, verbose: bool) -> None:
    stdout, stderr = get_stdout_stderr(verbose)
    subprocess.run(
        ["gh", "repo", "delete", repository_name, "--yes"], stdout=stdout, stderr=stderr
    )


def pull_request(
    repo: str, base: str, head: str, title: str, body: str, verbose: bool
) -> None:
    stdout, stderr = get_stdout_stderr(verbose)
    subprocess.run(
        [
            "gh",
            "pr",
            "create",
            "--repo",
            repo,
            "--base",
            base,
            "--head",
            head,
            "--title",
            title,
            "--body",
            body,
        ],
        stdout=stdout,
        stderr=stderr,
    )


def get_prs(repo: str, head: str, owner: str, verbose: bool) -> List[str]:
    try:
        result = subprocess.run(
            [
                "gh",
                "pr",
                "list",
                "--repo",
                repo,
                "--author",
                "@me",
                "--head",
                head,
                "--json",
                "headRepositoryOwner",
                "--json",
                "url",
                "-q",
                f'.[] | select ( .headRepositoryOwner.login == "{owner}" ) | .url',
            ],
            capture_output=True,
            text=True,
            check=True,
            env=dict(os.environ, **{"GH_PAGER": "cat"}),
        )
        prs = result.stdout.strip().splitlines()
        if verbose:
            info(", ".join(prs))
        return prs
    except subprocess.CalledProcessError as e:
        if verbose:
            error(e.stderr)
        return []


def get_username(verbose: bool) -> str:
    try:
        result = subprocess.run(
            ["gh", "api", "user", "-q", ".login"],
            capture_output=True,
            text=True,
            check=True,
        )
        username = result.stdout.strip().splitlines()[0]
        if verbose:
            info(username)
        return username
    except subprocess.CalledProcessError as e:
        if verbose:
            error(e.stderr)
        return ""


def get_user_orgs(verbose: bool) -> List[str]:
    try:
        result = subprocess.run(
            [
                "gh",
                "api",
                "-H",
                "Accept: application/vnd.github+json",
                "/user/orgs",
                "--jq",
                ".[].login",
                "--paginate",
            ],
            capture_output=True,
            text=True,
            check=True,
        )
        org_names = result.stdout.strip().splitlines()
        if verbose:
            info(", ".join(org_names))
        return org_names
    except subprocess.CalledProcessError as e:
        if verbose:
            error(e.stderr)
        return []


def get_user_prs(repo: str, owner: str, verbose: bool) -> List[str]:
    try:
        result = subprocess.run(
            [
                "gh",
                "pr",
                "list",
                "--repo",
                repo,
                "--author",
                "@me",
                "--head",
                "submission",
                "--json",
                "headRepositoryOwner",
                "--json",
                "url",
                "-q",
                f'.[] | select ( .headRepositoryOwner.login == "{owner}" ) | .url',
            ],
            capture_output=True,
            text=True,
            check=True,
            env=dict(os.environ, **{"GH_PAGER": "cat"}),
        )
        prs = result.stdout.strip().splitlines()
        if verbose:
            info(", ".join(prs))
        return prs
    except subprocess.CalledProcessError as e:
        if verbose:
            error(e.stderr)
        return []
