import logging
import sys

import click
from click_aliases import ClickAliasedGroup

from app.aliases import COMMAND_ALIASES
from app.commands import check, download, progress, setup, verify
from app.commands.repl import repl
from app.commands.version import version
from app.utils.click import ClickColor, CliContextKey, warn
from app.utils.version import Version, fetch_latest_release_version
from app.version import __version__


class LoggingGroup(ClickAliasedGroup):
    def invoke(self, ctx: click.Context) -> None:
        logger = logging.getLogger(__name__)
        logger.info("Running command %s with arguments %s", ctx.command_path, sys.argv)
        return super().invoke(ctx)


CONTEXT_SETTINGS = {"max_content_width": 120}


@click.group(
    cls=LoggingGroup,
    context_settings=CONTEXT_SETTINGS,
    invoke_without_command=True,
)
@click.option("--verbose", "-v", is_flag=True, help="Enable verbose output")
@click.pass_context
def cli(ctx: click.Context, verbose: bool) -> None:
    """Git-Mastery app"""
    ctx.ensure_object(dict)

    ctx.obj[CliContextKey.VERBOSE] = verbose

    current_version = Version.parse_version_string(__version__)
    ctx.obj[CliContextKey.VERSION] = current_version

    # Latest version checking is a soft dependency, should not fail operation
    latest_version, latest_version_error = fetch_latest_release_version()
    if latest_version_error is not None:
        warn(latest_version_error)

    if latest_version is not None and current_version.is_behind(latest_version):
        warn(
            click.style(
                f"Your version of Git-Mastery app {current_version} is behind the latest version {latest_version}.",
                fg=ClickColor.BRIGHT_RED,
            )
        )
        warn("We strongly recommend upgrading your app.")
        warn(
            f"Follow the update guide here: {click.style('https://git-mastery.org/companion-app/index.html#updating-the-git-mastery-app', bold=True)}"
        )

    if ctx.invoked_subcommand is None and not ctx.resilient_parsing:
        ctx.invoke(repl)


def start() -> None:
    commands = [check, download, progress, setup, verify, version]
    for command in commands:
        if command.name and command.name in COMMAND_ALIASES:
            cli.add_command(command, aliases=COMMAND_ALIASES[command.name])
        else:
            cli.add_command(command)
    cli(obj={})
