import json
import sys

import click

from app.commands.check.git import git
from app.commands.check.github import github
from app.commands.progress.constants import STUDENT_PROGRESS_FORK_NAME
from app.utils.click import confirm, error, info
from app.utils.gh_cli import delete_repo, get_username
from app.utils.gitmastery import generate_cds_string, require_gitmastery_root


@click.command()
@click.pass_context
def off(ctx: click.Context) -> None:
    """
    Removes the remote progress sync for Git-Mastery.
    """
    verbose = ctx.obj["VERBOSE"]

    gitmastery_root_path, gitmastery_config = require_gitmastery_root(
        requires_root=True
    )

    if not gitmastery_config.get("progress_remote", False):
        error("You have not enabled sync for Git-Mastery yet.")

    result = confirm("Are you sure you want to turn off syncing?")
    if not result:
        info("Cancelling command")
        sys.exit(0)

    ctx.invoke(git)
    ctx.invoke(github)

    info("Removing fork")
    username = get_username(verbose)
    delete_repo(
        f"{username}/{STUDENT_PROGRESS_FORK_NAME.format(username=username)}", verbose
    )
    gitmastery_config["progress_remote"] = False
    with open(gitmastery_root_path / ".gitmastery.json", "w") as config_file:
        config_file.write(json.dumps(gitmastery_config))
    info("Successfully removed your remote sync")
