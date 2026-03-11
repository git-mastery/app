from pathlib import Path

from ..constants import EXERCISE_NAME
from ..runner import BinaryRunner


def test_verify_exercise(runner: BinaryRunner, exercises_dir: Path) -> None:
    """Test that verify runs on a downloaded exercise."""
    exercise_dir = exercises_dir / EXERCISE_NAME
    res = runner.run(["verify"], cwd=exercise_dir)
    res.assert_success()
    # TODO: check that the correct tests have been run
    res.assert_stdout_contains("Starting verification of")
    res.assert_stdout_contains("Verification completed.")
