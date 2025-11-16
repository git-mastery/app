import json
import os

import click

from app.commands.check.git import git
from app.commands.check.github import github
from app.commands.progress.constants import (
    LOCAL_FOLDER_NAME,
    PROGRESS_REPOSITORY_NAME,
    STUDENT_PROGRESS_FORK_NAME,
)
from app.utils.cli import rmtree
from app.utils.click import info, invoke_command, success, warn
from app.utils.git import add_all, commit, push
from app.utils.github_cli import (
    clone_with_custom_name,
    fork,
    get_prs,
    get_username,
    has_fork,
    pull_request,
)
from app.utils.gitmastery import (
    GITMASTERY_CONFIG_NAME,
    must_be_in_gitmastery_root,
)


@click.command()
def on() -> None:
    """
    Enables sync between your local progress and remote progress.
    """
    config = must_be_in_gitmastery_root()

    invoke_command(git)
    invoke_command(github)

    info("Syncing progress tracker")
    info(
        f"Checking if you have fork of {click.style(PROGRESS_REPOSITORY_NAME, bold=True, italic=True)}"
    )

    username = get_username()
    fork_name = STUDENT_PROGRESS_FORK_NAME.format(username=username)

    if has_fork(fork_name):
        info("You already have a fork")
    else:
        warn("You don't have a fork yet, creating one")
        fork(PROGRESS_REPOSITORY_NAME, fork_name)

    os.chdir(config.path)

    # To avoid sync issues, we save the local progress and delete the local repository
    # before cloning again. This should automatically setup the origin and upstream
    # remotes as well
    local_progress = []
    local_progress_filepath = os.path.join(LOCAL_FOLDER_NAME, "progress.json")
    if os.path.isfile(local_progress_filepath):
        with open(local_progress_filepath, "r") as file:
            local_progress = json.load(file)
    rmtree(LOCAL_FOLDER_NAME)

    clone_with_custom_name(f"{username}/{fork_name}", LOCAL_FOLDER_NAME)

    # To reconcile the difference between local and remote progress, we merge by
    # (exercise_name, start_time) which should be unique
    remote_progress = []
    if os.path.isfile(local_progress_filepath):
        with open(local_progress_filepath, "r") as file:
            remote_progress = json.load(file)

    synced_progress = []
    seen = set()
    for entry in local_progress + remote_progress:
        key = (entry["exercise_name"], entry["started_at"])
        if key in seen:
            # Seen this entry before so we can ignore it
            continue
        seen.add(key)
        synced_progress.append(entry)

    synced_progress.sort(
        key=lambda entry: (entry["exercise_name"], entry["started_at"])
    )

    with open(local_progress_filepath, "w") as file:
        file.write(json.dumps(synced_progress, indent=2))

    # If we have seen more unique entries than what was stored remotely, we need to
    # push the changes
    had_update = len(seen) > len(remote_progress)
    if had_update:
        os.chdir(LOCAL_FOLDER_NAME)
        add_all()
        commit("Sync progress with local machine")
        push("origin", "main")

    prs = get_prs(PROGRESS_REPOSITORY_NAME, "main", username)
    if len(prs) == 0:
        warn("No pull request created for progress. Creating one now")
        pull_request(
            "git-mastery/progress",
            "main",
            f"{username}:main",
            f"[{username}] Progress",
            "Automated",
        )

    success("You have setup the progress tracker for Git-Mastery!")

    config.progress_remote = True
    with open(config.path / GITMASTERY_CONFIG_NAME, "w") as gitmastery_config_file:
        gitmastery_config_file.write(json.dumps(config, indent=2))
