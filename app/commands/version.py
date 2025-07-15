import click

from app.utils.click_utils import info
from app.utils.version_utils import Version
from app.version import __version__


@click.command()
@click.pass_context
def version(_: click.Context) -> None:
    current_version = Version.parse_version_string(__version__)
    info(f"Git-Mastery CLI is {click.style(current_version, bold=True, italic=True)}")
