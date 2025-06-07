import os

import click
from cli.utils.click_utils import info, error, prompt


@click.command()
@click.pass_context
def setup(_: click.Context) -> None:
    info(
        "Welcome to Git-Mastery! We will be setting up several components of Git-Mastery to ensure an optimal experience working on the various exercises."
    )
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
    open(os.path.join(directory_name, ".gitmastery.json"), "a").close()

    info(
        f"Setup complete. Your directory is: {click.style(directory_name, bold=True, italic=True)}"
    )
