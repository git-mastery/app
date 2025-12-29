import logging
import platform
import subprocess

import click

from app.utils.click import info, success, warn

logger = logging.getLogger(__name__)


def is_macos() -> bool:
    return platform.system().lower() == "darwin"


def run_brew_update() -> bool:
    """Updates Git-Mastery via Homebrew for macOS."""
    try:
        command = ["sh", "-c", "brew update && brew upgrade gitmastery"]
        info(f"Running: {click.style(' '.join(command), bold=True)}")
        result = subprocess.run(command)
        return result.returncode == 0
    except Exception as e:
        logger.error(f"Failed to run update command: {e}")
        return False


@click.command()
def update() -> None:
    """Update Git-Mastery to the latest version."""
    if not is_macos():
        info(
            "Auto-update is currently only supported on macOS. "
            "Please follow the update guide: https://git-mastery.github.io/app/update"
        )
        return

    info("Detected macOS. Starting update via Homebrew...")
    if run_brew_update():
        success("Git-Mastery has been updated successfully!")
    else:
        warn("Update command finished with errors. Please check the output above.")
