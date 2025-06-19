import json
import os
from datetime import datetime
from typing import Optional

import click
import pytz
from git_autograder import (
    GitAutograderInvalidStateException,
    GitAutograderRepo,
    GitAutograderStatus,
    GitAutograderWrongAnswerException,
)
from git_autograder.output import GitAutograderOutput

from cli.utils.click_utils import error, info, warn
from cli.utils.gh_cli_utils import get_prs, get_username, pull_request
from cli.utils.git_cli_utils import add_all, commit, push
from cli.utils.gitmastery_utils import (
    execute_py_file_function_from_url,
    find_gitmastery_exercise_root,
    find_gitmastery_root,
    read_gitmastery_config,
    read_gitmastery_exercise_config,
)


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
    info(f"{click.style('Status:', bold=True)} {click.style(output.status, fg=color)}")
    info(click.style("Comments:", bold=True))
    print("\n".join([f"\t- {comment}" for comment in (output.comments or [])]))


def submit_progress(output: GitAutograderOutput, verbose: bool) -> None:
    # TODO: handle edge cases where the student might have deleted progress themselves
    # TODO: If student does not have Github, we create a local folder for progress instead, then once setup, we connect it with fork

    username = get_username(verbose)
    progress_name = f"{username}-gitmastery-progress"

    gitmastery_root = find_gitmastery_root()
    if gitmastery_root is None:
        error(
            f"You are not in a Git-Mastery exercises folder. Navigate to an appropriate folder or use {click.style('gitmastery setup', bold=True, italic=True)}"
        )

    # Just asserting since mypy doesn't recognize that error will exit the program
    assert gitmastery_root is not None
    gitmastery_root_path, _ = gitmastery_root
    gitmastery_config = read_gitmastery_config(gitmastery_root_path)
    progress_setup = gitmastery_config.get("progress_setup", False)

    if not progress_setup:
        warn(
            f"Progress not submitted. Setup progress tracking via {click.style('gitmastery progress setup', bold=True, italic=True)}"
        )
        return

    if not os.path.isdir(gitmastery_root_path / progress_name):
        error(
            f"Progress directory is missing. Set it up again using {click.style('gitmastery progress setup', bold=True, italic=True)}"
        )

    info("Saving progress of attempt")
    os.chdir(gitmastery_root_path / progress_name)
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
        "status": output.status,
    }
    current_progress = []
    with open("progress.json", "r") as progress_file:
        current_progress = json.loads(progress_file.read())

    # If the existing progress already contains a SUCCESSFUL, we can skip submitting the progress
    for e in current_progress:
        if e["exercise_name"] == output.exercise_name and e["status"] == "SUCCESSFUL":
            warn(
                "You have already completed this exercise. Your latest submission will not be tracked"
            )
            return

    current_progress.append(entry)
    with open("progress.json", "w") as progress_file:
        progress_file.write(json.dumps(current_progress))

    add_all(verbose)
    commit("Update progress", verbose)
    push("origin", "main", verbose)

    prs = get_prs("git-mastery/progress", "main", username, verbose)
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
    verbose = ctx.obj["VERBOSE"]

    # Locally verify the changes
    # Check that current folder is exercise
    gitmastery_exercise_root = find_gitmastery_exercise_root()
    if gitmastery_exercise_root is None:
        error("You are not inside a Git-Mastery exercise folder.")

    started_at = datetime.now(tz=pytz.UTC)

    assert gitmastery_exercise_root is not None
    gitmastery_exercise_root_path, _ = gitmastery_exercise_root
    gitmastery_exercise_config = read_gitmastery_exercise_config(
        gitmastery_exercise_root_path
    )
    exercise_name = gitmastery_exercise_config["exercise_name"]
    formatted_exercise_name = exercise_name.replace("-", "_")

    info(
        f"Starting verification of {click.style(exercise_name, bold=True, italic=True)}"
    )

    requires_repo = gitmastery_exercise_config.get("requires_repo", True)
    output: Optional[GitAutograderOutput]
    try:
        os.chdir(gitmastery_exercise_root_path)
        if requires_repo:
            current_repo = GitAutograderRepo(exercise_name, ".")
            output = execute_py_file_function_from_url(
                formatted_exercise_name,
                "verify.py",
                "verify",
                repo=current_repo,  # type: ignore
            )
        else:
            output = execute_py_file_function_from_url(
                formatted_exercise_name, "verify.py", "verify"
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
            started_at=None,
            completed_at=None,
            comments=[str(e)],
            status=GitAutograderStatus.ERROR,
        )

    assert output is not None
    print_output(output)
    submit_progress(output, verbose)
