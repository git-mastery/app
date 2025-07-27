import os
import shutil
import stat
import subprocess
from pathlib import Path
from typing import Optional, Tuple, Union


def get_stdout_stderr(verbose: bool) -> Tuple[Optional[int], Optional[int]]:
    stdout = None if verbose else subprocess.DEVNULL
    stderr = None if verbose else subprocess.DEVNULL
    return stdout, stderr


def rmtree(folder_name: Union[str, Path]) -> None:
    def force_remove_readonly(func, path, _):
        os.chmod(path, stat.S_IWRITE)
        func(path)

    shutil.rmtree(folder_name, onerror=force_remove_readonly)
