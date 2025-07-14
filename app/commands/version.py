import click

from app.utils.click_utils import info
from app.version import __version__


@click.command()
@click.pass_context
def version(_: click.Context) -> None:
    info(f"Git-Mastery CLI is currently {__version__}")
