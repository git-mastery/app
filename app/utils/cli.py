import os
import shutil
import stat
from pathlib import Path
from typing import Union


def rmtree(folder_name: Union[str, Path]) -> None:
    def force_remove_readonly(func, path, _):
        os.chmod(path, stat.S_IWRITE)
        func(path)

    shutil.rmtree(folder_name, onerror=force_remove_readonly)
