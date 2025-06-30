import os
import shutil
import time
import webbrowser
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional

import click
import pytz

from app.commands.check import check
from app.exercise_config import ExerciseConfig
from app.utils.click_utils import error, info, success, warn
from app.utils.gh_cli_utils import (
    clone_with_custom_name,
    fork,
    get_username,
    has_fork,
)
from app.utils.git_cli_utils import add_all, commit, init
from app.utils.gitmastery_utils import (
    download_file,
    execute_py_file_function_from_url,
    find_gitmastery_root,
    get_gitmastery_file_path,
    get_variable_from_url,
    read_gitmastery_exercise_config,
)


def setup_exercise_folder(
    download_time: datetime, config: ExerciseConfig, verbose: bool
) -> None:
    exercise = config.exercise_name
    formatted_exercise = config.formatted_exercise_name

    config.downloaded_at = download_time.timestamp()

    with open(".gitmastery-exercise.json", "w") as gitmastery_exercise_file:
        gitmastery_exercise_file.write(config.to_json())

    if config.exercise_repo.repo_type == "local":
        info("Creating custom exercise folder")
        os.makedirs(config.exercise_repo.repo_name, exist_ok=True)
    elif config.exercise_repo.repo_type == "remote":
        # We have to assume that Github is checked
        info("Retrieving exercise from Github")

        username = get_username(verbose)
        exercise_repo = f"git-mastery/{config.exercise_repo.repo_title}"
        if config.exercise_repo.create_fork:
            info("Checking if you already have a fork")
            fork_name = config.exercise_fork_name(username)
            if has_fork(fork_name, verbose):
                info("You already have a fork")
            else:
                warn("You don't have a fork yet, creating one")
                fork(exercise_repo, fork_name, verbose)
            info("Creating clone of your fork")
            clone_with_custom_name(
                f"{username}/{fork_name}", config.exercise_repo.repo_name, verbose
            )
        else:
            info("Creating clone of repository")
            clone_with_custom_name(
                exercise_repo, config.exercise_repo.repo_name, verbose
            )

    os.chdir(config.exercise_repo.repo_name)
    download_resources: Optional[Dict[str, str]] = get_variable_from_url(
        formatted_exercise, "download.py", "__resources__", {}
    )
    if download_resources and len(download_resources) > 0:
        info("Downloading resources for the exercise...")

    if download_resources:
        for resource, path in download_resources.items():
            os.makedirs(Path(path).parent, exist_ok=True)
            is_binary = Path(path).suffix in [".png", ".jpg", ".jpeg", ".gif"]
            # Download and load all of these resources
            download_file(
                get_gitmastery_file_path(f"{formatted_exercise}/res/{resource}"),
                path,
                is_binary,
            )

    if config.exercise_repo.init:
        init(verbose)
        add_all(verbose)
        commit("Initial commit", verbose)

    info("Executing download setup")
    execute_py_file_function_from_url(
        formatted_exercise, "download.py", "setup", {"verbose": verbose}
    )

    success(f"Completed setting up {click.style(exercise, bold=True, italic=True)}")
    info("Start working on it:")


# TODO: Think about streamlining the config location
# TODO: Maybe store the random "keys" in config
@click.command()
@click.argument("exercise")
@click.pass_context
def download(ctx: click.Context, exercise: str) -> None:
    """Download an exercise"""
    download_time = datetime.now(tz=pytz.UTC)

    verbose = ctx.obj["VERBOSE"]

    formatted_exercise = exercise.replace("-", "_")

    # Check to make sure that they are currently in the root of a gitmastery exercises
    # folder, denoted by the .gitmastery.json file
    gitmastery_root = find_gitmastery_root()
    if gitmastery_root is None:
        error(
            f"You are not in a Git-Mastery exercises folder. Navigate to an appropriate folder or use {click.style('gitmastery setup', bold=True, italic=True)}"
        )

    # Just asserting since mypy doesn't recognize that error will exit the program
    assert gitmastery_root is not None
    _, steps_to_cd = gitmastery_root
    if steps_to_cd != 0:
        cd = "/".join([".."] * steps_to_cd)
        error(
            f"Use {click.style('cd ' + cd, bold=True, italic=True)} the root of the Git-Mastery exercises folder to download a new exercise."
        )

    info(f"Downloading {exercise}...")

    info(
        f"Downloaded {exercise} to {click.style(exercise + '/', bold=True, italic=True)}, setting it up now..."
    )
    if not os.path.isdir(exercise):
        os.makedirs(exercise)

    os.chdir(exercise)
    info("Downloading base files...")
    base_files = [".gitmastery-exercise.json", "README.md"]
    for file in base_files:
        download_file(
            get_gitmastery_file_path(f"{formatted_exercise}/{file}"), f"./{file}", False
        )
    config = read_gitmastery_exercise_config(Path("./"))

    # Check if the exercise requires Git to operate, if so, error if not present
    if config.requires_git:
        try:
            info("Exercise requires Git, checking if you have it setup")
            ctx.invoke(check, phase="git")
        except SystemExit as e:
            if e.code == 1:
                # Exited because of missing Github configuration
                # Rollback the download and remove the folder
                warn("Git is not setup. Rolling back the download")
                os.chdir("..")
                shutil.rmtree(formatted_exercise)
                warn("Setup Git before downloading this exercise")
                exit(1)

    # Check if the exercise requires Github/Github CLI to operate, if so, error if not present
    if config.requires_github:
        try:
            info("Exercise requires Github, checking if you have it setup")
            ctx.invoke(check, phase="github")
        except SystemExit as e:
            if e.code == 1:
                # Exited because of missing Github configuration
                # Rollback the download and remove the folder
                warn("Github is not setup. Rolling back the download")
                os.chdir("..")
                shutil.rmtree(formatted_exercise)
                warn("Setup Github and Github CLI before downloading this exercise")
                exit(1)

    if len(config.base_files) > 0:
        info("Downloading base files...")

    for resource, path in config.base_files.items():
        os.makedirs(Path(path).parent, exist_ok=True)
        is_binary = Path(path).suffix in [".png", ".jpg", ".jpeg", ".gif"]
        # Download and load all of these resources
        download_file(
            get_gitmastery_file_path(f"{formatted_exercise}/res/{resource}"),
            path,
            is_binary,
        )

    setup_exercise_folder(download_time, config, verbose)
    info(
        click.style(
            f"cd {exercise}/{config.exercise_repo.repo_name}", bold=True, italic=True
        )
    )

    info("Opening instructions in your browser in a moment...")
    # We add a temporary delay so people can read the message
    time.sleep(2)
    url = f"https://git-mastery.github.io/exercises/{formatted_exercise}"

    webbrowser.open(url, new=0, autoraise=True)
