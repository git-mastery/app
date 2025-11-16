import click

from app.utils.click import error, info, success
from app.utils.github_cli import (
    has_delete_repo_scope,
    is_authenticated,
    is_github_cli_installed,
)


@click.command()
def github() -> None:
    """
    Verifies if Github and Github CLI is installed and setup for Git-Mastery.
    """
    info("Checking that you have Github CLI is installed and configured")

    if is_github_cli_installed():
        info("Github CLI is installed")
    else:
        error("Github CLI is not installed yet")

    if is_authenticated():
        info("You have authenticated Github CLI")
    else:
        error("You have not authenticated Github CLI")

    if has_delete_repo_scope():
        info("You have authenticated Github CLI with the 'delete_repo' scope")
    else:
        error(
            "You need to authenticate Github CLI with the 'delete_repo' scope. Do so via 'gh auth refresh -s delete_repo'"
        )

    success("Github CLI is installed and configured")
