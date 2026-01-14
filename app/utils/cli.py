import os
import shutil
import stat
import time
from pathlib import Path
from typing import Union


def rmtree(folder_name: Union[str, Path]) -> None:
    """
    Remove a directory tree.

    Raises RuntimeError if the folder still exists after max retries.
    """
    if not os.path.exists(folder_name):
        return

    def force_remove_readonly(func, path, _):
        os.chmod(path, stat.S_IWRITE)
        func(path)

    shutil.rmtree(folder_name, onerror=force_remove_readonly)

    # Wait for folder to be fully deleted (Windows can be slow with permissions)
    max_retries = 20
    for _ in range(max_retries):
        if not os.path.exists(folder_name):
            return
        time.sleep(0.2)

    # If folder still exists after retries, raise error
    raise RuntimeError(f"Failed to delete {folder_name} after {max_retries} retries")
