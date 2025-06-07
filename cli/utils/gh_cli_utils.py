import os
import subprocess
from typing import List

from cli.utils.click_utils import error, info


def is_authenticated(verbose: bool = False) -> bool:
    stdout = None if verbose else subprocess.DEVNULL
    stderr = None if verbose else subprocess.DEVNULL
    return subprocess.call(["gh", "auth", "status"], stdout=stdout, stderr=stderr) == 0


def has_fork(fork_name: str, verbose: bool = False) -> bool:
    stdout = None if verbose else subprocess.DEVNULL
    stderr = None if verbose else subprocess.DEVNULL
    try:
        subprocess.run(
            ["gh", "repo", "view", fork_name], check=True, stdout=stdout, stderr=stderr
        )
        return True
    except subprocess.CalledProcessError:
        return False


def get_username(verbose: bool = False) -> str:
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


def get_user_orgs(verbose: bool = False) -> List[str]:
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


def get_user_prs(repo: str, owner: str, verbose: bool = False) -> List[str]:
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
