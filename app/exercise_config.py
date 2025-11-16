import json
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Literal, Optional


@dataclass
class ExerciseConfig:
    @dataclass
    class ExerciseRepoConfig:
        repo_type: Literal["local", "remote", "ignore"]
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
