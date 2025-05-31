import os
import subprocess
from typing import Any, List, Optional

import click


def error(message: str) -> None:
    click.echo(
        f"{click.style(' ERROR ', fg='black', bg='bright_red', bold=True)} {message}"
    )
    exit(1)


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
        "What do you want to name your problem sets directory?", default="problem-sets"
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
            f"Please confirm that you wish to:\n\t1. Create the Git-Mastery folder under {click.style(directory_path, italic=True, bold=True)}\n\t2. Store all your problem sets under organization {click.style(org_name, italic=True, bold=True)}\n",
            abort=True,
        )
    else:
        confirm(
            f"Please confirm that you wish to:\n\t1. Create the Git-Mastery folder under {click.style(directory_path, italic=True, bold=True)}",
            abort=True,
        )

    info(f"Creating directory {click.style(directory_path, italic=True, bold=True)}")
    os.makedirs(directory_name, exist_ok=True)
    if org_name is not None:
        info(f"Creating .org_name for {click.style(org_name, italic=True, bold=True)}")
        with open(os.path.join(directory_name, ".org_name"), "w") as f:
            f.write(org_name)

    info("Running diagnostics to ensure that Git-Mastery is properly setup.")

    info(f"Setup complete. Your directory is: {directory_name}")


@cli.command()
@click.argument("exercise")
@click.option("--org", default=None, help="GitHub organization")
@click.pass_context
def download(ctx, exercise, org):
    """Download an exercise"""
    verbose = ctx.obj["VERBOSE"]
    check_binary("git", "You need to install Git", verbose)
    check_binary("gh", "You need to install the GitHub CLI", verbose)

    if not is_authenticated(verbose):
        click.echo("You aren't logged into GitHub CLI. Run 'gh auth login' to login.")
        exit(1)

    click.echo(f"Downloading {exercise}...")

    stdout = None if verbose else subprocess.DEVNULL
    stderr = None if verbose else subprocess.DEVNULL

    if os.path.exists(".org_name"):
        with open(".org_name", "r") as f:
            org = f.read().strip()
        subprocess.run(
            [
                "gh",
                "repo",
                "fork",
                f"git-mastery/{exercise}",
                "--org",
                org,
                "--clone",
                "--",
                "--quiet",
            ],
            stdout=stdout,
            stderr=stderr,
        )
    else:
        if not org:
            click.echo(
                "[ERROR] Please provide an organization name or run setup first."
            )
            exit(1)
        subprocess.run(
            [
                "gh",
                "repo",
                "fork",
                f"git-mastery/{exercise}",
                "--org",
                org,
                "--clone",
                "--",
                "--quiet",
            ],
            stdout=stdout,
            stderr=stderr,
        )


@cli.command()
@click.pass_context
def submit(ctx):
    """Submit an exercise"""
    verbose = ctx.obj["VERBOSE"]
    check_binary("git", "You need to install Git", verbose)
    check_binary("gh", "You need to install the GitHub CLI", verbose)

    if not is_authenticated(verbose):
        click.echo("You aren't logged into GitHub CLI. Run 'gh auth login' to login.")
        exit(1)

    exercise_name = os.path.basename(os.getcwd())
    click.echo(f"Detected exercise: {exercise_name}")

    result = subprocess.run(
        [
            "gh",
            "pr",
            "list",
            "--state",
            "open",
            "--author",
            "@me",
            "--head",
            "submission",
        ],
        capture_output=True,
        text=True,
    )
    pr_exists = result.stdout.strip()

    stdout = None if verbose else subprocess.DEVNULL
    stderr = None if verbose else subprocess.DEVNULL

    if (
        subprocess.call(
            ["git", "rev-parse", "--verify", "submission"], stdout=stdout, stderr=stderr
        )
        != 0
    ):
        click.echo("Creating 'submission' branch")
        subprocess.run(["git", "branch", "submission"], stdout=stdout, stderr=stderr)

    if not pr_exists:
        subprocess.run(
            [
                "gh",
                "pr",
                "create",
                "--base",
                "main",
                "--head",
                "submission",
                "--title",
                "submission",
                "--body",
                "submission",
            ],
            stdout=stdout,
            stderr=stderr,
        )
        click.echo("Pull request created!")
    else:
        click.echo("A submission pull request already exists.")


if __name__ == "__main__":
    cli(obj={})
