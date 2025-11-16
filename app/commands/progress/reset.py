import json
import os
import sys
from datetime import datetime

import click
import pytz

from app.commands.check.git import git
from app.commands.check.github import github
from app.commands.download import setup_exercise_folder
from app.commands.progress.constants import (
    LOCAL_FOLDER_NAME,
    PROGRESS_REPOSITORY_NAME,
)
from app.utils.cli import rmtree
from app.utils.click import info, invoke_command, success, warn
from app.utils.git import add_all, commit, push
from app.utils.github_cli import delete_repo, get_prs, get_username, pull_request
from app.utils.gitmastery import (
    is_in_gitmastery_root,
    must_be_in_exercise_root,
)


@click.command()
def reset() -> None:
    # TODO: This command should work even if the user does not have syncing on - only check if Github is set up when it is necessary
    """
    Resets the progress of the current exercise.
    """
    download_time = datetime.now(tz=pytz.UTC)

    username = get_username()

    gitmastery_config = is_in_gitmastery_root()
    exercise_config = must_be_in_exercise_root()

    invoke_command(git)
    invoke_command(github)

    exercise_name = exercise_config.exercise_name

    os.chdir(exercise_config.path)
    info("Resetting the exercise folder")
    if exercise_config.exercise_repo.create_fork:
        # Remove the fork first
        exercise_fork_name = (
            f"{username}-gitmastery-{exercise_config.exercise_repo.repo_title}"
        )
        delete_repo(exercise_fork_name)

    if os.path.isdir(exercise_config.path / exercise_config.exercise_repo.repo_name):
        # Only delete if the sub-folder present
        # Sub-folder may not be present if repo_type is "ignore" or if "ignore" but the
        # student has already created the sub-folder needed
        rmtree(exercise_config.path / exercise_config.exercise_repo.repo_name)

    if exercise_config.exercise_repo.repo_type != "ignore":
        setup_exercise_folder(download_time, exercise_config)
        info(
            click.style(
                f"cd {exercise_config.exercise_repo.repo_name}",
                bold=True,
                italic=True,
            )
        )

    if not os.path.isdir(gitmastery_config.path / LOCAL_FOLDER_NAME):
        warn(
            f"Progress directory is missing. Set it up again using {click.style('gitmastery progress setup', bold=True, italic=True)}"
        )
        sys.exit(0)

    os.chdir(gitmastery_config.path / LOCAL_FOLDER_NAME)
    if not os.path.isfile("progress.json"):
        warn("Progress tracking file not created yet. No progress to reset.")
        return

    info(
        f"Resetting your progress for {click.style(exercise_name, bold=True, italic=True)}"
    )
    clean_progress = []
    with open("progress.json", "r") as progress_file:
        progress = json.load(progress_file)
        for entry in progress:
            if entry["exercise_name"] == exercise_name:
                continue
            clean_progress.append(entry)

    with open("progress.json", "w") as progress_file:
        progress_file.write(json.dumps(clean_progress, indent=2))

    progress_remote = gitmastery_config.progress_remote
    if progress_remote:
        info("Updating your remote progress as well")
        add_all()
        commit(f"Reset progress for {exercise_name}")
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

    success(
        f"Reset your progress for {click.style(exercise_name, bold=True, italic=True)}"
    )
