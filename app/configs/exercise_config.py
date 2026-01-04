import json
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Literal, Optional, Self, Type

from app.configs.utils import read_config

GITMASTERY_EXERCISE_CONFIG_NAME = ".gitmastery-exercise.json"


@dataclass
class ExerciseConfig:
    @dataclass
    class ExerciseRepoConfig:
        repo_type: Literal["local", "remote", "ignore", "local-ignore"]
        repo_name: str
        repo_title: Optional[str]
        create_fork: Optional[bool]
        init: Optional[bool]

    exercise_name: str
    tags: List[str]
    requires_git: bool
    requires_github: bool
    base_files: Dict[str, str]
    exercise_repo: ExerciseRepoConfig

    downloaded_at: Optional[float]

    path: Path
    cds: int

    @property
    def formatted_exercise_name(self) -> str:
        # Used primarily to match the name of the folders of the exercises repository
        return self.exercise_name.replace("-", "_")

    def exercise_fork_name(self, username: str) -> str:
        # Used to minimize conflicts with existing repositories on the user's account
        return f"{username}-gitmastery-{self.exercise_repo.repo_title}"

    def to_json(self) -> str:
        return json.dumps(
            self,
            default=lambda o: {
                k: v for k, v in o.__dict__.items() if k not in ("path", "cds")
            },
            indent=2,
        )

    def write(self) -> None:
        with open(
            self.path / GITMASTERY_EXERCISE_CONFIG_NAME, "w"
        ) as exercise_config_file:
            exercise_config_file.write(self.to_json())

    @classmethod
    def read(cls: Type[Self], path: Path, cds: int) -> Self:
        raw_config = read_config(path, GITMASTERY_EXERCISE_CONFIG_NAME)
        exercise_repo = raw_config["exercise_repo"]

        return cls(
            path=path,
            cds=cds,
            exercise_name=raw_config["exercise_name"],
            tags=raw_config["tags"],
            requires_git=raw_config["requires_git"],
            requires_github=raw_config["requires_github"],
            base_files=raw_config["base_files"],
            exercise_repo=ExerciseConfig.ExerciseRepoConfig(
                repo_type=exercise_repo["repo_type"],  # type: ignore
                repo_name=exercise_repo["repo_name"],
                repo_title=exercise_repo["repo_title"],
                create_fork=exercise_repo["create_fork"],
                init=exercise_repo["init"],
            ),
            downloaded_at=None,
        )
