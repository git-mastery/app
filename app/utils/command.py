import os
import subprocess
from dataclasses import dataclass
from subprocess import CompletedProcess
from typing import Dict, TypeVar

from typing_extensions import List

T = TypeVar("T")


@dataclass
class CommandResult:
    result: CompletedProcess[str]

    def is_success(self) -> bool:
        return self.result.returncode == 0

    @property
    def stdout(self) -> str:
        return self.result.stdout.strip()


def run(command: List[str], verbose: bool, env: Dict[str, str] = {}) -> CommandResult:
    result = subprocess.run(
        command, capture_output=True, text=True, env=dict(os.environ, **env)
    )
    if verbose:
        if result.returncode == 0:
            print(result.stdout)
        else:
            print(result.stderr)
    return CommandResult(result=result)
