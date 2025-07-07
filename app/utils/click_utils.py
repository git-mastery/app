from sys import exit
from typing import Any, Optional

import click


def error(message: str) -> None:
    click.echo(
        f"{click.style(' ERROR ', fg='black', bg='bright_red', bold=True)} {message}"
    )
    exit(1)


def info(message: str) -> None:
    click.echo(
        f"{click.style(' INFO ', fg='black', bg='bright_blue', bold=True)} {message}"
    )


def debug(message: str) -> None:
    click.echo(f"{click.style(' DEBUG ', fg='white', bg='black', bold=True)} {message}")


def warn(message: str) -> None:
    click.echo(
        f"{click.style(' WARN ', fg='black', bg='bright_yellow', bold=True)} {message}"
    )


def success(message: str) -> None:
    click.echo(
        f"{click.style(' SUCCESS ', fg='black', bg='bright_green', bold=True)} {message}"
    )


def prompt(message: str, default: Optional[Any] = None) -> Any:
    return click.prompt(
        f"{click.style(' PROMPT ', fg='black', bg='magenta', bold=True)} {message}",
        default=default,
    )


def confirm(message: str, abort: bool = False) -> bool:
    return click.confirm(f"\n{message}", abort=abort)
