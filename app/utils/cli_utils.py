import subprocess
from typing import Optional, Tuple


def get_stdout_stderr(verbose: bool) -> Tuple[Optional[int], Optional[int]]:
    stdout = None if verbose else subprocess.DEVNULL
    stderr = None if verbose else subprocess.DEVNULL
    return stdout, stderr
