import click

from app.utils.click import error, info, success
from app.utils.gh_cli import is_authenticated, is_github_cli_installed
from app.utils.git_cli import get_git_config, is_git_installed


@click.command()
@click.pass_context
def github(ctx: click.Context) -> None:
    """
    Verifies if Github and Github CLI is installed and setup for Git-Mastery.
    """
    verbose = ctx.obj["VERBOSE"]

    info("Checking that you have Github CLI is installed and configured")

    if is_github_cli_installed(verbose):
        info("Github CLI is installed")
    else:
        error("Github CLI is not installed yet")

    if is_authenticated(verbose):
        info("You have authenticated Github CLI")
    else:
        error("You have not authenticated Github CLI")

    success("Github CLI is installed and configured")
