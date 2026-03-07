import json
from pathlib import Path

from ..constants import EXERCISE_NAME, HANDS_ON_NAME
from ..runner import BinaryRunner


def test_download_exercise(runner: BinaryRunner, gitmastery_root: Path) -> None:
    """download creates the exercise folder with its config and README."""
    res = runner.run(["download", EXERCISE_NAME], cwd=gitmastery_root)
    res.assert_success()

    exercise_folder = gitmastery_root / EXERCISE_NAME
    assert exercise_folder.is_dir()

    exercise_config = exercise_folder / ".gitmastery-exercise.json"
    assert exercise_config.is_file()
    assert json.loads(exercise_config.read_text())["exercise_name"] == EXERCISE_NAME

    assert (exercise_folder / "README.md").is_file()


def test_download_hands_on(runner: BinaryRunner, gitmastery_root: Path) -> None:
    """download creates the hands-on folder."""
    res = runner.run(["download", HANDS_ON_NAME], cwd=gitmastery_root)
    res.assert_success()

    assert (gitmastery_root / HANDS_ON_NAME).is_dir()
