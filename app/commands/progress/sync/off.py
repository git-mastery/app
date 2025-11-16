import json
import os
import sys

import click

from app.commands.check.git import git
from app.commands.check.github import github
from app.commands.progress.constants import (
    PROGRESS_LOCAL_FOLDER_NAME,
    STUDENT_PROGRESS_FORK_NAME,
)
from app.utils.cli import rmtree
from app.utils.click import confirm, error, info, invoke_command
from app.utils.github_cli import delete_repo, get_username
from app.utils.gitmastery import must_be_in_gitmastery_root


@click.command()
def off() -> None:
    """
    Removes the remote progress sync for Git-Mastery.
    """
    config = must_be_in_gitmastery_root()

    if not config.progress_remote:
        error("You have not enabled sync for Git-Mastery yet.")

    result = confirm("Are you sure you want to turn off syncing?")
    if not result:
        info("Cancelling command")
        sys.exit(0)

    invoke_command(git)
    invoke_command(github)

    info("Removing fork")
    username = get_username()
    delete_repo(f"{username}/{STUDENT_PROGRESS_FORK_NAME.format(username=username)}")
    config.progress_remote = False
    with open(config.path / ".gitmastery.json", "w") as config_file:
        config_file.write(json.dumps(config))

    local_progress = []
    local_progress_filepath = os.path.join(PROGRESS_LOCAL_FOLDER_NAME, "progress.json")
    with open(local_progress_filepath, "r") as file:
        local_progress = json.load(file)

    rmtree(PROGRESS_LOCAL_FOLDER_NAME)

    # Re-create just the progress folder
    with open(local_progress_filepath, "a") as progress_file:
        progress_file.write(json.dumps(local_progress, indent=2))

    info("Successfully removed your remote sync")
