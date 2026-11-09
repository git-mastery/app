import importlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from subprocess import CompletedProcess
from unittest.mock import Mock

import pytest
from click.testing import CliRunner
from git import Actor, Repo
from git_autograder import (
    GitAutograderInvalidStateException,
    GitAutograderStatus,
    GitAutograderWrongAnswerException,
)
from git_autograder.output import GitAutograderOutput

from app.commands.verify import _execute_verify, verify
from app.utils.click import error, info
from app.utils.gitmastery import EXERCISE_UTILS_FILES

from e2e.constants import EXERCISE_NAME
from e2e.runner import BinaryRunner

cli_module = importlib.import_module("app.cli")
verify_module = importlib.import_module("app.commands.verify")


@pytest.fixture
def runner() -> BinaryRunner:
    return BinaryRunner.from_env()


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
                "downloaded_at": None,
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
    now = datetime.now(timezone.utc)
    return GitAutograderOutput(
        status=GitAutograderStatus.SUCCESSFUL,
        exercise_name=EXERCISE_NAME,
        started_at=now,
        completed_at=now,
        comments=["First comment", "Second comment"],
    )


@pytest.fixture
def cli_runner(
    exercise_dir: Path,
    graded_output: GitAutograderOutput,
    monkeypatch: pytest.MonkeyPatch,
) -> CliRunner:
    monkeypatch.setattr(cli_module.cli, "commands", {})
    monkeypatch.setattr(cli_module.cli, "_aliases", {})
    monkeypatch.setattr(cli_module.cli, "_commands", {})
    cli_module.cli.add_command(verify, aliases=["v"])
    monkeypatch.setattr(
        cli_module,
        "fetch_latest_release_version",
        lambda: (None, "Version check unavailable"),
    )
    monkeypatch.setattr(verify_module, "get_username", lambda: "test-user")

    def grade(
        exercise_path: Path,
        exercise_name: str,
        formatted_exercise_name: str,
        started_at: datetime,
    ) -> GitAutograderOutput:
        info("Fetching exercise information")
        print("Grader diagnostics")
        return graded_output

    monkeypatch.setattr(verify_module, "_execute_verify", grade)
    return CliRunner()


@pytest.mark.parametrize(
    ("status", "text"),
    [
        (GitAutograderStatus.SUCCESSFUL, "Completed"),
        (GitAutograderStatus.UNSUCCESSFUL, "Incomplete"),
        (GitAutograderStatus.ERROR, "Error"),
    ],
)
@pytest.mark.parametrize("json_output", [False, True])
def test_verify_status_and_progress(
    cli_runner: CliRunner,
    graded_output: GitAutograderOutput,
    exercise_dir: Path,
    status: GitAutograderStatus,
    text: str,
    json_output: bool,
) -> None:
    graded_output.status = status
    result = cli_runner.invoke(
        cli_module.cli, ["verify", "--json"] if json_output else ["verify"]
    )
    assert result.exit_code == 0, result.output
    if json_output:
        assert json.loads(result.stdout) == {
            "exercise_name": EXERCISE_NAME,
            "status": text,
            "comments": graded_output.comments,
        }
        assert result.stdout.count("\n") == 1
        assert "Version check unavailable" in result.stderr
        assert "Grader diagnostics" in result.stderr
        assert "Saving progress of attempt" in result.stderr
    else:
        assert f" INFO  Status: {text}" in result.stdout
        assert (
            " INFO  Comments:\n\t- First comment\n\t- Second comment\n" in result.stdout
        )
        assert "Version check unavailable" in result.stdout
        assert "Grader diagnostics" in result.stdout
        assert result.stderr == ""

    entries = json.loads(
        (exercise_dir.parent / ".gitmastery" / "progress" / "progress.json").read_text()
    )
    assert graded_output.started_at is not None
    assert graded_output.completed_at is not None
    assert entries == [
        {
            "exercise_name": EXERCISE_NAME,
            "status": text,
            "comments": graded_output.comments,
            "started_at": graded_output.started_at.timestamp(),
            "completed_at": graded_output.completed_at.timestamp(),
        }
    ]


@pytest.mark.parametrize(
    "comments", [None, [], ['Quotes: "hello"', "Two\nlines", "こんにちは 😀"]]
)
def test_json_feedback_round_trips(
    cli_runner: CliRunner,
    graded_output: GitAutograderOutput,
    comments: list[str] | None,
) -> None:
    graded_output.comments = comments
    graded_output.exercise_name = None
    result = cli_runner.invoke(cli_module.cli, ["verify", "--json"], color=True)
    assert result.exit_code == 0, result.output
    payload = json.loads(result.stdout)
    assert payload["exercise_name"] == EXERCISE_NAME
    assert payload["comments"] == (comments or [])
    assert result.stdout.isascii()
    assert "\x1b" not in result.stdout


