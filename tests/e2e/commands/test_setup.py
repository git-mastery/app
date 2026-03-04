from pathlib import Path


def test_setup(exercises_dir: Path) -> None:
    """
    Test that setup creates the progress directory, progress.json, .gitmastery.json and .gitmastery.log
    Setup command already called in conftest.py for test setup
    """
    progress_dir = exercises_dir / "progress"
    assert progress_dir.is_dir(), f"Expected {progress_dir} to exist"

    progress_file = progress_dir / "progress.json"
    assert progress_file.is_file(), f"Expected {progress_file} to exist"

    config_file = exercises_dir / ".gitmastery.json"
    assert config_file.is_file(), f"Expected {config_file} to exist"

    log_file = exercises_dir / ".gitmastery.log"
    assert log_file.is_file(), f"Expected {log_file} to exist"
