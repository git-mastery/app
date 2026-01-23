import json
from dataclasses import dataclass
from pathlib import Path
from typing import Self, Type, Optional, Union

from app.configs.utils import read_config

GITMASTERY_CONFIG_NAME = ".gitmastery.json"


@dataclass
class GitMasteryConfig:
    @dataclass
    class ExercisesSource:
        # "remote" or "local"
        type: str = "remote"
        # remote fields (legacy uses username/repository/branch)
        username: Optional[str] = None
        repository: Optional[str] = None
        branch: Optional[str] = "main"
        # local field
        path: Optional[str] = None

        def to_url(self) -> str:
            if self.type != "remote":
                raise ValueError("to_url only valid for remote ExercisesSource")
            return f"https://github.com/{self.username}/{self.repository}.git"

        @classmethod
        def from_raw(cls, raw: Union["GitMasteryConfig.ExercisesSource", dict, None]) -> "GitMasteryConfig.ExercisesSource":
            # Pass-through if already the correct instance
            if isinstance(raw, cls):
                return raw
            # Default remote
            if raw is None:
                return cls(type="remote", username="git-mastery", repository="exercises", branch="main")
            if isinstance(raw, dict):
                typ = raw.get("type")
                # explicit local
                if typ == "local":
                    return cls(type="local", path=raw.get("path"))
                # fallthrough for None (legacy)/detected remote
                return cls(
                    type="remote",
                    username=raw.get("username", "git-mastery"),
                    repository=raw.get("repository", "exercises"),
                    branch=raw.get("branch", "main"),
                )
            raise ValueError("Unsupported exercises_source shape")


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
        exercises_source = GitMasteryConfig.ExercisesSource.from_raw(exercises_source_raw)

        return cls(
            path=path,
            cds=cds,
            progress_local=raw_config.get("progress_local", True),
            progress_remote=raw_config.get("progress_remote", False),
            exercises_source=exercises_source,
        )


GIT_MASTERY_EXERCISES_SOURCE = GitMasteryConfig.ExercisesSource.from_raw(
    {"type": "remote", "username": "git-mastery", "repository": "exercises", "branch": "main"}
)
