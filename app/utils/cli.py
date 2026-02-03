import os
import shutil
import stat
import time
from datetime import datetime
from pathlib import Path
from typing import Union

from app.utils.click import error

MAX_DELETE_RETRIES = 20
MAX_RETRY_INTERVAL = 0.2


def rmtree(folder_name: Union[str, Path]) -> None:
    """
    Remove a directory tree with backup-and-restore safety mechanism.
    
    If deletion fails, the folder is restored to its original state,
    ensuring no data loss occurs.
    
    Raises RuntimeError if the folder still exists after max retries,
    or the original exception if deletion fails.
    """
    if not os.path.exists(folder_name):
        return

    # Convert to absolute path for consistency
    folder_path = os.path.abspath(folder_name)
    folder_basename = os.path.basename(folder_path)
    parent_dir = os.path.dirname(folder_path)
    
    # Create backup name with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_name = f".{folder_basename}_backup_{timestamp}"
    backup_path = os.path.join(parent_dir, backup_name)
    
    # Create backup
    try:
        shutil.copytree(folder_path, backup_path, symlinks=True, ignore_dangling_symlinks=True)
    except Exception as backup_error:
        error(
            f"Failed to create backup of {folder_name}. Deletion aborted."
        )
    
    # Attempt deletion
    def force_remove_readonly(func, path, _):
        os.chmod(path, stat.S_IWRITE)
        func(path)
    
    try:
        shutil.rmtree(folder_path, onerror=force_remove_readonly)
        
        # Wait for folder to be fully deleted (Windows can be slow with permissions)
        max_retries = MAX_DELETE_RETRIES
        for _ in range(max_retries):
            if not os.path.exists(folder_path):
                break
            time.sleep(MAX_RETRY_INTERVAL)
        
        # If folder still exists after retries, raise error
        if os.path.exists(folder_path):
            raise RuntimeError(f"Failed to delete {folder_name} after {max_retries} retries")
        
        # Deletion succeeded, clean up backup
        shutil.rmtree(backup_path, ignore_errors=True)
        
    except Exception as deletion_error:
        try:
            shutil.copytree(backup_path, folder_path, dirs_exist_ok=True)
            shutil.rmtree(backup_path, ignore_errors=True)
        except Exception as restoration_error:
            # Restoration also failed - leave backup in place
            error(
                f"Failed to delete {folder_name}. Please make sure it is not accessed by other process. "
                f"Your data is preserved at: {backup_path}"
            )
        
        # Restoration succeeded, show error message
        error(
            f"Failed to delete {folder_name}. Please make sure it is not accessed by other process."
        )
