import os
import shutil
import subprocess
from pathlib import Path

import click

from cli.commands.check import check
from cli.utils.click_utils import error, info, success, warn
from cli.utils.git_cli_utils import add_all, commit, init
from cli.utils.gitmastery_utils import (
    download_file,
    execute_py_file_function_from_url,
    find_gitmastery_root,
    get_gitmastery_file_path,
    read_gitmastery_exercise_config,
)


@click.command()
@click.argument("exercise")
@click.pass_context
def download(ctx: click.Context, exercise: str) -> None:
    """Download an exercise"""
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

    stdout = None if verbose else subprocess.DEVNULL
    stderr = None if verbose else subprocess.DEVNULL

    info(
        f"Downloaded {exercise} to {click.style(formatted_exercise + '/', bold=True, italic=True)}, setting it up now..."
    )
    if not os.path.isdir(formatted_exercise):
        os.makedirs(formatted_exercise)

    os.chdir(formatted_exercise)
    info("Downloading base files...")
    base_files = [
        ".gitmastery-exercise.json",
        "README.md",
    ]
    for file in base_files:
        download_file(
            get_gitmastery_file_path(f"{formatted_exercise}/{file}"), f"./{file}", False
        )
    config = read_gitmastery_exercise_config(Path("./"))

    # Check if the exercise requires Git to operate, if so, error if not present
    if config.get("requires_repo", True):
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
    if config.get("requires_github", False):
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

    if len(config.get("resources", {})) > 0:
        info("Downloading resources...")

    for resource, path in config.get("resources", {}).items():
        os.makedirs(Path(path).parent, exist_ok=True)
        is_binary = Path(path).suffix in [".png", ".jpg", ".jpeg", ".gif"]
        # Download and load all of these resources
        download_file(
            get_gitmastery_file_path(f"{formatted_exercise}/res/{resource}"),
            path,
            is_binary,
        )

    if config.get("requires_repo", True):
        info("Setting up exercise with Git")
        init(verbose)
        add_all(verbose)
        commit("Initial commit", verbose)
    info("Executing download setup")
    execute_py_file_function_from_url(
        formatted_exercise, "download.py", "setup", verbose=verbose
    )
    success(f"Completed setting up {click.style(exercise, bold=True, italic=True)}")
    info("Start working on it:")
    info(click.style(f"cd {formatted_exercise}", bold=True, italic=True))
