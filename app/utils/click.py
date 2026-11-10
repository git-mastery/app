import logging
import sys
from collections.abc import Callable, Iterator
from contextlib import contextmanager, redirect_stdout
from contextvars import ContextVar
from enum import StrEnum
from functools import wraps
from typing import Any, NoReturn, Optional, ParamSpec, TextIO, TypeVar

import click

from app.configs.exercise_config import ExerciseConfig
from app.configs.gitmastery_config import GitMasteryConfig

logger = logging.getLogger(__name__)

_JSON_STDOUT: ContextVar[Optional[TextIO]] = ContextVar("json_stdout", default=None)
P = ParamSpec("P")
T = TypeVar("T")


@contextmanager
def json_output_scope(enabled: bool = True) -> Iterator[TextIO]:
    """Reserve stdout for JSON and route Python diagnostics to stderr.

    :param enabled: Whether to enable JSON output routing.
    :yield: The original stdout stream for the JSON result.
    """
    saved_stdout = _JSON_STDOUT.get()
    if not enabled or saved_stdout is not None:
        yield saved_stdout if saved_stdout is not None else sys.stdout
        return

    saved_stdout = sys.stdout
    token = _JSON_STDOUT.set(saved_stdout)
    try:
        with redirect_stdout(sys.stderr):
            yield saved_stdout
    finally:
        _JSON_STDOUT.reset(token)


def with_json_output(func: Callable[P, T]) -> Callable[P, T]:
    """Route diagnostics before command guards when ``json_output`` is enabled."""

    @wraps(func)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
        with json_output_scope(bool(kwargs.get("json_output", False))):
            return func(*args, **kwargs)

    return wrapper


def get_json_output_stream() -> TextIO:
    """Return the stdout stream reserved for the JSON result."""
    saved_stdout = _JSON_STDOUT.get()
    return saved_stdout if saved_stdout is not None else sys.stdout


class CliContextKey(StrEnum):
    GITMASTERY_ROOT_CONFIG = "GITMASTERY_ROOT_CONFIG"
    GITMASTERY_EXERCISE_CONFIG = "GITMASTERY_EXERCISE_CONFIG"
    VERBOSE = "VERBOSE"
    VERSION = "VERSION"


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


def error(message: str) -> NoReturn:
    logger.error(message)
    click.echo(
        f"{click.style(' ERROR ', fg=ClickColor.BLACK, bg=ClickColor.BRIGHT_RED, bold=True)} {message}"
    )
    sys.exit(1)


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


def get_verbose() -> bool:
    return click.get_current_context().obj.get(CliContextKey.VERBOSE, False)


def get_gitmastery_root_config() -> Optional[GitMasteryConfig]:
    return click.get_current_context().obj.get(
        CliContextKey.GITMASTERY_ROOT_CONFIG, None
    )


def must_get_gitmastery_root_config() -> GitMasteryConfig:
    v = get_gitmastery_root_config()
    if v is None:
        raise ValueError("Git-Mastery root config expected.")
    return v


def get_exercise_root_config() -> Optional[ExerciseConfig]:
    return click.get_current_context().obj.get(
        CliContextKey.GITMASTERY_EXERCISE_CONFIG, None
    )


def must_get_exercise_root_config() -> ExerciseConfig:
    v = get_exercise_root_config()
    if v is None:
        raise ValueError("Git-Mastery exercise config expected.")
    return v


def invoke_command(command: click.Command) -> None:
    ctx = click.get_current_context()
    ctx.invoke(command)
