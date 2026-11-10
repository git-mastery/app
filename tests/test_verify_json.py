import importlib
import json
from datetime import datetime
from pathlib import Path

import click
import pytest
from click.testing import CliRunner
from git_autograder import GitAutograderStatus
from git_autograder.output import GitAutograderOutput

from app.cli import LoggingGroup, cli
from app.commands.verify import verify

verify_module = importlib.import_module("app.commands.verify")
EXERCISE_NAME = "example"


@pytest.fixture
def exercise_dir(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    metadata = tmp_path / ".gitmastery"
    (metadata / "progress").mkdir(parents=True)
    (metadata / "config.json").write_text("{}", encoding="utf-8")
    exercise = tmp_path / EXERCISE_NAME
    exercise.mkdir()
    (exercise / ".gitmastery-exercise.json").write_text(
        json.dumps(
            {
                "exercise_name": EXERCISE_NAME,
                "tags": [],
                "requires_git": False,
                "requires_github": False,
                "base_files": {},
                "exercise_repo": {
                    "repo_type": "ignore",
                    "repo_name": "unused",
                    "repo_title": None,
                    "create_fork": False,
                    "init": False,
                },
            }
        ),
        encoding="utf-8",
    )
    monkeypatch.chdir(exercise)
    return exercise


@pytest.fixture
def graded_output() -> GitAutograderOutput:
    return GitAutograderOutput(
        status=GitAutograderStatus.SUCCESSFUL,
        exercise_name=EXERCISE_NAME,
        started_at=None,
        completed_at=None,
        comments=['First "comment"\nwith a newline', "こんにちは 😀"],
    )


@pytest.fixture
def application(
    exercise_dir: Path,
    graded_output: GitAutograderOutput,
    monkeypatch: pytest.MonkeyPatch,
) -> click.Group:
    group = LoggingGroup("gitmastery", callback=cli.callback, params=cli.params)
    group.add_command(verify, aliases=["v"])
    monkeypatch.setattr(
        "app.cli.fetch_latest_release_version",
        lambda: (None, "Version check unavailable"),
    )
    monkeypatch.setattr(verify_module, "get_username", lambda: "test-user")

    def grade(
        exercise_path: Path,
        exercise_name: str,
        formatted_exercise_name: str,
        started_at: datetime,
    ) -> GitAutograderOutput:
        print("Grader diagnostics")
        return graded_output

    monkeypatch.setattr(verify_module, "_execute_verify", grade)
    return group


def test_json_grading_result(
    application: click.Group,
    graded_output: GitAutograderOutput,
) -> None:
    """JSON contains the grade and all comments, with diagnostics on stderr."""
    result = CliRunner().invoke(application, ["verify", "--json"], color=True)
    assert result.exit_code == 0, result.output
    assert json.loads(result.stdout) == {
        "exercise_name": EXERCISE_NAME,
        "status": "Completed",
        "comments": graded_output.comments,
    }
    assert "Version check unavailable" in result.stderr
    assert "Grader diagnostics" in result.stderr
    assert "Saving progress of attempt" in result.stderr


def test_json_without_comments(
    application: click.Group, graded_output: GitAutograderOutput
) -> None:
    """Absent feedback is an empty list, without the text renderer's placeholder."""
    graded_output.comments = None
    result = CliRunner().invoke(application, ["verify", "--json"])
    assert result.exit_code == 0, result.output
    assert json.loads(result.stdout)["comments"] == []
