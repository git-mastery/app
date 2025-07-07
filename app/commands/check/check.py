import click

from app.commands.check.git import git
from app.commands.check.github import github


@click.group()
def check() -> None:
    """
    Verifies if Git/Github CLI is properly installed for Git-Mastery.
    """
    pass


check.add_command(git)
check.add_command(github)
