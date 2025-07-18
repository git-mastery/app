import re
from typing import List, Optional

from app.utils.command import run


def is_github_cli_installed(verbose: bool) -> bool:
    # If git is not installed yet, we should expect a 127 exit code
    # 127 indicating that the command not found: https://stackoverflow.com/questions/1763156/127-return-code-from
    result = run(["gh", "--version"], verbose)
    return result.is_success()


def get_https_or_ssh(verbose: bool) -> Optional[str]:
    result = run(["gh", "auth", "status"], verbose, {"GH_PAGER": "cat"})
    if result.is_success():
        regex = re.compile(r"Git operations protocol: (\w+)")
        match = regex.search(result.stdout)
        if match:
            protocol = match.group(1).lower()
            return protocol
    return None


def is_authenticated(verbose: bool) -> bool:
    return run(["gh", "auth", "status"], verbose).is_success()


def has_fork(fork_name: str, verbose: bool) -> bool:
    result = run(
        ["gh", "repo", "view", fork_name, "--json", "isFork", "--jq", ".isFork"],
        verbose,
        env={"GH_PAGER": "cat"},
    )
    return result.is_success() and result.stdout == "true"


def get_repo_ssh_url(repo: str, verbose: bool) -> Optional[str]:
    result = run(
        ["gh", "repo", "view", repo, "--json", "sshUrl", "--jq", ".sshUrl"],
        verbose,
        env={"GH_PAGER": "cat"},
    )
    if result.is_success():
        return result.stdout
    return None


def get_repo_https_url(repo: str, verbose: bool) -> Optional[str]:
    result = run(
        ["gh", "repo", "view", repo, "--json", "url", "--jq", ".url"],
        verbose,
        env={"GH_PAGER": "cat"},
    )
    if result.is_success():
        return result.stdout + ".git"
    return None


def fork(repository_name: str, fork_name: str, verbose: bool) -> None:
    run(
        [
            "gh",
            "repo",
            "fork",
            repository_name,
            "--default-branch-only",
            "--fork-name",
            fork_name,
        ],
        verbose,
    )


def clone(repository_name: str, verbose: bool) -> None:
    run(["gh", "repo", "clone", repository_name], verbose)


def clone_with_custom_name(repository_name: str, name: str, verbose: bool) -> None:
    run(["gh", "repo", "clone", repository_name, name], verbose)


def delete_repo(repository_name: str, verbose: bool) -> None:
    run(["gh", "repo", "delete", repository_name, "--yes"], verbose)


def pull_request(
    repo: str, base: str, head: str, title: str, body: str, verbose: bool
) -> None:
    run(
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
        verbose,
    )


def get_prs(repo: str, head: str, owner: str, verbose: bool) -> List[str]:
    result = run(
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
        verbose,
        env={"GH_PAGER": "cat"},
    )

    if result.is_success():
        prs = result.stdout.splitlines()
        return prs
    return []


def get_username(verbose: bool) -> str:
    result = run(["gh", "api", "user", "-q", ".login"], verbose)

    if result.is_success():
        username = result.stdout.splitlines()[0]
        return username
    return ""


def get_user_orgs(verbose: bool) -> List[str]:
    result = run(
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
        verbose,
    )
    if result.is_success():
        org_names = result.stdout.splitlines()
        return org_names
    return []


def get_user_prs(repo: str, owner: str, verbose: bool) -> List[str]:
    result = run(
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
        verbose,
        env={"GH_PAGER": "cat"},
    )
    if result.is_success():
        prs = result.stdout.splitlines()
        return prs
    return []
