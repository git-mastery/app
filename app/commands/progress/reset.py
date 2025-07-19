import json
import os
import shutil
import sys
from datetime import datetime

import click
import pytz

from app.commands.check.git import git
from app.commands.check.github import github
from app.commands.download import setup_exercise_folder
from app.commands.progress.constants import (
    LOCAL_FOLDER_NAME,
)
from app.utils.click import error, info, success, warn
from app.utils.gh_cli import delete_repo, get_username
from app.utils.gitmastery import (
    require_gitmastery_exercise_root,
    require_gitmastery_root,
)


@click.command()
@click.pass_context
def reset(ctx: click.Context) -> None:
    """
    Resets the progress of the current exercise.
    """
    verbose = ctx.obj["VERBOSE"]

    download_time = datetime.now(tz=pytz.UTC)

    username = get_username(verbose)

    ctx.invoke(git)
    ctx.invoke(github)

    gitmastery_path, _ = require_gitmastery_root(requires_root=False)
    gitmastery_exercise_path, gitmastery_exercise_config = (
        require_gitmastery_exercise_root(requires_root=True)
    )

    exercise_name = gitmastery_exercise_config.exercise_name

    os.chdir(gitmastery_exercise_path)
    info("Resetting the exercise folder")
    if gitmastery_exercise_config.exercise_repo.create_fork:
        # Remove the fork first
        username = get_username(verbose)
        exercise_fork_name = f"{username}-gitmastery-{gitmastery_exercise_config.exercise_repo.repo_title}"
        delete_repo(exercise_fork_name, verbose)
    shutil.rmtree(
        gitmastery_exercise_path / gitmastery_exercise_config.exercise_repo.repo_name
    )
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

    success(
        f"Reset your progress for {click.style(exercise_name, bold=True, italic=True)}"
    )
