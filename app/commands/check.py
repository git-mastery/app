import subprocess
from typing import Optional

import click

from app.utils.click_utils import error, info, success
from app.utils.gh_cli_utils import is_authenticated, is_github_cli_installed
from app.utils.git_cli_utils import get_git_config, is_git_installed


def check_git(verbose: bool) -> None:
    info("Checking that you have Git installed and configured")
    # TODO: verify that exit code is 1 on failure
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

    config_default_branch_name = get_git_config("init.defaultBranch", verbose)
    if not config_default_branch_name:
        error(
            f"You do not have {click.style('init.defaultBranch', bold=True)} yet. Run {click.style('git config --global init.defaultBranch main', bold=True, italic=True)}."
        )
    elif config_default_branch_name != "main":
        error(
            f"{click.style('user.email', bold=True)} needs to be 'main'. Run {click.style('git config --global init.defaultBranch main', bold=True, italic=True)}."
        )
    else:
        info(
            f"You have set {click.style('init.defaultBranch', bold=True)} as {click.style(config_default_branch_name, bold=True, italic=True)}"
        )

    success("Git is installed and configured")


def check_github(verbose: bool) -> None:
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


@click.command()
@click.argument("phase")
@click.pass_context
def check(ctx: click.Context, phase: str) -> None:
    """
    Verifies if Git/Github CLI is properly installed for Git-Mastery

    PHASE can either be git or github.
    """
    verbose = ctx.obj["VERBOSE"]
    allowed = {"git", "github"}
    phase = phase.strip().lower()
    if phase not in allowed:
        error("Select 'git' or 'github' for the phase to check")

    info(f"Checking {phase}...")

    if phase == "git":
        check_git(verbose)
    elif phase == "github":
        check_github(verbose)
