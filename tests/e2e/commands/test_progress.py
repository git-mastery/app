import json
from pathlib import Path
import pytest

from ..runner import BinaryRunner


def test_progress_show(runner: BinaryRunner, gitmastery_root: Path) -> None:
    """progress show displays the progress header."""
    res = runner.run(["progress", "show"], cwd=gitmastery_root)
    res.assert_success()
    res.assert_stdout_contains("Your Git-Mastery progress:")


def test_progress_sync_on_then_off(runner: BinaryRunner, gitmastery_root: Path) -> None:
    """progress sync on/off toggles progress_remote in the config."""
    res_on = runner.run(["progress", "sync", "on"], cwd=gitmastery_root)
    res_on.assert_success()
    res_on.assert_stdout_contains("You have setup the progress tracker for Git-Mastery!")
    assert json.loads((gitmastery_root / ".gitmastery.json").read_text())["progress_remote"] is True

    # send 'y' to confirm
    res_off = runner.run(
        ["progress", "sync", "off"], cwd=gitmastery_root, stdin_text="y\n"
    )
    res_off.assert_success()
    res_off.assert_stdout_contains("Successfully removed your remote sync")
    assert json.loads((gitmastery_root / ".gitmastery.json").read_text())["progress_remote"] is False


@pytest.mark.order(after="tests/e2e/commands/test_verify.py::test_verify_exercise")
def test_progress_reset(runner: BinaryRunner, verified_exercise_dir: Path) -> None:
    """progress reset removes the current exercise's entry from progress.json."""
    res = runner.run(["progress", "reset"], cwd=verified_exercise_dir)
    res.assert_success()
    progress_json = verified_exercise_dir.parent / "progress" / "progress.json"
    # TODO: need to verify that the exercise itself progress was reset, not just progress.json was cleared
    assert json.loads(progress_json.read_text()) == []
