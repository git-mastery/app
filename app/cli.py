import logging
import sys

import click
import requests

from app.commands import check, download, progress, setup, verify
from app.commands.version import version
from app.utils.click import ClickColor, CliContextKey, warn
from app.utils.gitmastery import (
    find_exercise_root,
    find_gitmastery_root,
    read_gitmastery_config,
    read_exercise_config,
)
from app.utils.version import Version
from app.version import __version__


class LoggingGroup(click.Group):
    def invoke(self, ctx: click.Context) -> None:
        logger = logging.getLogger(__name__)
        logger.info("Running command %s with arguments %s", ctx.command_path, sys.argv)
        return super().invoke(ctx)


@click.group(cls=LoggingGroup)
@click.option("--verbose", "-v", is_flag=True, help="Enable verbose output")
@click.pass_context
def cli(ctx, verbose) -> None:
    """Git-Mastery app"""
    ctx.ensure_object(dict)

    # Attempt to load both Git-Mastery root config and exercise config where possible
    gitmastery_root = find_gitmastery_root()
    if gitmastery_root is not None:
        root_path, cds = gitmastery_root
        gitmastery_root_config = read_gitmastery_config(root_path, cds)
        ctx.obj[CliContextKey.GITMASTERY_ROOT_CONFIG] = gitmastery_root_config

    exercise_root = find_exercise_root()
    if exercise_root is not None:
        root_path, cds = exercise_root
        exercise_root_config = read_exercise_config(root_path, cds)
        ctx.obj[CliContextKey.GITMASTERY_EXERCISE_CONFIG] = exercise_root_config

    ctx.obj[CliContextKey.VERBOSE] = verbose

    current_version = Version.parse_version_string(__version__)
    ctx.obj[CliContextKey.VERSION] = current_version
    latest_version = (
        requests.get(
            "https://github.com/git-mastery/app/releases/latest", allow_redirects=False
        )
        .headers["Location"]
        .rsplit("/", 1)[-1]
    )
    if current_version.is_behind(Version.parse_version_string(latest_version)):
        warn(
            click.style(
                f"Your version of Git-Mastery app {current_version} is behind the latest version {latest_version}.",
                fg=ClickColor.BRIGHT_RED,
            )
        )
        warn("We strongly recommend upgrading your app.")
        warn(
            f"Follow the update guide here: {click.style('https://git-mastery.github.io/app/update', bold=True)}"
        )


def start() -> None:
    commands = [check, download, progress, setup, verify, version]
    for command in commands:
        cli.add_command(command)
    cli(obj={})
