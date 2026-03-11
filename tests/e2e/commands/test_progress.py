from pathlib import Path

from ..constants import EXERCISE_NAME
from ..runner import BinaryRunner


def test_progress_show(runner: BinaryRunner, exercises_dir: Path) -> None:
    """Test that progress show displays progress."""
    res = runner.run(["progress", "show"], cwd=exercises_dir)
    res.assert_success()
    res.assert_stdout_contains("Your Git-Mastery progress:")


def test_progress_sync_on_then_off(runner: BinaryRunner, exercises_dir: Path) -> None:
    """Test that progress sync on followed by sync off works correctly."""
    # Enable sync
    res_on = runner.run(["progress", "sync", "on"], cwd=exercises_dir)
    res_on.assert_success()
    res_on.assert_stdout_contains(
        "You have setup the progress tracker for Git-Mastery!"
    )

    # Disable sync (send 'y' to confirm)
    res_off = runner.run(
        ["progress", "sync", "off"], cwd=exercises_dir, stdin_text="y\n"
    )
    res_off.assert_success()
    res_off.assert_stdout_contains("Successfully removed your remote sync")


def test_progress_reset(runner: BinaryRunner, exercises_dir: Path) -> None:
    """Test that progress reset works correctly after verify has run."""
    exercise_dir = exercises_dir / EXERCISE_NAME
    res = runner.run(["progress", "reset"], cwd=exercise_dir)
    # TODO: verify that the progress has actually been reset
    res.assert_success()
