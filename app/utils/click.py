import logging
from enum import StrEnum
from sys import exit
from typing import Any, Optional

import click

logger = logging.getLogger(__name__)


class ClickColor(StrEnum):
    BLACK = "black"
    RED = "red"
    GREEN = "green"
    YELLOW = "yellow"
    BLUE = "blue"
    MAGENTA = "magenta"
    CYAN = "cyan"
    WHITE = "white"
    BRIGHT_BLACK = "bright_black"
    BRIGHT_RED = "bright_red"
    BRIGHT_GREEN = "bright_green"
    BRIGHT_YELLOW = "bright_yellow"
    BRIGHT_BLUE = "bright_blue"
    BRIGHT_MAGENTA = "bright_magenta"
    BRIGHT_CYAN = "bright_cyan"
    BRIGHT_WHITE = "bright_white"


def error(message: str) -> None:
    logger.error(message)
    click.echo(
        f"{click.style(' ERROR ', fg=ClickColor.BLACK, bg=ClickColor.BRIGHT_RED, bold=True)} {message}"
    )
    exit(1)


def info(message: str) -> None:
    logger.info(message)
    click.echo(
        f"{click.style(' INFO ', fg=ClickColor.BLACK, bg=ClickColor.BRIGHT_BLUE, bold=True)} {message}"
    )


def debug(message: str) -> None:
    logger.debug(message)
    click.echo(
        f"{click.style(' DEBUG ', fg=ClickColor.WHITE, bg=ClickColor.BLACK, bold=True)} {message}"
    )


def warn(message: str) -> None:
    logger.warning(message)
    click.echo(
        f"{click.style(' WARN ', fg=ClickColor.BLACK, bg=ClickColor.BRIGHT_YELLOW, bold=True)} {message}"
    )


def success(message: str) -> None:
    logger.info(message)
    click.echo(
        f"{click.style(' SUCCESS ', fg=ClickColor.BLACK, bg=ClickColor.BRIGHT_GREEN, bold=True)} {message}"
    )


def prompt(message: str, default: Optional[Any] = None) -> Any:
    logger.info(f"Prompted user '{message}'")
    response = click.prompt(
        f"{click.style(' PROMPT ', fg=ClickColor.BLACK, bg=ClickColor.MAGENTA, bold=True)} {message}",
        default=default,
    )
    logger.info(f"Response to prompt: {response}")
    return response


def confirm(message: str, abort: bool = False) -> bool:
    logger.info(f"Confirming: '{message}'")
    response = click.confirm(
        f"{click.style(' CONFIRM ', fg=ClickColor.BLACK, bg=ClickColor.BRIGHT_CYAN, bold=True)} {message}",
        abort=abort,
    )
    logger.info(f"Response to confirmation: {response}")
    return response


def get_verbose_from_click_context() -> bool:
    return click.get_current_context().obj["VERBOSE"]


def invoke_command(command: click.Command) -> None:
    ctx = click.get_current_context()
    ctx.invoke(command)
