import json
import os

import click
from cli.commands.check import check
from cli.utils.click_utils import info, error, prompt


@click.command()
@click.pass_context
def setup(ctx: click.Context) -> None:
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
