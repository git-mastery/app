import json
from pathlib import Path

from ..constants import EXERCISE_NAME


def test_verify_exercise(verified_exercise_dir: Path) -> None:
    """verify writes a progress entry with the expected fields."""
    progress_json = verified_exercise_dir.parent / "progress" / "progress.json"
    entries = json.loads(progress_json.read_text())
    assert len(entries) == 1
    entry = entries[0]
    assert entry["exercise_name"] == EXERCISE_NAME
    assert "started_at" in entry
    assert "completed_at" in entry
    assert "status" in entry
