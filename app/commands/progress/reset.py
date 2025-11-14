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
from app.utils.click import info, success, warn
from app.utils.gh_cli import delete_repo, get_prs, get_username, pull_request
from app.utils.git_cli import add_all, commit, push
from app.utils.gitmastery import (
    require_gitmastery_exercise_root,
    require_gitmastery_root,
)


@click.command()
@click.pass_context
def reset(ctx: click.Context) -> None:
    # TODO: This command should work even if the user does not have syncing on - only check if Github is set up when it is necessary
    """
    Resets the progress of the current exercise.
    """
    verbose = ctx.obj["VERBOSE"]

    download_time = datetime.now(tz=pytz.UTC)

    username = get_username(verbose)

    gitmastery_path, gitmastery_config = require_gitmastery_root(requires_root=False)
    gitmastery_exercise_path, gitmastery_exercise_config = (
        require_gitmastery_exercise_root(requires_root=True)
    )

    ctx.invoke(git)
    ctx.invoke(github)

    exercise_name = gitmastery_exercise_config.exercise_name

    os.chdir(gitmastery_exercise_path)
    info("Resetting the exercise folder")
    if gitmastery_exercise_config.exercise_repo.create_fork:
        # Remove the fork first
        username = get_username(verbose)
        exercise_fork_name = f"{username}-gitmastery-{gitmastery_exercise_config.exercise_repo.repo_title}"
        delete_repo(exercise_fork_name, verbose)

    if os.path.isdir(
        gitmastery_exercise_path / gitmastery_exercise_config.exercise_repo.repo_name
    ):
        # Only delete if the sub-folder present
        # Sub-folder may not be present if repo_type is "ignore" or if "ignore" but the
        # student has already created the sub-folder needed
        rmtree(
            gitmastery_exercise_path
            / gitmastery_exercise_config.exercise_repo.repo_name
        )

    if gitmastery_exercise_config.exercise_repo.repo_type != "ignore":
        setup_exercise_folder(download_time, gitmastery_exercise_config, verbose)
        info(
            click.style(
                f"cd {gitmastery_exercise_config.exercise_repo.repo_name}",
                bold=True,
                italic=True,
            )
        )

    if not os.path.isdir(gitmastery_path / LOCAL_FOLDER_NAME):
        warn(
            f"Progress directory is missing. Set it up again using {click.style('gitmastery progress setup', bold=True, italic=True)}"
        )
        sys.exit(0)

    os.chdir(gitmastery_path / LOCAL_FOLDER_NAME)
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

    progress_remote = gitmastery_config.get("progress_remote", False)
    if progress_remote:
        info("Updating your remote progress as well")
        add_all(verbose)
        commit(f"Reset progress for {exercise_name}", verbose)
        push("origin", "main", verbose)

        prs = get_prs(PROGRESS_REPOSITORY_NAME, "main", username, verbose)
        if len(prs) == 0:
            warn("No pull request created for progress. Creating one now")
            pull_request(
                "git-mastery/progress",
                "main",
                f"{username}:main",
                f"[{username}] Progress",
                "Automated",
                verbose,
            )

    success(
        f"Reset your progress for {click.style(exercise_name, bold=True, italic=True)}"
    )
