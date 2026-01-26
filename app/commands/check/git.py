import click

from app.utils.click import error, info, success
from app.utils.git import (
    MIN_GIT_VERSION,
    get_git_config,
    get_git_version,
)


@click.command()
def git() -> None:
    """
    Verifies if Git is installed and setup for Git-Mastery.
    """
    info("Checking that you have Git installed and configured")

    git_version = get_git_version()
    if git_version is None:
        error("Git is not installed")

    info("Git is installed")

    if git_version.is_behind(MIN_GIT_VERSION):
        error(
            f"Git {git_version} is behind the minimum required version. "
            f"Please upgrade to Git {MIN_GIT_VERSION} or later. "
            f"Refer to https://git-scm.com/downloads"
        )

    info(f"Git {git_version} meets the minimum version requirement.")

    config_user_name = get_git_config("user.name")
    if not config_user_name:
        error(
            f"You do not have {click.style('user.name', bold=True)} yet. Run {click.style('git config --global user.name <name>', bold=True, italic=True)}."
        )
    else:
        info(
            f"You have set {click.style('user.name', bold=True)} as {click.style(config_user_name, bold=True, italic=True)}"
        )

    config_user_email = get_git_config("user.email")
    if not config_user_email:
        error(
            f"You do not have {click.style('user.email', bold=True)} yet. Run {click.style('git config --global user.email <email>', bold=True, italic=True)}."
        )
    else:
        info(
            f"You have set {click.style('user.email', bold=True)} as {click.style(config_user_email, bold=True, italic=True)}"
        )

    success("Git is installed and configured")
