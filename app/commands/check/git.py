import click

from app.utils.click import error, info, success
from app.utils.git_cli import get_git_config, is_git_installed


@click.command()
@click.pass_context
def git(ctx: click.Context) -> None:
    """
    Verifies if Git is installed and setup for Git-Mastery.
    """
    verbose = ctx.obj["VERBOSE"]

    info("Checking that you have Git installed and configured")
    if is_git_installed(verbose):
        info("Git is installed")
    else:
        error("Git is not installed")

    config_user_name = get_git_config("user.name", verbose)
    if not config_user_name:
        error(
            f"You do not have {click.style('user.name', bold=True)} yet. Run {click.style('git config --global user.name <name>', bold=True, italic=True)}."
        )
    else:
        info(
            f"You have set {click.style('user.name', bold=True)} as {click.style(config_user_name, bold=True, italic=True)}"
        )

    config_user_email = get_git_config("user.email", verbose)
    if not config_user_email:
        error(
            f"You do not have {click.style('user.email', bold=True)} yet. Run {click.style('git config --global user.email <email>', bold=True, italic=True)}."
        )
    else:
        info(
            f"You have set {click.style('user.email', bold=True)} as {click.style(config_user_email, bold=True, italic=True)}"
        )

    success("Git is installed and configured")
