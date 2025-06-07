from cli import cli
from cli.commands import check, download, setup, verify

if __name__ == "__main__":
    cli.cli.add_command(check)
    cli.cli.add_command(download)
    cli.cli.add_command(setup)
    cli.cli.add_command(verify)
    cli.cli(obj={})
