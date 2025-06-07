import os
import subprocess
from pathlib import Path

import click

from cli.utils.click_utils import error, info
from cli.utils.gitmastery_utils import (
    find_gitmastery_root,
    read_gitmastery_exercise_config,
    download_file,
    get_gitmastery_file_path,
    execute_py_file_function_from_url,
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
        subprocess.run(["git", "init"], stdout=stdout, stderr=stderr)
        subprocess.run(["git", "add", "."], stdout=stdout, stderr=stderr)
        subprocess.run(
            ["git", "commit", "-m", "Initial commit"], stdout=stdout, stderr=stderr
        )
    info("Executing download setup")
    execute_py_file_function_from_url(
        formatted_exercise, "download.py", "setup", verbose=verbose
    )
    info(f"Completed setting up {click.style(exercise, bold=True, italic=True)}")
    info("Start working on it:")
    info(click.style(f"cd {formatted_exercise}", bold=True, italic=True))
