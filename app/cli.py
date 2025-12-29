import logging
import platform
import sys

import click
import requests

from app.commands import check, download, progress, setup, update, verify
from app.commands.version import version
from app.utils.click import ClickColor, CliContextKey, warn
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
        # Auto-update only supported on macOS
        # TODO: Add support for other platforms
        if platform.system().lower() == "darwin":
            warn("Attempting automatic update...")
            ctx.invoke(update)
        else:
            warn("We strongly recommend upgrading your app.")
            warn(
                f"Follow the update guide here: {click.style('https://git-mastery.github.io/app/update', bold=True)}"
            )


def start() -> None:
    commands = [check, download, progress, setup, update, verify, version]
    for command in commands:
        cli.add_command(command)
    cli(obj={})
