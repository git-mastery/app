from pathlib import Path

from ..constants import EXERCISE_NAME, HANDS_ON_NAME
from ..runner import BinaryRunner


def test_download_exercise(runner: BinaryRunner, exercises_dir: Path) -> None:
    """Test the download command output successfully performs the download for exercise."""
    res = runner.run(["download", EXERCISE_NAME], cwd=exercises_dir)
    res.assert_success()

    exercise_folder = exercises_dir / EXERCISE_NAME
    assert exercise_folder.is_dir()

    exercise_config = exercise_folder / ".gitmastery-exercise.json"
    assert exercise_config.is_file()

    exercise_readme = exercise_folder / "README.md"
    assert exercise_readme.is_file()


def test_download_hands_on(runner: BinaryRunner, exercises_dir: Path) -> None:
    """Test the download command output successfully performs the download for hands-on."""
    res = runner.run(["download", HANDS_ON_NAME], cwd=exercises_dir)
    res.assert_success()

    hands_on_folder = exercises_dir / HANDS_ON_NAME
    assert hands_on_folder.is_dir()
