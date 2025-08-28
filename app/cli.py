import logging
import sys

import click
import requests

from app.commands import check, download, progress, setup, verify
from app.commands.version import version
from app.utils.click import warn
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
    ctx.obj["VERBOSE"] = verbose
    current_version = Version.parse_version_string(__version__)
    req = requests.get("https://api.github.com/repos/git-mastery/app/tags")
    if req.ok:
        # Only continue with checks if request succeeds
        # Request could fail due to Github API rate limits or other errors
        tags = req.json()
        latest_version = Version.parse_version_string(tags[0]["name"])
        if current_version.is_behind(latest_version):
            warn(
                click.style(
                    f"Your version of Git-Mastery app {current_version} is behind the latest version {latest_version}.",
                    fg="bright_red",
                )
            )
            warn("We strongly recommend upgrading your app.")
            warn(
                f"Follow the update guide here: {click.style('https://git-mastery.github.io/app/update', bold=True)}"
            )


def start() -> None:
    cli.add_command(check)
    cli.add_command(download)
    cli.add_command(progress)
    cli.add_command(setup)
    cli.add_command(verify)
    cli.add_command(version)
    cli(obj={})
