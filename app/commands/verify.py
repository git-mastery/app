import json
import os
from datetime import datetime
from typing import Optional, SupportsComplex

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
    LOCAL_FOLDER_NAME,
    PROGRESS_REPOSITORY_NAME,
)
from app.utils.click import error, info, warn
from app.utils.gh_cli import get_prs, get_username, pull_request
from app.utils.git_cli import add_all, commit, push
from app.utils.gitmastery import (
    execute_py_file_function_from_url,
    require_gitmastery_exercise_root,
    require_gitmastery_root,
)


def get_output_status_text(output: GitAutograderOutput) -> str:
    status = (
        "Completed"
        if output.status == GitAutograderStatus.SUCCESSFUL
        else "Incomplete"
        if output.status == GitAutograderStatus.UNSUCCESSFUL
        else "Error"
    )
    return status


def print_output(output: GitAutograderOutput) -> None:
    color = (
        "bright_green"
        if output.status == GitAutograderStatus.SUCCESSFUL
        else "bright_red"
        if output.status == GitAutograderStatus.UNSUCCESSFUL
        else "bright_yellow"
    )
    info("Verification completed.")
    info("")
    status = get_output_status_text(output)
    info(f"{click.style('Status:', bold=True)} {click.style(status, fg=color)}")
    info(click.style("Comments:", bold=True))
    print("\n".join([f"\t- {comment}" for comment in (output.comments or [])]))


def submit_progress(output: GitAutograderOutput, verbose: bool) -> None:
    username = get_username(verbose)

    gitmastery_root_path, gitmastery_config = require_gitmastery_root()
    progress_local = gitmastery_config.get("progress_local", False)

    if not progress_local:
        warn(
            f"Something strange has occurred, try to recreate the Git-Mastery exercise directory using {click.style('gitmastery setup', bold=True, italic=True)}"
        )
        return

    if not os.path.isdir(gitmastery_root_path / LOCAL_FOLDER_NAME):
        error(
            f"Something strange has occurred, try to recreate the Git-Mastery exercise directory using {click.style('gitmastery setup', bold=True, italic=True)}"
        )

    info("Saving progress of attempt")
    os.chdir(gitmastery_root_path / LOCAL_FOLDER_NAME)
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
        "status": get_output_status_text(output),
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

    progress_remote = gitmastery_config.get("progress_remote", False)
    if progress_remote:
        info("Updating your remote progress as well")
        add_all(verbose)
        commit("Update progress", verbose)
        push("origin", "main", verbose)

        prs = get_prs(PROGRESS_REPOSITORY_NAME, "main", username, verbose)
        if len(prs) == 0:
            warn("No pull request created for progress. Creating one now")
            pull_request(
                "git-mastery/progress",
                "main",
                f"{username}:main",
                f"[{username}] Progress",
                "Automated",
                verbose,
            )

    info("Updated your progress")


@click.command()
@click.pass_context
def verify(ctx: click.Context) -> None:
    """
    Verifies the state of the exercise attempt.
    """
    verbose = ctx.obj["VERBOSE"]

    started_at = datetime.now(tz=pytz.UTC)

    exercise_path, config = require_gitmastery_exercise_root()
    exercise_name = config.exercise_name
    formatted_exercise_name = config.formatted_exercise_name

    info(
        f"Starting verification of {click.style(exercise_name, bold=True, italic=True)}"
    )

    output: Optional[GitAutograderOutput]
    try:
        os.chdir(exercise_path)
        exercise = GitAutograderExercise(exercise_path)
        output = execute_py_file_function_from_url(
            formatted_exercise_name,
            "verify.py",
            "verify",
            {"exercise": exercise},  # type: ignore
        )
    except (
        GitAutograderInvalidStateException,
        GitAutograderWrongAnswerException,
    ) as e:
        output = GitAutograderOutput(
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
        output = GitAutograderOutput(
            exercise_name=exercise_name,
            started_at=started_at,
            completed_at=datetime.now(tz=pytz.UTC),
            comments=[str(e)],
            status=GitAutograderStatus.ERROR,
        )

    assert output is not None
    print_output(output)
    submit_progress(output, verbose)
