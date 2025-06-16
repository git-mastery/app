import json
import os

import click

from cli.commands.check import check
from cli.utils.click_utils import error, info, success, warn
from cli.utils.gh_cli_utils import clone, fork, get_username, has_fork
from cli.utils.gitmastery_utils import (
    GITMASTERY_CONFIG_NAME,
    find_gitmastery_root,
    read_gitmastery_config,
    find_gitmastery_exercise_root,
    read_gitmastery_exercise_config,
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

    gitmastery_root = find_gitmastery_root()
    if gitmastery_root is None:
        error(
            f"You are not in a Git-Mastery exercises folder. Navigate to an appropriate folder or use {click.style('gitmastery setup', bold=True, italic=True)}"
        )

    # Just asserting since mypy doesn't recognize that error will exit the program
    assert gitmastery_root is not None
    gitmastery_root_path, steps_to_cd = gitmastery_root
    if steps_to_cd != 0:
        cd = "/".join([".."] * steps_to_cd)
        error(
            f"Use {click.style('cd ' + cd, bold=True, italic=True)} the root of the Git-Mastery exercises folder to download a new exercise."
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

    gitmastery_config = read_gitmastery_config(gitmastery_root_path)
    gitmastery_config["progress_setup"] = True
    with open(
        gitmastery_root_path / GITMASTERY_CONFIG_NAME, "w"
    ) as gitmastery_config_file:
        gitmastery_config_file.write(json.dumps(gitmastery_config))


@progress.command()
@click.pass_context
def reset(ctx: click.Context) -> None:
    verbose = ctx.obj["VERBOSE"]

    username = get_username(verbose)
    fork_name = f"{username}-gitmastery-progress"

    ctx.invoke(check, phase="git")
    ctx.invoke(check, phase="github")

    gitmastery_root = find_gitmastery_root()
    if gitmastery_root is None:
        error(
            f"You are not in a Git-Mastery exercises folder. Navigate to an appropriate folder or use {click.style('gitmastery setup', bold=True, italic=True)}"
        )

    # Just asserting since mypy doesn't recognize that error will exit the program
    assert gitmastery_root is not None
    gitmastery_root_path, _ = gitmastery_root
    gitmastery_config = read_gitmastery_config(gitmastery_root_path)

    gitmastery_exercise_root = find_gitmastery_exercise_root()
    if gitmastery_exercise_root is None:
        error("You are not inside a Git-Mastery exercise folder.")

    assert gitmastery_exercise_root is not None
    gitmastery_exercise_root_path, _ = gitmastery_exercise_root
    gitmastery_exercise_config = read_gitmastery_exercise_config(
        gitmastery_exercise_root_path
    )
    exercise_name = gitmastery_exercise_config["exercise_name"]

    if gitmastery_config.get("progress_setup", False):
        error(
            f"You have not setup progress tracking Git-Mastery yet. Do so with {click.style('gitmastery progress setup', bold=True, italic=True)}"
        )

    if not os.path.isdir(gitmastery_root_path / fork_name):
        error(
            f"Progress directory is missing. Set it up again using {click.style('gitmastery progress setup', bold=True, italic=True)}"
        )

    os.chdir(gitmastery_root_path / fork_name)
    if not os.path.isfile("progress.json"):
        warn("Progress tracking file not created yet. No progress to reset.")
        return

    info(
        f"Resetting your progress for {click.style(exercise_name, bold=True, italic=True)}"
    )
    with open("progress.json", "w") as progress_file:
        progress = json.load(progress_file)
        clean_progress = []
        for entry in progress:
            if entry["exercise_name"] == exercise_name:
                continue
            clean_progress.append(entry)
        progress_file.write(json.dumps(clean_progress))

    success(
        f"Reset your progress for {click.style(exercise_name, bold=True, italic=True)}"
    )