def test_verbose_and_alias(
    cli_runner: CliRunner, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(
        verify_module,
        "get_username",
        importlib.import_module("app.utils.github_cli").get_username,
    )
    monkeypatch.setattr(
        "subprocess.run",
        lambda *args, **kwargs: CompletedProcess(args[0], 0, "test-user\n", ""),
    )
    result = cli_runner.invoke(cli_module.cli, ["--verbose", "v", "--json"])
    assert result.exit_code == 0, result.output
    assert json.loads(result.stdout)["status"] == "Completed"
    assert "\ttest-user" in result.stderr


@pytest.mark.parametrize("missing", ["exercise", "root"])
def test_missing_configuration(
    cli_runner: CliRunner, exercise_dir: Path, missing: str
) -> None:
    config = (
        exercise_dir / ".gitmastery-exercise.json"
        if missing == "exercise"
        else exercise_dir.parent / ".gitmastery" / "config.json"
    )
    config.unlink()
    result = cli_runner.invoke(cli_module.cli, ["verify", "--json"])
    assert result.exit_code == 1
    assert result.stdout == ""
    assert " ERROR " in result.stderr


def test_repository_failure_before_grading(
    cli_runner: CliRunner, monkeypatch: pytest.MonkeyPatch
) -> None:
    repo = Mock()
    repo.__enter__ = Mock(side_effect=RuntimeError("Repository unavailable"))
    repo.__exit__ = Mock(return_value=False)
    monkeypatch.setattr(verify_module, "ExercisesRepo", lambda: repo)
    monkeypatch.setattr(verify_module, "_execute_verify", _execute_verify)
    result = cli_runner.invoke(cli_module.cli, ["verify", "--json"])
    assert result.exit_code != 0
    assert result.stdout == ""
    assert isinstance(result.exception, RuntimeError)


@pytest.mark.parametrize(
    ("exception", "status", "comments"),
    [
        (
            GitAutograderWrongAnswerException(["Wrong answer", "Try again"]),
            "Incomplete",
            ["Wrong answer", "Try again"],
        ),
        (
            GitAutograderInvalidStateException("Invalid state"),
            "Error",
            ["Invalid state"],
        ),
        (
            RuntimeError("Unexpected grading failure"),
            "Error",
            ["Unexpected grading failure"],
        ),
    ],
)
def test_grading_exceptions(
    cli_runner: CliRunner,
    monkeypatch: pytest.MonkeyPatch,
    exception: Exception,
    status: str,
    comments: list[str],
) -> None:
    repo = Mock()
    repo.__enter__ = Mock(return_value=repo)
    repo.__exit__ = Mock(return_value=False)
    monkeypatch.setattr(verify_module, "ExercisesRepo", lambda: repo)
    monkeypatch.setattr(verify_module, "_execute_verify", _execute_verify)
    monkeypatch.setattr(
        verify_module.Namespace, "load_file_as_namespace", Mock(side_effect=exception)
    )
    result = cli_runner.invoke(cli_module.cli, ["verify", "--json"])
    assert result.exit_code == 0, result.output
    payload = json.loads(result.stdout)
    assert payload["status"] == status
    assert payload["comments"] == comments


def test_json_survives_submission_failure(
    cli_runner: CliRunner,
    graded_output: GitAutograderOutput,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def fail_submission(output: GitAutograderOutput) -> None:
        assert output is graded_output
        error("Submission failed")

    submit = Mock(side_effect=fail_submission)
    monkeypatch.setattr(verify_module, "_submit_progress", submit)
    result = cli_runner.invoke(cli_module.cli, ["verify", "--json"])
    assert result.exit_code == 1
    assert json.loads(result.stdout)["status"] == "Completed"
    assert "Submission failed" in result.stderr
    submit.assert_called_once_with(graded_output)


def test_remote_progress_is_submitted_once(
    cli_runner: CliRunner, exercise_dir: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    (exercise_dir.parent / ".gitmastery" / "config.json").write_text(
        '{"progress_remote": true}', encoding="utf-8"
    )
    operations = {}
    for name in ("add_all", "commit", "push", "pull_request"):
        operations[name] = Mock()
        monkeypatch.setattr(verify_module, name, operations[name])
    monkeypatch.setattr(verify_module, "get_prs", Mock(return_value=[]))
    result = cli_runner.invoke(cli_module.cli, ["verify", "--json"])
    assert result.exit_code == 0, result.output
    assert json.loads(result.stdout)["status"] == "Completed"
    assert "No pull request created" in result.stderr
    for operation in operations.values():
        operation.assert_called_once()


def test_migration_warning(cli_runner: CliRunner, exercise_dir: Path) -> None:
    metadata = exercise_dir.parent / ".gitmastery"
    (metadata / "config.json").rename(exercise_dir.parent / ".gitmastery.json")
    (metadata / "progress").rename(exercise_dir.parent / "progress")
    result = cli_runner.invoke(cli_module.cli, ["verify", "--json"])
    assert result.exit_code == 0, result.output
    assert json.loads(result.stdout)["status"] == "Completed"
    assert "Migrated your Git-Mastery metadata" in result.stderr


@pytest.mark.parametrize("args", [["--json", "--help"], ["--help", "--json"]])
def test_help_remains_on_stdout(cli_runner: CliRunner, args: list[str]) -> None:
    result = cli_runner.invoke(cli_module.cli, ["verify", *args])
    assert result.exit_code == 0
    assert "--json" in result.stdout
    assert "Usage:" in result.stdout
    assert result.stderr == ""


def test_usage_error_does_not_grade(
    cli_runner: CliRunner, monkeypatch: pytest.MonkeyPatch
) -> None:
    grade = Mock()
    monkeypatch.setattr(verify_module, "_execute_verify", grade)
    result = cli_runner.invoke(cli_module.cli, ["verify", "--json", "--unknown"])
    assert result.exit_code == 2
    assert "No such option" in result.stderr
    grade.assert_not_called()


def test_direct_invocation_and_output_restoration(
    cli_runner: CliRunner, exercise_dir: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    stdout = sys.stdout
    result = cli_runner.invoke(verify, ["--json"], obj={})
    assert result.exit_code == 0, result.output
    assert json.loads(result.stdout)["status"] == "Completed"
    assert "Grader diagnostics" in result.stderr
    assert sys.stdout is stdout

    monkeypatch.chdir(exercise_dir)
    result = cli_runner.invoke(cli_module.cli, ["verify"])
    assert result.exit_code == 0, result.output
    assert " INFO  Status: Completed" in result.stdout
    assert result.stderr == ""


def test_output_restoration_after_failure(
    cli_runner: CliRunner, exercise_dir: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    (exercise_dir / ".gitmastery-exercise.json").unlink()
    result = cli_runner.invoke(cli_module.cli, ["verify", "--json"])
    assert result.exit_code == 1
    result = cli_runner.invoke(cli_module.cli, ["verify"])
    assert result.exit_code == 1
    assert " ERROR " in result.stdout
    assert result.stderr == ""


def test_verify_json_binary(
    runner: BinaryRunner, exercise_dir: Path, tmp_path: Path
) -> None:
    """Exercise real grading and persistence without a remote exercise source."""
    source = tmp_path / "source"
    source.mkdir()
    verifier = source / "under_control"
    verifier.mkdir()
    (verifier / "verify.py").write_text(
        "from git_autograder import GitAutograderStatus\n"
        "def verify(exercise):\n"
        "    print('Binary grader diagnostics')\n"
        "    return exercise.to_output(['First comment', 'Second comment'], "
        "GitAutograderStatus.SUCCESSFUL)\n",
        encoding="utf-8",
    )
    utilities = source / "exercise_utils"
    utilities.mkdir()
    for name in EXERCISE_UTILS_FILES:
        (utilities / f"{name}.py").write_text("", encoding="utf-8")
    repo = Repo.init(source)
    repo.index.add(["under_control/verify.py", "exercise_utils"])
    actor = Actor("Test verifier", "test@example.com")
    repo.index.commit("Test verifier", author=actor, committer=actor)
    (tmp_path / ".gitmastery" / "config.json").write_text(
        json.dumps({"exercises_source": {"type": "local", "repo_path": str(source)}}),
        encoding="utf-8",
    )
    gh_config = tmp_path / "gh-config"
    gh_config.mkdir()
    result = runner.run(
        ["verify", "--json"],
        cwd=exercise_dir,
        env={"GH_TOKEN": "", "GITHUB_TOKEN": "", "GH_CONFIG_DIR": str(gh_config)},
    )
    result.assert_success()
    assert json.loads(result.stdout) == {
        "exercise_name": EXERCISE_NAME,
        "status": "Completed",
        "comments": ["First comment", "Second comment"],
    }
    assert "Using local exercises source" in result.stderr
    assert "Binary grader diagnostics" in result.stderr
    progress = json.loads(
        (tmp_path / ".gitmastery" / "progress" / "progress.json").read_text()
    )
    assert len(progress) == 1
    assert progress[0]["status"] == "Completed"
