import logging
import os
import subprocess
from dataclasses import dataclass
from subprocess import CompletedProcess
from typing import Dict

from typing_extensions import List


@dataclass
class CommandResult:
    result: CompletedProcess[str]

    def is_success(self) -> bool:
        return self.result.returncode == 0

    @property
    def stdout(self) -> str:
        return self.result.stdout.strip()


def run(command: List[str], verbose: bool, env: Dict[str, str] = {}) -> CommandResult:
    logger = logging.getLogger(__name__)
    result = subprocess.run(
        command, capture_output=True, text=True, env=dict(os.environ, **env)
    )
    logger.info("Ran command: %s", command)
    if env:
        logger.info("Env: %s", env)
    if verbose:
        if result.returncode == 0:
            logger.info(result.stdout)
            print("\t" + result.stdout)
        else:
            logger.error(result.stderr)
            print("\t" + result.stderr)
    return CommandResult(result=result)
