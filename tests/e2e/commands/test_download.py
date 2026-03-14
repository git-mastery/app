import json
from pathlib import Path

from ..constants import EXERCISE_NAME


def test_download_exercise(downloaded_exercise_dir: Path) -> None:
    """download creates the exercise folder with its config and README."""
    assert downloaded_exercise_dir.is_dir()

    exercise_config = downloaded_exercise_dir / ".gitmastery-exercise.json"
    assert exercise_config.is_file()
    assert json.loads(exercise_config.read_text())["exercise_name"] == EXERCISE_NAME

    assert (downloaded_exercise_dir / "README.md").is_file()


def test_download_hands_on(downloaded_hands_on_dir: Path) -> None:
    """download creates the hands-on folder."""
    assert downloaded_hands_on_dir.is_dir()
