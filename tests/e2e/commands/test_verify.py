import json
from pathlib import Path

from ..constants import EXERCISE_NAME
from ..runner import BinaryRunner


def test_verify_exercise(runner: BinaryRunner, downloaded_exercise_dir: Path) -> None:
    """verify runs successfully and writes a progress entry with the expected fields."""
    res = runner.run(["verify"], cwd=downloaded_exercise_dir)
    res.assert_success()
    res.assert_stdout_contains("Starting verification of")
    res.assert_stdout_contains("Verification completed.")

    progress_json = downloaded_exercise_dir.parent / "progress" / "progress.json"
    entries = json.loads(progress_json.read_text())
    assert len(entries) == 1
    entry = entries[0]
    assert entry["exercise_name"] == EXERCISE_NAME
    assert "started_at" in entry
    assert "completed_at" in entry
    assert "status" in entry
