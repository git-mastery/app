import subprocess
from typing import Optional

import click

from cli.utils.click_utils import error, info, success
from cli.utils.gh_cli_utils import is_authenticated


def is_git_installed(verbose: bool) -> bool:
    result = subprocess.run(["git", "--version"], capture_output=True, text=True)
    if verbose:
        if result.returncode == 0:
            print(result.stdout)
        else:
            print(result.stderr)
    return result.returncode == 0


def get_git_config(key: str, verbose: bool) -> Optional[str]:
    result = subprocess.run(
        ["git", "config", "--global", "--get", key], capture_output=True, text=True
    )
    if result.returncode == 0 and result.stdout.strip():
        if verbose:
            print(result.stdout)
        return result.stdout.strip()
    else:
        if verbose:
            print(result.stderr)
        return None


def is_github_cli_installed(verbose: bool) -> bool:
    result = subprocess.run(["gh", "--version"], capture_output=True, text=True)
    if verbose:
        if result.returncode == 0:
            print(result.stdout)
        else:
            print(result.stderr)
    return result.returncode == 0


@click.command()
@click.argument("phase")
@click.pass_context
def check(ctx: click.Context, phase: str) -> None:
    verbose = ctx.obj["VERBOSE"]
    allowed = {"git", "github"}
    phase = phase.strip().lower()
    if phase not in allowed:
        error("Select 'git' or 'github' for the phase to check")

    info(f"Checking {phase}...")

    if phase == "git":
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
    elif phase == "github":
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
