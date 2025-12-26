from functools import wraps
from typing import Any, Callable, Dict, Tuple

import click
from app.configs.configs import find_root
from app.configs.gitmastery_config import GITMASTERY_CONFIG_NAME, GitMasteryConfig
from app.hooks.utils import generate_cds_string
from app.utils.click import CliContextKey, error


def in_gitmastery_root(
    must: bool = False,
) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        @click.pass_context
        @wraps(func)
        def wrapper(
            ctx: click.Context, *args: Tuple[Any, ...], **kwargs: Dict[str, Any]
        ) -> Any:
            root = find_root(GITMASTERY_CONFIG_NAME)
            if root is None:
                error(
                    f"You are not in a Git-Mastery root folder. Navigate to an appropriate folder or use "
                    f"{click.style('gitmastery setup', bold=True, italic=True)}"
                )

            path, cds = root
            config = GitMasteryConfig.read(path, cds)

            if must and cds != 0:
                error(
                    f"Use {click.style('cd ' + generate_cds_string(cds), bold=True, italic=True)} "
                    "to move to the root of the Git-Mastery root folder."
                )

            # store config in ctx.obj
            ctx.obj[CliContextKey.GITMASTERY_ROOT_CONFIG] = config

            # call the original command
            return func(*args, **kwargs)

        return wrapper

    return decorator
