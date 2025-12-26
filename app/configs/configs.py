import json
from pathlib import Path
from typing import Dict, Optional, Tuple


def find_root(filename: str) -> Optional[Tuple[Path, int]]:
    current = Path.cwd()
    steps = 0
    for parent in [current] + list(current.parents):
        if (parent / filename).is_file():
            return parent, steps
        steps += 1

    return None


def read_config(path: Path, filename: str) -> Dict:
    with open(path / filename, "r") as f:
        contents = f.read()
        if contents.strip() == "":
            return {}
        return json.loads(contents)
