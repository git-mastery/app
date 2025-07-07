import click

from app.commands.progress.sync.off import off
from app.commands.progress.sync.on import on


@click.group()
def sync() -> None:
    pass


sync.add_command(on)
sync.add_command(off)
