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
from app.utils.click import error

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


@pytest.mark.parametrize(
    ("status", "text", "args"),
    [
        (GitAutograderStatus.SUCCESSFUL, "Completed", ["verify", "--json"]),
        (GitAutograderStatus.UNSUCCESSFUL, "Incomplete", ["v", "--json"]),
        (GitAutograderStatus.ERROR, "Error", ["--verbose", "verify", "--json"]),
    ],
)
def test_json_grading_result(
    application: click.Group,
    graded_output: GitAutograderOutput,
    status: GitAutograderStatus,
    text: str,
    args: list[str],
) -> None:
    """Return every comment and a stable status without diagnostic text in JSON."""
    graded_output.status = status
    result = CliRunner().invoke(application, args, color=True)
    assert result.exit_code == 0, result.output
    assert json.loads(result.stdout) == {
        "exercise_name": EXERCISE_NAME,
        "status": text,
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


def test_json_before_grading_failure(
    application: click.Group, exercise_dir: Path
) -> None:
    """A guard failure must leave stdout empty rather than emit a grading result."""
    (exercise_dir / ".gitmastery-exercise.json").unlink()
    result = CliRunner().invoke(application, ["verify", "--json"])
    assert result.exit_code == 1
    assert result.stdout == ""
    assert "not inside a Git-Mastery exercise folder" in result.stderr


def test_json_after_submission_failure(
    application: click.Group, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Retain the grading result when saving progress fails afterward."""

    def fail_submission(output: GitAutograderOutput) -> None:
        error("Saving progress failed")

    monkeypatch.setattr(verify_module, "_submit_progress", fail_submission)
    result = CliRunner().invoke(application, ["verify", "--json"])
    assert result.exit_code == 1
    assert json.loads(result.stdout)["status"] == "Completed"
    assert "Saving progress failed" in result.stderr


def test_json_help(application: click.Group) -> None:
    """The early JSON-mode check must leave Click help on stdout."""
    result = CliRunner().invoke(application, ["verify", "--json", "--help"])
    assert result.exit_code == 0
    assert "Usage:" in result.stdout
    assert "--json" in result.stdout
    assert result.stderr == ""


def test_direct_json_and_subsequent_invocations(
    application: click.Group,
    exercise_dir: Path,
    graded_output: GitAutograderOutput,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Support REPL-style direct invocation and restore routing for later commands."""
    runner = CliRunner()
    direct = runner.invoke(verify, ["--json"], obj={})
    assert direct.exit_code == 0, direct.output
    assert json.loads(direct.stdout)["status"] == "Completed"
    assert "Grader diagnostics" in direct.stderr

    monkeypatch.chdir(exercise_dir)
    grouped = runner.invoke(application, ["verify", "--json"])
    assert grouped.exit_code == 0, grouped.output
    assert json.loads(grouped.stdout) == json.loads(direct.stdout)

    monkeypatch.chdir(exercise_dir)
    plain = runner.invoke(application, ["verify"])
    assert plain.exit_code == 0, plain.output
    assert " INFO  Status: Completed" in plain.stdout
    assert " INFO  Comments:" in plain.stdout
    for comment in graded_output.comments or []:
        assert comment in plain.stdout
    assert "Version check unavailable" in plain.stdout
    assert plain.stderr == ""
