import json
import os
from datetime import datetime
from pathlib import Path
from typing import Optional

import click
import pytz
from git_autograder import (
    GitAutograderExercise,
    GitAutograderInvalidStateException,
    GitAutograderStatus,
    GitAutograderWrongAnswerException,
)
from git_autograder.output import GitAutograderOutput

from app.commands.progress.constants import (
    PROGRESS_LOCAL_FOLDER_NAME,
    PROGRESS_REPOSITORY_NAME,
)
from app.utils.click import ClickColor, error, info, warn
from app.utils.git import add_all, commit, push
from app.utils.github_cli import get_prs, get_username, pull_request
from app.utils.gitmastery import (
    ExercisesRepo,
    Namespace,
    is_in_exercise_root,
    is_in_gitmastery_root,
)


def _get_output_status_text(output: GitAutograderOutput) -> str:
    status = (
        "Completed"
        if output.status == GitAutograderStatus.SUCCESSFUL
        else "Incomplete"
        if output.status == GitAutograderStatus.UNSUCCESSFUL
        else "Error"
    )
    return status


def _get_output_status_color(output: GitAutograderOutput) -> str:
    color = (
        ClickColor.BRIGHT_GREEN
        if output.status == GitAutograderStatus.SUCCESSFUL
        else ClickColor.BRIGHT_RED
        if output.status == GitAutograderStatus.UNSUCCESSFUL
        else ClickColor.BRIGHT_YELLOW
    )
    return color


def _print_output(output: GitAutograderOutput) -> None:
    color = _get_output_status_color(output)
    status = _get_output_status_text(output)

    info("Verification completed.")
    info("")
    info(f"{click.style('Status:', bold=True)} {click.style(status, fg=color)}")
    info(click.style("Comments:", bold=True))
    click.echo(
        "\n".join(
            [f"\t- {comment}" for comment in (output.comments or ["No comments"])]
        )
    )


def _submit_progress(output: GitAutograderOutput) -> None:
    username = get_username()

    config = is_in_gitmastery_root()
    progress_local = config.progress_local

    if not progress_local:
        warn(
            f"Something strange has occurred, try to recreate the Git-Mastery exercise directory using {click.style('gitmastery setup', bold=True, italic=True)}"
        )
        return

    if not os.path.isdir(config.path / PROGRESS_LOCAL_FOLDER_NAME):
        error(
            f"Something strange has occurred, try to recreate the Git-Mastery exercise directory using {click.style('gitmastery setup', bold=True, italic=True)}"
        )

    info("Saving progress of attempt")
    os.chdir(config.path / PROGRESS_LOCAL_FOLDER_NAME)
    if not os.path.isfile("progress.json"):
        warn("Progress tracking file not created yet, doing that now")
        with open("progress.json", "w") as progress_file:
            progress_file.write(json.dumps([]))

    entry = {
        "exercise_name": output.exercise_name,
        "started_at": output.started_at.timestamp() if output.started_at else None,
        "completed_at": output.completed_at.timestamp()
        if output.completed_at
        else None,
        "comments": output.comments,
        "status": _get_output_status_text(output),
    }
    current_progress = []
    with open("progress.json", "r") as progress_file:
        current_progress = json.loads(progress_file.read())

    # If the existing progress already contains a SUCCESSFUL, we can skip submitting the progress
    for e in current_progress:
        if e["exercise_name"] == output.exercise_name and e["status"] == "SUCCESSFUL":
            info(
                "You have already completed this exercise. Your latest submission will not be tracked"
            )
            return

    current_progress.append(entry)
    with open("progress.json", "w") as progress_file:
        progress_file.write(json.dumps(current_progress, indent=2))

    progress_remote = config.progress_remote
    if progress_remote:
        info("Updating your remote progress as well")
        add_all()
        commit("Update progress")
        push("origin", "main")

        prs = get_prs(PROGRESS_REPOSITORY_NAME, "main", username)
        if len(prs) == 0:
            warn("No pull request created for progress. Creating one now")
            pull_request(
                "git-mastery/progress",
                "main",
                f"{username}:main",
                f"[{username}] Progress",
                "Automated",
            )

    info("Updated your progress")


def _execute_verify(
    exercise_path: Path,
    exercise_name: str,
    formatted_exercise_name: str,
    started_at: datetime,
) -> GitAutograderOutput:
    with ExercisesRepo() as repo:
        try:
            os.chdir(exercise_path)
            exercise = GitAutograderExercise(exercise_path)
            namespace = Namespace.load_file_as_namespace(
                repo, f"{formatted_exercise_name}/verify.py"
            )
            return namespace.execute_function(
                "verify",
                {"exercise": exercise},  # type: ignore
            )
        except (
            GitAutograderInvalidStateException,
            GitAutograderWrongAnswerException,
        ) as e:
            return GitAutograderOutput(
                exercise_name=exercise_name,
                started_at=started_at,
                completed_at=datetime.now(tz=pytz.UTC),
                comments=[e.message] if isinstance(e.message, str) else e.message,
                status=(
                    GitAutograderStatus.ERROR
                    if isinstance(e, GitAutograderInvalidStateException)
                    else GitAutograderStatus.UNSUCCESSFUL
                ),
            )
        except Exception as e:
            # Unexpected exception
            return GitAutograderOutput(
                exercise_name=exercise_name,
                started_at=started_at,
                completed_at=datetime.now(tz=pytz.UTC),
                comments=[str(e)],
                status=GitAutograderStatus.ERROR,
            )


@click.command()
def verify() -> None:
    """
    Verifies the state of the exercise attempt.
    """
    started_at = datetime.now(tz=pytz.UTC)

    config = is_in_exercise_root()

    exercise_path = config.path
    exercise_name = config.exercise_name
    formatted_exercise_name = config.formatted_exercise_name

    info(
        f"Starting verification of {click.style(exercise_name, bold=True, italic=True)}"
    )

    output = _execute_verify(
        exercise_path, exercise_name, formatted_exercise_name, started_at
    )
    _print_output(output)
    _submit_progress(output)
