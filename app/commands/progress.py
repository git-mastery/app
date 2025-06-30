import json
import os
import shutil
import sys
from datetime import datetime

import click
import pytz

from app.commands.check import check
from app.commands.download import setup_exercise_folder
from app.utils.click_utils import error, info, success, warn
from app.utils.gh_cli_utils import clone, delete_repo, fork, get_username, has_fork
from app.utils.gitmastery_utils import (
    GITMASTERY_CONFIG_NAME,
    generate_cds_string,
    require_gitmastery_exercise_root,
    require_gitmastery_root,
)

PROGRESS_REPOSITORY_NAME = "git-mastery/progress"


@click.group()
def progress() -> None:
    pass


@progress.command()
@click.pass_context
def setup(ctx: click.Context) -> None:
    verbose = ctx.obj["VERBOSE"]

    username = get_username(verbose)
    fork_name = f"{username}-gitmastery-progress"

    ctx.invoke(check, phase="git")
    ctx.invoke(check, phase="github")

    gitmastery_root_path, cds, gitmastery_config = require_gitmastery_root()
    if cds != 0:
        error(
            f"Use {click.style('cd ' + generate_cds_string(cds), bold=True, italic=True)} the root of the Git-Mastery exercises folder to download a new exercise."
        )

    info("Setting up progress tracker for you")
    info(
        f"Checking if you have fork of {click.style(PROGRESS_REPOSITORY_NAME, bold=True, italic=True)}"
    )

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


@progress.command()
@click.pass_context
def reset(ctx: click.Context) -> None:
    verbose = ctx.obj["VERBOSE"]

    download_time = datetime.now(tz=pytz.UTC)

    username = get_username(verbose)
    fork_name = f"{username}-gitmastery-progress"

    ctx.invoke(check, phase="git")
    ctx.invoke(check, phase="github")

    gitmastery_path, _, gitmastery_config = require_gitmastery_root()
    gitmastery_exercise_path, cds, gitmastery_exercise_config = (
        require_gitmastery_exercise_root()
    )

    if cds > 0:
        error(
            f"Go back to the root of the exercise to reset the exercise. Use {click.style(f'cd {generate_cds_string(cds)}', bold=True, italic=True)}"
        )

    exercise_name = gitmastery_exercise_config.exercise_name

    os.chdir(gitmastery_exercise_path)
    info("Resetting the exercise folder")
    if gitmastery_exercise_config.exercise_repo.create_fork:
        # Remove the fork first
        username = get_username(verbose)
        fork_name = f"{username}-gitmastery-{gitmastery_exercise_config.exercise_repo.repo_title}"
        delete_repo(fork_name, verbose)
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

    if not gitmastery_config.get("progress_setup", False):
        error(
            f"You have not setup progress tracking Git-Mastery yet. Do so with {click.style('gitmastery progress setup', bold=True, italic=True)}"
        )

    if not os.path.isdir(gitmastery_path / fork_name):
        warn(
            f"Progress directory is missing. Set it up again using {click.style('gitmastery progress setup', bold=True, italic=True)}"
        )
        sys.exit(0)

    os.chdir(gitmastery_path / fork_name)
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
        progress_file.write(json.dumps(clean_progress))

    success(
        f"Reset your progress for {click.style(exercise_name, bold=True, italic=True)}"
    )
