import json
import os
import re
import subprocess
import time
from pathlib import Path
from sys import exit
from typing import Any, Dict, List, Optional, Tuple
from urllib.parse import quote

import click
import requests


def error(message: str) -> None:
    click.echo(
        f"{click.style(' ERROR ', fg='black', bg='bright_red', bold=True)} {message}"
    )
    exit()


def info(message: str) -> None:
    click.echo(
        f"{click.style(' INFO ', fg='black', bg='bright_blue', bold=True)} {message}"
    )


def debug(message: str) -> None:
    click.echo(f"{click.style(' DEBUG ', fg='white', bg='black', bold=True)} {message}")


def warn(message: str) -> None:
    click.echo(
        f"{click.style(' WARN ', fg='black', bg='bright_yellow', bold=True)} {message}"
    )


def prompt(message: str, default: Optional[Any] = None) -> Any:
    return click.prompt(f"\n{message}", default=default)


def confirm(message: str, abort: bool = False) -> bool:
    return click.confirm(f"\n{message}", abort=abort)


def check_binary(binary: str, error_message: str, verbose: bool = False) -> None:
    stdout = None if verbose else subprocess.DEVNULL
    stderr = None if verbose else subprocess.DEVNULL
    if subprocess.call(["which", binary], stdout=stdout, stderr=stderr) != 0:
        error(error_message)


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


def find_gitmastery_root() -> Optional[Tuple[Path, int]]:
    current = Path.cwd()
    steps = 0
    for parent in [current] + list(current.parents):
        if (parent / ".gitmastery.json").is_file():
            return parent, steps
        steps += 1

    return None


def read_gitmastery_config(gitmastery_config_path: Path) -> Dict:
    with open(gitmastery_config_path / ".gitmastery.json", "r") as f:
        return json.loads(f.read())


def find_gitmastery_exercise_root() -> Optional[Tuple[Path, int]]:
    current = Path.cwd()
    steps = 0
    for parent in [current] + list(current.parents):
        if (parent / ".gitmastery-exercise.json").is_file():
            return parent, steps
        steps += 1

    return None


def read_gitmastery_exercise_config(gitmastery_exercise_config_path: Path) -> Dict:
    with open(gitmastery_exercise_config_path / ".gitmastery-exercise.json", "r") as f:
        return json.loads(f.read())


@click.group()
@click.option("--verbose", "-v", is_flag=True, help="Enable verbose output")
@click.pass_context
def cli(ctx, verbose) -> None:
    """Git Mastery CLI"""
    ctx.ensure_object(dict)
    ctx.obj["VERBOSE"] = verbose


@cli.command()
@click.pass_context
def setup(ctx: click.Context) -> None:
    """Initial setup"""
    verbose = ctx.obj["VERBOSE"]
    check_binary("git", "You need to install Git", verbose)
    check_binary("gh", "You need to install the GitHub CLI", verbose)

    if not is_authenticated(verbose):
        error("You aren't logged in to GitHub CLI yet. Run 'gh auth login' to login")

    info(
        "Welcome to Git-Mastery! We will be setting up several components of Git-Mastery to ensure an optimal experience working on the various exercises."
    )
    directory_name = prompt(
        "What do you want to name your exercises directory?",
        default="gitmastery-exercises",
    )

    if os.path.isdir(directory_name):
        error(
            f"Directory {directory_name} already exists in this folder, specify a new folder name."
        )

    directory_path = os.path.join(os.getcwd(), directory_name)

    create_org = confirm(
        "Do you want to create a dedicated GitHub organization to store your attempts?"
    )
    org_name: Optional[str] = None
    if create_org:
        info(
            "Github CLI currently does not support creating organizations on your behalf"
        )
        info("Please follow these instructions to create a new organization:")
        info(
            click.style(
                "https://docs.github.com/en/organizations/collaborating-with-groups-in-organizations/creating-a-new-organization-from-scratch",
                bold=True,
                italic=True,
            )
        )
        org_name = prompt("Enter the name of the organization")
        user_orgs = get_user_orgs(verbose)
        if org_name not in user_orgs:
            error(f"You are not part of {org_name}")

        confirm(
            f"Please confirm that you wish to:\n\t1. Create the Git-Mastery folder under {click.style(directory_path, italic=True, bold=True)}\n\t2. Store all your exercises under organization {click.style(org_name, italic=True, bold=True)}\n",
            abort=True,
        )
    else:
        confirm(
            f"Please confirm that you wish to:\n\t1. Create the Git-Mastery folder under {click.style(directory_path, italic=True, bold=True)}\n",
            abort=True,
        )

    info(f"Creating directory {click.style(directory_path, italic=True, bold=True)}")
    os.makedirs(directory_name, exist_ok=True)
    with open(os.path.join(directory_name, ".gitmastery.json"), "w") as f:
        info(
            f"Creating {click.style('.gitmastery.json', bold=True, italic=True)} with the configurations for {directory_name}"
        )
        config = {}
        if org_name is not None:
            config["org_name"] = org_name
        f.write(json.dumps(config))

    info("Running diagnostics to ensure that Git-Mastery is properly setup.")

    os.chdir(directory_name)
    ctx.invoke(download, exercise="diagnostic")
    ctx.invoke(submit)

    info(
        f"Setup complete. Your directory is: {click.style(directory_name, bold=True, italic=True)}"
    )


