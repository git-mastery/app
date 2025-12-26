import json
from dataclasses import dataclass
from pathlib import Path


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


GIT_MASTERY_EXERCISES_SOURCE = GitMasteryConfig.ExercisesSource(
    username="git-mastery", repository="exercises", branch="main"
)
