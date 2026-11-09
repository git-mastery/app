import json
import shutil
from pathlib import Path

from ..constants import EXERCISE_NAME
from ..runner import BinaryRunner


def test_verify_exercise(verified_exercise_dir: Path) -> None:
    """verify writes a progress entry with the expected fields."""
    progress_json = (
        verified_exercise_dir.parent / ".gitmastery" / "progress" / "progress.json"
    )
    entries = json.loads(progress_json.read_text())
    assert len(entries) == 1
    entry = entries[0]
    assert entry["exercise_name"] == EXERCISE_NAME
    assert "started_at" in entry
    assert "completed_at" in entry
    assert "status" in entry


def test_verify_json(
    runner: BinaryRunner, downloaded_exercise_dir: Path, tmp_path: Path
) -> None:
    """JSON verification returns the grade while still saving progress."""
    exercise_dir = tmp_path / EXERCISE_NAME
    shutil.copytree(downloaded_exercise_dir, exercise_dir)
    metadata = tmp_path / ".gitmastery"
    (metadata / "progress").mkdir(parents=True)
    config = json.loads(
        (downloaded_exercise_dir.parent / ".gitmastery" / "config.json").read_text()
    )
    config["progress_remote"] = False
    (metadata / "config.json").write_text(json.dumps(config), encoding="utf-8")

    result = runner.run(["verify", "--json"], cwd=exercise_dir)
    result.assert_success()
    grade = json.loads(result.stdout)
    entries = json.loads((metadata / "progress" / "progress.json").read_text())
    assert len(entries) == 1
    assert grade == {
        "exercise_name": EXERCISE_NAME,
        "status": entries[0]["status"],
        "comments": entries[0]["comments"] or [],
    }
    assert grade["status"] in ("Completed", "Incomplete", "Error")
