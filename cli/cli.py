import click

from cli.commands import check, download, progress, setup, verify


@click.group()
@click.option("--verbose", "-v", is_flag=True, help="Enable verbose output")
@click.pass_context
def cli(ctx, verbose) -> None:
    """Git Mastery CLI"""
    ctx.ensure_object(dict)
    ctx.obj["VERBOSE"] = verbose


def start() -> None:
    cli.add_command(check)
    cli.add_command(download)
    cli.add_command(progress)
    cli.add_command(setup)
    cli.add_command(verify)
    cli(obj={})