@cli.command()
@click.argument("exercise")
@click.pass_context
def download(ctx: click.Context, exercise: str) -> None:
    """Download an exercise"""
    verbose = ctx.obj["VERBOSE"]
    check_binary("git", "You need to install Git", verbose)
    check_binary("gh", "You need to install the GitHub CLI", verbose)

    if not is_authenticated(verbose):
        error("You aren't logged into GitHub CLI. Run 'gh auth login' to login.")

    # Check to make sure that they are currently in the root of a gitmastery exercises
    # folder, denoted by the .gitmastery.json file
    gitmastery_root = find_gitmastery_root()
    if gitmastery_root is None:
        error(
            f"You are not in a Git-Mastery exercises folder. Navigate to an appropriate folder or use {click.style('gitmastery setup', bold=True, italic=True)}"
        )

    # Just asserting since mypy doesn't recognize that error will exit the program
    assert gitmastery_root is not None
    gitmastery_root_path, steps_to_cd = gitmastery_root
    if steps_to_cd != 0:
        cd = "/".join([".."] * steps_to_cd)
        error(
            f"Use {click.style('cd ' + cd, bold=True, italic=True)} the root of the Git-Mastery exercises folder to download a new exercise."
        )

    config = read_gitmastery_config(gitmastery_root_path)

    info(f"Downloading {exercise}...")

    stdout = None if verbose else subprocess.DEVNULL
    stderr = None if verbose else subprocess.DEVNULL

    if os.path.isdir(exercise):
        error(
            f"Current Git-Mastery exercises folder already contains {exercise}. If this is not the intended exercise, remove it and try again."
        )

    info(f"Attempting to create a fork of git-mastery/{exercise}")
    info("Checking if a fork already exists")

    user = config.get("org_name", get_username())
    fork_name = f"{user}/{exercise}"
    if has_fork(fork_name):
        warn("Fork already exists. Cloning it")
        subprocess.run(["gh", "repo", "clone", fork_name], stdout=stdout, stderr=stderr)
    else:
        if "org_name" in config and config["org_name"].strip() != "":
            org = config["org_name"]
            subprocess.run(
                [
                    "gh",
                    "repo",
                    "fork",
                    f"git-mastery/{exercise}",
                    "--org",
                    org,
                    "--clone",
                ],
                stdout=stdout,
                stderr=stderr,
            )
        else:
            subprocess.run(
                [
                    "gh",
                    "repo",
                    "fork",
                    f"git-mastery/{exercise}",
                    "--clone",
                ],
                stdout=stdout,
                stderr=stderr,
            )

    info(
        f"Downloaded {exercise} to {click.style(exercise + '/', bold=True, italic=True)}, setting it up now..."
    )
    os.chdir(exercise)
    subprocess.run(["bash", "./post-download.sh"], stdout=stdout, stderr=stderr)
    info(f"Completed setting up {click.style(exercise, bold=True, italic=True)}")
    info("Start working on it:")
    info(click.style(f"cd {exercise}", bold=True, italic=True))


