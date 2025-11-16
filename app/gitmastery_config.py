import json
from dataclasses import dataclass
from pathlib import Path


@dataclass
class GitMasteryConfig:
    progress_local: bool
    progress_remote: bool

    path: Path
    cds: int

    def to_json(self) -> str:
        omit_fields = ["path", "cds"]
        dict_self = self.__dict__
        for field in omit_fields:
            dict_self.pop(field)
        return json.dumps(dict_self, sort_keys=False, indent=2)
