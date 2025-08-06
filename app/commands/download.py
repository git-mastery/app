import os
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional

import click
import pytz

from app.commands.check.git import git
from app.commands.check.github import github
from app.exercise_config import ExerciseConfig
from app.utils.cli import rmtree
from app.utils.click import error, info, success, warn
from app.utils.gh_cli import (
    clone_with_custom_name,
    fork,
    get_username,
    has_fork,
)
from app.utils.git_cli import add_all, commit, empty_commit, init
from app.utils.gitmastery import (
    download_file,
    execute_py_file_function_from_url,
    exercise_exists,
    get_gitmastery_file_path,
    get_variable_from_url,
    read_gitmastery_exercise_config,
    require_gitmastery_root,
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
        if download_resources:
            add_all(verbose)
            commit("Initial commit", verbose)
        else:
            empty_commit("Initial commit", verbose)

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

    require_gitmastery_root(requires_root=True)

    info(f"Checking if {exercise} is available")
    if not exercise_exists(exercise):
        error(f"Missing exercise {exercise}. Make sure you typed the name correctly.")

    info(
        f"Downloading {exercise} to {click.style(exercise + '/', bold=True, italic=True)}"
    )

    if os.path.isdir(exercise):
        warn(f"You already have {exercise}, removing it to download again")
        rmtree(exercise)

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
            ctx.invoke(git)
        except SystemExit as e:
            if e.code == 1:
                # Exited because of missing Github configuration
                # Rollback the download and remove the folder
                warn("Git is not setup. Rolling back the download")
                os.chdir("..")
                rmtree(formatted_exercise)
                warn("Setup Git before downloading this exercise")
                exit(1)

    # Check if the exercise requires Github/Github CLI to operate, if so, error if not present
    if config.requires_github:
        try:
            info("Exercise requires Github, checking if you have it setup")
            ctx.invoke(github)
        except SystemExit as e:
            if e.code == 1:
                # Exited because of missing Github configuration
                # Rollback the download and remove the folder
                warn("Github is not setup. Rolling back the download")
                os.chdir("..")
                rmtree(formatted_exercise)
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
