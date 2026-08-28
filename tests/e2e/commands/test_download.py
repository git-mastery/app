import json
from pathlib import Path

from ..constants import EXERCISE_NAME, HANDS_ON_NAME
from ..runner import BinaryRunner


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


def test_download_blocks_when_already_downloaded(
    runner: BinaryRunner, gitmastery_root: Path, downloaded_exercise_dir: Path
) -> None:
    """download refuses to overwrite an existing exercise folder."""
    sentinel = downloaded_exercise_dir / "NOTES.md"
    sentinel.write_text("local work")

    try:
        res = runner.run(["download", EXERCISE_NAME], cwd=gitmastery_root)

        assert res.returncode != 0, (
            f"Expected a non-zero exit code, got {res.returncode}\n"
            f"stdout:\n{res.stdout}"
        )
        res.assert_stdout_contains("already have")
        res.assert_stdout_contains("--force")

        assert sentinel.is_file()
        assert sentinel.read_text() == "local work"
    finally:
        sentinel.unlink()


def test_download_hands_on_blocks_when_already_downloaded(
    runner: BinaryRunner, gitmastery_root: Path, downloaded_hands_on_dir: Path
) -> None:
    """download refuses to overwrite an existing hands-on folder."""
    sentinel = downloaded_hands_on_dir / "NOTES.md"
    sentinel.write_text("local work")

    try:
        res = runner.run(["download", HANDS_ON_NAME], cwd=gitmastery_root)

        assert res.returncode != 0, (
            f"Expected a non-zero exit code, got {res.returncode}\n"
            f"stdout:\n{res.stdout}"
        )
        res.assert_stdout_contains("--force")

        assert sentinel.is_file()
    finally:
        sentinel.unlink()


def test_download_force_overwrites(
    runner: BinaryRunner, isolated_gitmastery_root: Path
) -> None:
    """download --force wipes the existing exercise folder and downloads it again."""
    runner.run(
        ["download", EXERCISE_NAME], cwd=isolated_gitmastery_root
    ).assert_success()

    exercise_dir = isolated_gitmastery_root / EXERCISE_NAME
    sentinel = exercise_dir / "NOTES.md"
    sentinel.write_text("local work")

    runner.run(
        ["download", EXERCISE_NAME, "--force"], cwd=isolated_gitmastery_root
    ).assert_success()

    assert not sentinel.exists()
    assert (exercise_dir / ".gitmastery-exercise.json").is_file()
    assert (exercise_dir / "README.md").is_file()
