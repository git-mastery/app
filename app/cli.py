import click
import requests

from app.commands import check, download, progress, setup, verify
from app.commands.version import version
from app.utils.click_utils import warn
from app.utils.version_utils import Version
from app.version import __version__


@click.group()
@click.option("--verbose", "-v", is_flag=True, help="Enable verbose output")
@click.pass_context
def cli(ctx, verbose) -> None:
    """Git-Mastery CLI"""
    ctx.ensure_object(dict)
    ctx.obj["VERBOSE"] = verbose
    current_version = Version.parse_version_string(__version__)
    tags = requests.get("https://api.github.com/repos/git-mastery/app/tags").json()
    latest_version = Version.parse_version_string(tags[0]["name"])
    if current_version.is_behind(latest_version):
        warn(
            f"Your version of Git-Mastery CLI {click.style(current_version, bold=True)} is behind the latest version {click.style(latest_version, bold=True, italic=True)}. Please update the CLI."
        )


def start() -> None:
    cli.add_command(check)
    cli.add_command(download)
    cli.add_command(progress)
    cli.add_command(setup)
    cli.add_command(verify)
    cli.add_command(version)
    cli(obj={})
