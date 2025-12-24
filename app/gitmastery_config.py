import json
from dataclasses import dataclass
from pathlib import Path

from app.utils.version import Version


@dataclass
class GitMasteryConfig:
    progress_local: bool
    progress_remote: bool
    exercises_version: Version

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
