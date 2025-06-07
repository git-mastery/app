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

from cli.utils.click_utils import error, info
from cli.utils.gitmastery_utils import (
    execute_py_file_function_from_url,
    find_gitmastery_exercise_root,
    read_gitmastery_exercise_config,
)


@click.command()
@click.pass_context
def verify(_ctx: click.Context) -> None:
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
    info("Verification completed.")
    info("")
    info(f"{click.style('Status:', bold=True)} {output.status}")
    info(click.style("Comments:", bold=True))
    print("\n".join([f"\t- {comment}" for comment in (output.comments or [])]))
