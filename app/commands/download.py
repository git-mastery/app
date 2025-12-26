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
from app.utils.click import (
    error,
    get_verbose,
    info,
    invoke_command,
    success,
    warn,
)
from app.utils.git import add_all, commit, empty_commit, init
from app.utils.github_cli import (
    clone_with_custom_name,
    delete_repo,
    fork,
    get_username,
    has_fork,
)
from app.utils.gitmastery import (
    ExercisesRepo,
    Namespace,
    must_be_in_gitmastery_root,
    read_exercise_config,
)


def _download_exercise(
    exercise: str, formatted_exercise: str, download_time: datetime
) -> None:
    with ExercisesRepo() as repo:
        info(f"Checking if {exercise} is available")

        if not repo.has_file(f"{formatted_exercise}/.gitmastery-exercise.json"):
            error(
                f"Missing exercise {exercise}. Make sure you typed the name correctly."
            )

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
            repo.download_file(
                f"{formatted_exercise}/{file}",
                f"./{file}",
                False,
            )
        config = read_exercise_config(Path("./"), 0)

        # Check if the exercise requires Git to operate, if so, error if not present
        if config.requires_git:
            try:
                info("Exercise requires Git, checking if you have it setup")
                invoke_command(git)
            except SystemExit as e:
                if e.code == 1:
                    # Exited because of missing Github configuration
                    # Rollback the download and remove the folder
                    warn("Git is not setup. Rolling back the download")
                    os.chdir("..")
                    rmtree(exercise)
                    warn("Setup Git before downloading this exercise")
                    exit(1)

        # Check if the exercise requires Github/Github CLI to operate, if so, error if not present
        if config.requires_github:
            try:
                info("Exercise requires Github, checking if you have it setup")
                invoke_command(github)
            except SystemExit as e:
                if e.code == 1:
                    # Exited because of missing Github configuration
                    # Rollback the download and remove the folder
                    warn("Github is not setup. Rolling back the download")
                    os.chdir("..")
                    rmtree(exercise)
                    warn("Setup Github and Github CLI before downloading this exercise")
                    exit(1)

        if len(config.base_files) > 0:
            info("Downloading base files...")

        for resource, path in config.base_files.items():
            os.makedirs(Path(path).parent, exist_ok=True)
            is_binary = Path(path).suffix in [".png", ".jpg", ".jpeg", ".gif"]
            # Download and load all of these resources
            repo.download_file(
                f"{formatted_exercise}/res/{resource}",
                path,
                is_binary,
            )

        if config.exercise_repo.repo_type != "ignore":
            setup_exercise_folder(repo, download_time, config)
            info(
                click.style(
                    f"cd {exercise}/{config.exercise_repo.repo_name}",
                    bold=True,
                    italic=True,
                )
            )
        else:
            config.downloaded_at = download_time.timestamp()
            info(click.style(f"cd {exercise}", bold=True, italic=True))
            with open(".gitmastery-exercise.json", "w") as gitmastery_exercise_file:
                gitmastery_exercise_file.write(config.to_json())


def _download_hands_on(hands_on: str, formatted_hands_on: str) -> None:
    with ExercisesRepo() as repo:
        info(f"Checking if {hands_on} is available")

        hands_on_without_prefix = formatted_hands_on.lstrip("hp_")

        if not repo.has_file(f"hands_on/{hands_on_without_prefix}.py"):
            error(
                f"Missing hands-on {hands_on}. Make sure you typed the name correctly."
            )

        info(
            f"Downloading {hands_on} to {click.style(hands_on + '/', bold=True, italic=True)}"
        )

        if os.path.isdir(hands_on):
            warn(f"You already have {hands_on}, removing it to download again")
            rmtree(hands_on)

        os.makedirs(hands_on)
        os.chdir(hands_on)

        hands_on_namespace = Namespace.load_file_as_namespace(
            repo, f"hands_on/{hands_on_without_prefix}.py"
        )
        requires_git = hands_on_namespace.get_variable("__requires_git__", False)
        requires_github = hands_on_namespace.get_variable("__requires_github__", False)

        if requires_git:
            try:
                info("Hands-on requires Git, checking if you have it setup")
                invoke_command(git)
            except SystemExit as e:
                if e.code == 1:
                    # Exited because of missing Github configuration
                    # Rollback the download and remove the folder
                    warn("Git is not setup. Rolling back the download")
                    os.chdir("..")
                    rmtree(hands_on)
                    warn("Setup Git before downloading this hands-on")
                    exit(1)

        if requires_github:
            try:
                info("Hands-on requires Github, checking if you have it setup")
                invoke_command(github)
            except SystemExit as e:
                if e.code == 1:
                    # Exited because of missing Github configuration
                    # Rollback the download and remove the folder
                    warn("Github is not setup. Rolling back the download")
                    os.chdir("..")
                    rmtree(hands_on)
                    warn("Setup Github and Github CLI before downloading this hands-on")
                    exit(1)

        hands_on_namespace.execute_function(
            "download",
            {"verbose": get_verbose()},
        )
        success(f"Completed setting up {click.style(hands_on, bold=True, italic=True)}")


def setup_exercise_folder(
    repo: ExercisesRepo, download_time: datetime, config: ExerciseConfig
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

        username = get_username()
        exercise_repo = f"git-mastery/{config.exercise_repo.repo_title}"
        if config.exercise_repo.create_fork:
            info("Checking if you already have a fork")
            fork_name = config.exercise_fork_name(username)
            if has_fork(fork_name):
                info("You already have a fork, deleting it")
                delete_repo(fork_name)
            info("Creating fork of exercise repository")
            fork(exercise_repo, fork_name)
            info("Creating clone of your fork")
            clone_with_custom_name(
                f"{username}/{fork_name}", config.exercise_repo.repo_name
            )
        else:
            info("Creating clone of repository")
            clone_with_custom_name(exercise_repo, config.exercise_repo.repo_name)

    os.chdir(config.exercise_repo.repo_name)
    namespace = Namespace.load_file_as_namespace(
        repo, f"{formatted_exercise}/download.py"
    )
    download_resources: Optional[Dict[str, str]] = namespace.get_variable(
        "__resources__", {}
    )
    if download_resources and len(download_resources) > 0:
        info("Downloading resources for the exercise...")

    if download_resources:
        for resource, path in download_resources.items():
            os.makedirs(Path(path).parent, exist_ok=True)
            is_binary = Path(path).suffix in [".png", ".jpg", ".jpeg", ".gif"]
            # Download and load all of these resources
            repo.download_file(
                f"{formatted_exercise}/res/{resource}",
                path,
                is_binary,
            )

    if config.exercise_repo.init:
        init()
        initial_commit_message = "Set initial state"
        if download_resources:
            add_all()
            commit(initial_commit_message)
        else:
            empty_commit(initial_commit_message)

    info("Executing download setup")
    namespace.execute_function(
        "setup",
        {"verbose": get_verbose()},
    )

    success(f"Completed setting up {click.style(exercise, bold=True, italic=True)}")
    info("Start working on it:")


# TODO: Think about streamlining the config location
# TODO: Maybe store the random "keys" in config
@click.command()
@click.argument("exercise")
def download(exercise: str) -> None:
    """Download an exercise"""
    download_time = datetime.now(tz=pytz.UTC)

    formatted_exercise = exercise.replace("-", "_")
    is_hands_on = exercise.startswith("hp-")

    must_be_in_gitmastery_root()

    if is_hands_on:
        _download_hands_on(exercise, formatted_exercise)
    else:
        _download_exercise(exercise, formatted_exercise, download_time)
