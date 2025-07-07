import json
import os

import click

from app.commands.check.git import git
from app.commands.check.github import github
from app.commands.progress.constants import (
    PROGRESS_REPOSITORY_NAME,
    STUDENT_PROGRESS_FORK_NAME,
)
from app.utils.click_utils import error, info, success, warn
from app.utils.gh_cli_utils import clone, fork, get_username, has_fork
from app.utils.gitmastery_utils import (
    GITMASTERY_CONFIG_NAME,
    generate_cds_string,
    require_gitmastery_root,
)


@click.command()
@click.pass_context
def on(ctx: click.Context) -> None:
    """
    Enables sync between your local progress and remote progress.
    """
    verbose = ctx.obj["VERBOSE"]

    gitmastery_root_path, cds, gitmastery_config = require_gitmastery_root()
    if cds != 0:
        error(
            f"Use {click.style('cd ' + generate_cds_string(cds), bold=True, italic=True)} the root of the Git-Mastery exercises folder to download a new exercise."
        )

    ctx.invoke(git)
    ctx.invoke(github)

    info("Setting up progress tracker for you")
    info(
        f"Checking if you have fork of {click.style(PROGRESS_REPOSITORY_NAME, bold=True, italic=True)}"
    )

    username = get_username(verbose)
    fork_name = STUDENT_PROGRESS_FORK_NAME.format(username=username)

    if has_fork(fork_name, verbose):
        info("You already have a fork")
    else:
        warn("You don't have a fork yet, creating one")
        fork(PROGRESS_REPOSITORY_NAME, fork_name, verbose)

    info(
        f"Checking if you have a clone for {click.style(fork_name, bold=True, italic=True)}"
    )
    if os.path.isdir(fork_name):
        info("You already have the progress repository cloned")
    else:
        warn("You don't have a clone of the progress repository yet, creating one")
        clone(f"{username}/{fork_name}", verbose)

    success("You have setup the progress tracker for Git-Mastery!")

    gitmastery_config["progress_setup"] = True
    with open(
        gitmastery_root_path / GITMASTERY_CONFIG_NAME, "w"
    ) as gitmastery_config_file:
        gitmastery_config_file.write(json.dumps(gitmastery_config))
