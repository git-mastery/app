import json
import os

import click

from app.commands.check.github import github
from app.commands.progress.constants import LOCAL_FOLDER_NAME
from app.utils.click import error, info, invoke_command
from app.utils.github_cli import get_username
from app.utils.gitmastery import (
    require_gitmastery_root,
)


@click.command()
def show() -> None:
    """
    View your progress made.
    """
    gitmastery_root_path, gitmastery_config = require_gitmastery_root()
    if not gitmastery_config.get("progress_local", False):
        error("You do not have progress tracking supported.")

    if not os.path.isdir(gitmastery_root_path / LOCAL_FOLDER_NAME):
        error(
            f"Something strange has occurred, try to recreate the Git-Mastery exercise directory using {click.style('gitmastery setup', bold=True, italic=True)}"
        )

    if gitmastery_config.get("progress_remote", False):
        invoke_command(github)

    progress_file_path = gitmastery_root_path / LOCAL_FOLDER_NAME / "progress.json"
    all_progress = []
    if os.path.isfile(progress_file_path):
        with open(progress_file_path, "r") as file:
            all_progress = json.load(file)

    all_progress.sort(
        key=lambda entry: (entry["exercise_name"], -entry["completed_at"])
    )
    seen = set()
    results = []
    for i in range(len(all_progress)):
        if all_progress[i]["exercise_name"] in seen:
            continue
        seen.add(all_progress[i]["exercise_name"])
        results.append(
            f"{click.style(all_progress[i]['exercise_name'], bold=True)}: {all_progress[i]['status']}"
        )

    if gitmastery_config.get("progress_remote", False):
        invoke_command(github)
        username = get_username()
        dashboard_url = (
            f"https://git-mastery.github.io/progress-dashboard/#/dashboard/{username}"
        )
        results.append("")
        results.append(
            f"Check out your progress on the dashboard: {click.style(dashboard_url, bold=True, italic=True)}"
        )

    info("Your Git-Mastery progress:")
    click.echo("\n".join(results))