@cli.command()
@click.pass_context
def submit(ctx: click.Context) -> None:
    """Submit an exercise"""
    verbose = ctx.obj["VERBOSE"]

    stdout = None if verbose else subprocess.DEVNULL
    stderr = None if verbose else subprocess.DEVNULL

    check_binary("git", "You need to install Git", verbose)
    check_binary("gh", "You need to install the GitHub CLI", verbose)

    if not is_authenticated(verbose):
        error("You aren't logged into GitHub CLI. Run 'gh auth login' to login.")

    username = get_username(verbose)

    # Check to make sure that they are currently in the root of a gitmastery exercises folder,
    # denoted by the .gitmastery.json file
    gitmastery_root = find_gitmastery_root()
    if gitmastery_root is None:
        error(
            f"You are not in a Git-Mastery exercises folder. Navigate to an appropriate folder or use {click.style('gitmastery setup', bold=True, italic=True)}"
        )

    # Just asserting since mypy doesn't recognize that error will exit the program
    assert gitmastery_root is not None
    gitmastery_root_path, _ = gitmastery_root

    gitmastery_config = read_gitmastery_config(gitmastery_root_path)
    org_name = gitmastery_config.get("org_name", "")
    has_org = org_name.strip() != ""
    owner = org_name if has_org else username

    gitmastery_exercise_root = find_gitmastery_exercise_root()
    if gitmastery_exercise_root is None:
        error("You are not inside a Git-Mastery exercise folder.")

    assert gitmastery_exercise_root is not None
    gitmastery_exercise_root_path, _ = gitmastery_exercise_root
    gitmastery_exercise_config = read_gitmastery_exercise_config(
        gitmastery_exercise_root_path
    )
    exercise_name = gitmastery_exercise_config.get("exercise_name")
    exercise_repo_name = f"git-mastery/{exercise_name}"

    if (
        subprocess.call(
            ["git", "rev-parse", "--verify", "submission"], stdout=stdout, stderr=stderr
        )
        != 0
    ):
        info(f"Creating {click.style('submission', bold=True, italic=True)} branch")
        subprocess.run(["git", "branch", "submission"], stdout=stdout, stderr=stderr)

    user_prs = get_user_prs(exercise_repo_name, owner, verbose)
    pr_exists = len(user_prs) > 0

    current_branch_result = subprocess.run(
        ["git", "rev-parse", "--abbrev-ref", "HEAD"], capture_output=True, text=True
    )
    current_branch = current_branch_result.stdout.strip()

    info("Pushing all commits across all branches")
    subprocess.run(["git", "push", "--all", "origin"], stderr=stderr, stdout=stdout)
    info("Switching to submission branch")
    subprocess.run(["git", "checkout", "submission"], stdout=stdout, stderr=stderr)
    info("Creating submission")
    subprocess.run(
        ["git", "commit", "--allow-empty", "-m", "Submission"],
        stdout=stdout,
        stderr=stderr,
    )
    info("Pushing submission")
    subprocess.run(
        ["git", "push", "origin", "submission"], stdout=stdout, stderr=stderr
    )
    info(f"Switching back to {current_branch}")
    subprocess.run(["git", "checkout", current_branch], stdout=stdout, stderr=stderr)

    if not pr_exists:
        if has_org:
            info("You are using a Github Organization to attempt this exercise.")
            warn(
                "The Github CLI currently does not support creating PRs for an organization yet."
            )
            info(
                f"Create the PR via the following link and click {click.style('Create Pull Request', bold=True)}:"
            )
            info(
                click.style(
                    f"https://github.com/git-mastery/{exercise_name}/compare/main...{org_name}:{exercise_name}:submission?expand=1&body={quote('Automated Submission')}&title={quote(f'[{org_name}] [{exercise_name}] Submission')}",
                    bold=True,
                    italic=True,
                )
            )
            confirm("Have you created the pull request?")
        else:
            info("PR does not exist yet, creating a new one from your branch!")
            subprocess.run(
                [
                    "gh",
                    "pr",
                    "create",
                    "--repo",
                    f"git-mastery/{exercise_name}",
                    "--base",
                    "main",
                    "--head",
                    f"{username}:submission",
                    "--title",
                    f"[{username}] [{exercise_name}] Submission",
                    "--body",
                    "Automated submission",
                ],
                stdout=stdout,
                stderr=stderr,
            )
        info("Pull request created!")
        time.sleep(5)
    else:
        info("A PR already exists, the latest push should update it.")

    user_prs = get_user_prs(exercise_repo_name, owner, verbose)
    if len(user_prs) == 0:
        warn(
            f"You should have one PR, but we could not detect it yet. Try visiting {click.style(f'https://github.com/git-mastery/{exercise_name}/pulls', bold=True, italic=True)} to find it"
        )
        exit()

    pr_url = user_prs[0]
    info("Submission completed!")
    info(f"Visit {click.style(pr_url, bold=True, italic=True)} for feedback!")


