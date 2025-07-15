import json
import os

import click

from app.commands.check.git import git
from app.commands.progress.constants import PROGRESS_REPOSITORY_NAME
from app.utils.click_utils import error, info, prompt
from app.utils.gh_cli_utils import clone
from app.utils.git_cli_utils import remove_remote


@click.command()
@click.pass_context
def setup(ctx: click.Context) -> None:
    """
    Sets up Git-Mastery for your local machine.
    """
    verbose = ctx.obj["VERBOSE"]

    info(
        "Welcome to Git-Mastery! We will be setting up Git-Mastery for your local machine."
    )
    ctx.invoke(git)
    directory_name = prompt(
        "What do you want to name your exercises directory?",
        default="gitmastery-exercises",
    )

    if os.path.isdir(directory_name):
        error(
            f"Directory {directory_name} already exists in this folder, specify a new folder name."
        )

    directory_path = os.path.join(os.getcwd(), directory_name)

    info(f"Creating directory {click.style(directory_path, italic=True, bold=True)}")
    os.makedirs(directory_name, exist_ok=False)
    os.chdir(directory_path)

    info("Setting up your local progress tracker...")
    clone(PROGRESS_REPOSITORY_NAME, verbose)
    with open(".gitmastery.json", "w") as gitmastery_file:
        gitmastery_file.write(
            json.dumps({"progress_local": True, "progress_remote": False})
        )

    os.chdir(os.path.join(directory_path, "progress"))
    remove_remote("origin", verbose)

    info(
        f"Setup complete. Your directory is: {click.style(directory_name, bold=True, italic=True)}"
    )
