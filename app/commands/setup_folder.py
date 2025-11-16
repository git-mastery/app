import json
import os

import click

from app.commands.check.git import git
from app.commands.progress.constants import PROGRESS_LOCAL_FOLDER_NAME
from app.utils.click import error, info, invoke_command, prompt


@click.command("setup")
def setup() -> None:
    """
    Sets up Git-Mastery for your local machine.
    """
    info(
        "Welcome to Git-Mastery! We will be setting up Git-Mastery for your local machine."
    )

    invoke_command(git)
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
    os.makedirs(PROGRESS_LOCAL_FOLDER_NAME, exist_ok=True)
    with open(".gitmastery.json", "w") as gitmastery_file:
        gitmastery_file.write(
            json.dumps({"progress_local": True, "progress_remote": False})
        )

    with open("progress/progress.json", "a") as progress_file:
        progress_file.write(json.dumps([], indent=2))

    info(
        f"Setup complete. Your directory is: {click.style(directory_name, bold=True, italic=True)}"
    )
