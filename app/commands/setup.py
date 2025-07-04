import json
import os

import click
from app.commands.check import check
from app.utils.click_utils import info, error, prompt


@click.command()
@click.pass_context
def setup(ctx: click.Context) -> None:
    """
    Sets up Git-Mastery for your local machine.
    """
    info(
        "Welcome to Git-Mastery! We will be setting up several components of Git-Mastery to ensure an optimal experience working on the various exercises."
    )
    ctx.invoke(check, phase="git")
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
    os.makedirs(directory_name, exist_ok=True)
    with open(os.path.join(directory_name, ".gitmastery.json"), "w") as gitmastery_file:
        gitmastery_file.write(json.dumps({}))

    info(
        f"Setup complete. Your directory is: {click.style(directory_name, bold=True, italic=True)}"
    )
    info("Next steps:")
    info(
        f"\t1. Download exercises using {click.style('gitmastery download <exercise>', bold=True, italic=True, underline=True)}"
    )
    info(
        f"\t2. Setup progress tracking using {click.style('gitmastery progress setup', bold=True, italic=True, underline=True)}"
    )
    info("Enjoy!")
