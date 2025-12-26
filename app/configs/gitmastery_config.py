import json
from dataclasses import dataclass
from pathlib import Path
from typing import Self, Type

from app.configs.configs import read_config

GITMASTERY_CONFIG_NAME = ".gitmastery.json"


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
        with open(self.path / GITMASTERY_CONFIG_NAME, "w") as exercise_config_file:
            exercise_config_file.write(self.to_json())

    @classmethod
    def read(cls: Type[Self], path: Path, cds: int) -> Self:
        raw_config = read_config(path, GITMASTERY_CONFIG_NAME)

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
