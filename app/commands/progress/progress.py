import click

from app.commands.progress.reset import reset
from app.commands.progress.show import show
from app.commands.progress.sync.sync import sync


@click.group()
def progress() -> None:
    """Tracks the progress made by students on Git-Mastery exercises."""
    pass


progress.add_command(sync)
progress.add_command(reset)
progress.add_command(show)
