import os
import subprocess

import click


def check_binary(binary, error_message, verbose=False):
    stdout = None if verbose else subprocess.DEVNULL
    stderr = None if verbose else subprocess.DEVNULL
    if subprocess.call(["which", binary], stdout=stdout, stderr=stderr) != 0:
        click.echo(f"[ERROR] {error_message}")
        exit(1)


def is_authenticated(verbose=False):
    stdout = None if verbose else subprocess.DEVNULL
    stderr = None if verbose else subprocess.DEVNULL
    return subprocess.call(["gh", "auth", "status"], stdout=stdout, stderr=stderr) == 0


@click.group()
@click.option("--verbose", "-v", is_flag=True, help="Enable verbose output")
@click.pass_context
def cli(ctx, verbose):
    """Git Mastery CLI"""
    ctx.ensure_object(dict)
    ctx.obj["VERBOSE"] = verbose


@cli.command()
@click.pass_context
def setup(ctx):
    """Initial setup"""
    verbose = ctx.obj["VERBOSE"]
    check_binary("git", "You need to install Git", verbose)
    check_binary("gh", "You need to install the GitHub CLI", verbose)

    if not is_authenticated(verbose):
        click.echo(
            "You aren't logged in to GitHub CLI yet. Run 'gh auth login' to login"
        )
        exit(1)

    click.echo("Welcome to Git Mastery setup!")
    directory_name = click.prompt(
        "What do you want to name your problem sets directory?", default="problem-sets"
    )

    create_org = click.confirm(
        "Do you want to create a dedicated GitHub organization to store your attempts?"
    )
    if create_org:
        org_name = click.prompt("Enter the name of the organization")
        subprocess.run(
            ["gh", "repo", "create", org_name, "--private", "--confirm"], check=True
        )
        with open(".org_name", "w") as f:
            f.write(org_name)

    os.makedirs(directory_name, exist_ok=True)
    click.echo(f"Setup complete. Your directory is: {directory_name}")


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
