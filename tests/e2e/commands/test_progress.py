import json
from pathlib import Path

from ..result import RunResult


def test_progress_show(progress_results: RunResult) -> None:
    """progress show displays the progress header."""
    progress_results.assert_stdout_contains("Your Git-Mastery progress:")


def test_progress_sync_on_then_off(progress_results: RunResult, gitmastery_root: Path) -> None:
    """progress sync on/off toggles progress_remote in the config."""
    progress_results.assert_stdout_contains("You have setup the progress tracker for Git-Mastery!")
    progress_results.assert_stdout_contains("Successfully removed your remote sync")
    assert json.loads((gitmastery_root / ".gitmastery.json").read_text())["progress_remote"] is False


def test_progress_reset(reset_results: RunResult, verified_exercise_dir: Path) -> None:
    """progress reset removes the current exercise's entry from progress.json."""
    progress_json = verified_exercise_dir.parent / "progress" / "progress.json"
    # TODO: need to verify that the exercise itself progress was reset, not just progress.json was cleared
    assert json.loads(progress_json.read_text()) == []
