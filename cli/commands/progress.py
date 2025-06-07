import json
import os

import click

from cli.commands.check import check
from cli.utils.click_utils import error, info, success, warn
from cli.utils.gh_cli_utils import clone, fork, get_username, has_fork
from cli.utils.gitmastery_utils import (
    GITMASTERY_CONFIG_NAME,
    find_gitmastery_root,
    read_gitmastery_config,
)

PROGRESS_REPOSITORY_NAME = "git-mastery/progress"


@click.group()
def progress() -> None:
    pass


@progress.command()
@click.pass_context
def setup(ctx: click.Context) -> None:
    verbose = ctx.obj["VERBOSE"]

    ctx.invoke(check, phase="git")
    ctx.invoke(check, phase="github")

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

    info("Setting up progress tracker for you")
    info(
        f"Checking if you have fork of {click.style(PROGRESS_REPOSITORY_NAME, bold=True, italic=True)}"
    )

    if has_fork("progress", verbose):
        info("You already have a fork")
    else:
        warn("You don't have a fork yet, creating one")
        fork(PROGRESS_REPOSITORY_NAME, verbose)

    username = get_username(verbose)

    info(
        f"Checking if you have a clone for {click.style('progress', bold=True, italic=True)}"
    )
    if os.path.isdir("progress"):
        info("You already have the progress repository cloned")
    else:
        warn("You don't have a clone of the progress repository yet, creating one")
        clone(f"{username}/progress", verbose)

    success("You have setup the progress tracker for Git-Mastery!")

    gitmastery_config = read_gitmastery_config(gitmastery_root_path)
    gitmastery_config["progress_setup"] = True
    with open(
        gitmastery_root_path / GITMASTERY_CONFIG_NAME, "w"
    ) as gitmastery_config_file:
        gitmastery_config_file.write(json.dumps(gitmastery_config))
