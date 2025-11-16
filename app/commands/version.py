import click

from app.utils.click import CliContextKey, info


@click.command()
@click.pass_context
def version(ctx: click.Context) -> None:
    info(
        f"Git-Mastery app is {click.style(ctx.obj[CliContextKey.VERSION], bold=True, italic=True)}"
    )
