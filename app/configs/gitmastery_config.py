import json
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Self, Type

from app.configs.utils import find_root, read_config

GITMASTERY_FOLDER_NAME = ".gitmastery"
GITMASTERY_CONFIG_NAME = "config.json"


@dataclass
class GitMasteryConfig:
    @dataclass
    class ExercisesSource:
        username: str
        repository: str
        branch: str

        def to_url(self) -> str:
            return f"https://github.com/{self.username}/{self.repository}.git"

    progress_local: bool
    progress_remote: bool
    exercises_source: ExercisesSource

    path: Path
    cds: int

    def to_json(self) -> str:
        return json.dumps(
            self,
            default=lambda o: {
                k: v for k, v in o.__dict__.items() if k not in ("path", "cds")
            },
            indent=2,
        )

    def write(self) -> None:
        with open(self.path / GITMASTERY_FOLDER_NAME / GITMASTERY_CONFIG_NAME, "w") as exercise_config_file:
            exercise_config_file.write(self.to_json())

    @classmethod
    def read(cls: Type[Self], path: Path, cds: int) -> Self:
        raw_config = read_config(path / GITMASTERY_FOLDER_NAME, GITMASTERY_CONFIG_NAME)

        exercises_source_raw = raw_config.get("exercises_source", {})
        return cls(
            path=path,
            cds=cds,
            progress_local=raw_config.get("progress_local", True),
            progress_remote=raw_config.get("progress_remote", False),
            exercises_source=GitMasteryConfig.ExercisesSource(
                username=exercises_source_raw.get("username", "git-mastery"),
                repository=exercises_source_raw.get("repository", "exercises"),
                branch=exercises_source_raw.get("branch", "main"),
            ),
        )


GIT_MASTERY_EXERCISES_SOURCE = GitMasteryConfig.ExercisesSource(
    username="git-mastery", repository="exercises", branch="main"
)


def migrate_to_gitmastery_folder() -> Optional[Path]:
    """
    If old-style layout is detected (.gitmastery.json at root, no .gitmastery/ folder),
    migrate files into the new .gitmastery/ folder convention.
    Returns the root path if migration occurred, otherwise None.
    """
    old_root = find_root(".gitmastery.json")
    if old_root is None:
        return None

    root, _ = old_root
    new_dir = root / GITMASTERY_FOLDER_NAME
    if new_dir.exists():
        return None

    new_dir.mkdir()
    (root / ".gitmastery.json").rename(new_dir / GITMASTERY_CONFIG_NAME)
    old_log = root / ".gitmastery.log"
    if old_log.exists():
        old_log.rename(new_dir / "gitmastery.log")
    return root