@cli.command()
@click.argument("script", required=False)
@click.pass_context
def verify(ctx: click.Context, script: Optional[str]) -> None:
    verbose = ctx.obj["VERBOSE"]

    check_binary("git", "You need to install Git", verbose)
    check_binary("gh", "You need to install the GitHub CLI", verbose)

    if script is None:
        # Locally verify the changes
        # Check that current folder is exercise
        gitmastery_exercise_root = find_gitmastery_exercise_root()
        if gitmastery_exercise_root is None:
            error("You are not inside a Git-Mastery exercise folder.")

        assert gitmastery_exercise_root is not None
        gitmastery_exercise_root_path, _ = gitmastery_exercise_root
        gitmastery_exercise_config = read_gitmastery_exercise_config(
            gitmastery_exercise_root_path
        )
        exercise_name = gitmastery_exercise_config["exercise_name"]
        verification = gitmastery_exercise_config.get(
            "verification", f"exercise/{exercise_name}"
        )
        info(
            f"Running local verification for {click.style(exercise_name, bold=True, italic=True)} using verification script {click.style(verification, bold=True, italic=True)}"
        )
        script_url = f"https://raw.githubusercontent.com/git-mastery/local-verifications/refs/heads/main/{verification}.sh"
        response = requests.get(script_url)

        if response.status_code == 200:
            content = response.text
            info("The following output is from the local verification script:")
            subprocess.run(["bash", "-c", content])
        else:
            error(
                f"Failed to fetch {click.style(verification, bold=True, italic=True)}. Inform the Git-Mastery team."
            )
        return

    script_regex = re.compile("^(hands-on|exercise)/(.*)$")
    result = script_regex.search(script)
    if result is None:
        error("Invalid script path provided.")

    assert result is not None
    script_type = result.group(1)
    script_name = result.group(2)

    # TODO: Might want to think about how to harden this part of the application
    script_url = f"https://raw.githubusercontent.com/git-mastery/local-verifications/refs/heads/main/{script_type}/{script_name}.sh"
    info(
        f"Retrieving local verification script for {click.style(f'{script_type}/{script_name}', bold=True, italic=True)}"
    )
    response = requests.get(script_url)

    if response.status_code == 200:
        info(
            f"Successfully fetch local verification script for {click.style(f'{script_type}/{script_name}', bold=True, italic=True)}"
        )
        content = response.text
        info(
            "Running local verification, the following output is from the local verification script:"
        )
        subprocess.run(["bash", "-c", content])
    else:
        error(
            f"Failed to fetch {click.style(f'{script_type}/{script_name}', bold=True, italic=True)}. Make sure it's a valid script provided."
        )


if __name__ == "__main__":
    cli(obj={})
