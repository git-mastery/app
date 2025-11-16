import click

from app.utils.click import info
from app.utils.version import Version
from app.version import __version__


@click.command()
def version() -> None:
    current_version = Version.parse_version_string(__version__)
    info(f"Git-Mastery app is {click.style(current_version, bold=True, italic=True)}")
