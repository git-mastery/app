from functools import wraps
from typing import Any, Callable

import click

from app.configs.exercise_config import GITMASTERY_EXERCISE_CONFIG_NAME, ExerciseConfig
from app.configs.utils import find_root
from app.hooks.utils import generate_cds_string
from app.utils.click import CliContextKey, error


def in_exercise_root(
    must: bool = False,
) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        @click.pass_context
        @wraps(func)
        def wrapper(
            ctx: click.Context, *args: tuple[Any, ...], **kwargs: dict[str, Any]
        ) -> Any:
            root = find_root(GITMASTERY_EXERCISE_CONFIG_NAME)
            if root is None:
                error("You are not inside a Git-Mastery exercise folder.")

            path, cds = root
            config = ExerciseConfig.read(path, cds)

            if must and cds != 0:
                exercise_name = config.exercise_name
                error(
                    f"Use {click.style('cd ' + generate_cds_string(cds), bold=True, italic=True)} "
                    f"to move to the root of the {click.style(exercise_name, bold=True, italic=True)} exercise folder."
                )

            ctx.obj[CliContextKey.GITMASTERY_EXERCISE_CONFIG] = config
            return func(*args, **kwargs)

        return wrapper

    return decorator
