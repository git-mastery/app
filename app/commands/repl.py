import cmd
import os
import shlex
import subprocess
import sys
from typing import List

import click

from app.commands.check import check
from app.commands.download import download
from app.commands.progress.progress import progress
from app.commands.setup_folder import setup
from app.commands.verify import verify
from app.commands.version import version
from app.utils.click import CliContextKey, ClickColor
from app.utils.version import Version
from app.version import __version__


GITMASTERY_COMMANDS = {
    "check": check,
    "download": download,
    "progress": progress,
    "setup": setup,
    "verify": verify,
    "version": version,
}


class GitMasteryREPL(cmd.Cmd):
    """Interactive REPL for Git-Mastery commands."""

    intro = click.style(
        "\nWelcome to the Git-Mastery REPL!\n"
        "Type 'help' for available commands, or 'exit' to quit.\n"
        "Git-Mastery commands work with or without the 'gitmastery' prefix.\n"
        "Shell commands are also supported.\n",
        fg=ClickColor.BRIGHT_CYAN,
    )

    def __init__(self) -> None:
        super().__init__()
        self._update_prompt()

    def _update_prompt(self) -> None:
        """Update prompt to show current directory."""
        cwd = os.path.basename(os.getcwd()) or os.getcwd()
        self.prompt = click.style(f"gitmastery [{cwd}]> ", fg=ClickColor.BRIGHT_GREEN)

    def postcmd(self, stop: bool, line: str) -> bool:
        """Update prompt after each command."""
        self._update_prompt()
        return stop

    def precmd(self, line: str) -> str:
        """Pre-process command line before execution."""
        # Strip 'gitmastery' prefix if present
        stripped = line.strip()
        if stripped.startswith("gitmastery "):
            return stripped[len("gitmastery ") :]
        return line

    def default(self, line: str) -> None:
        """Handle commands not recognized by cmd module."""
        parts = shlex.split(line)
        if not parts:
            return

        command_name = parts[0]
        args = parts[1:]

        if command_name in GITMASTERY_COMMANDS:
            self._run_gitmastery_command(command_name, args)
            return

        self._run_shell_command(line)

    def _run_gitmastery_command(self, command_name: str, args: List[str]) -> None:
        """Execute a gitmastery command."""
        command = GITMASTERY_COMMANDS[command_name]
        original_cwd = os.getcwd()
        try:
            ctx = command.make_context(command_name, args)
            ctx.ensure_object(dict)
            ctx.obj[CliContextKey.VERBOSE] = False
            ctx.obj[CliContextKey.VERSION] = Version.parse_version_string(__version__)
            with ctx:
                command.invoke(ctx)
        except click.ClickException as e:
            e.show()
        except click.Abort:
            click.echo("Aborted.")
        except SystemExit:
            pass
        except Exception as e:
            click.echo(click.style(f"Error: {e}", fg=ClickColor.BRIGHT_RED))
        finally:
            os.chdir(original_cwd)

    def _run_shell_command(self, line: str) -> None:
        """Execute a shell command via subprocess."""
        try:
            result = subprocess.run(line, shell=True)
            if result.returncode != 0:
                click.echo(
                    click.style(
                        f"Command exited with code {result.returncode}",
                        fg=ClickColor.BRIGHT_YELLOW,
                    )
                )
        except Exception as e:
            click.echo(click.style(f"Shell error: {e}", fg=ClickColor.BRIGHT_RED))

    def do_cd(self, path: str) -> bool:
        """Change directory."""
        if not path:
            path = os.path.expanduser("~")
        try:
            os.chdir(os.path.expanduser(path))
        except FileNotFoundError:
            click.echo(
                click.style(f"Directory not found: {path}", fg=ClickColor.BRIGHT_RED)
            )
        except PermissionError:
            click.echo(
                click.style(f"Permission denied: {path}", fg=ClickColor.BRIGHT_RED)
            )
        return False

    def do_exit(self, arg: str) -> bool:
        """Exit the Git-Mastery REPL."""
        click.echo(click.style("Goodbye!", fg=ClickColor.BRIGHT_CYAN))
        return True

    def do_quit(self, arg: str) -> bool:
        """Exit the Git-Mastery REPL."""
        return self.do_exit(arg)

    def do_help(self, arg: str) -> bool:  # type: ignore[override]
        """Show help for commands."""
        if arg:
            # Check if it's a gitmastery command
            if arg in GITMASTERY_COMMANDS:
                command = GITMASTERY_COMMANDS[arg]
                click.echo(f"\n{arg}: {command.help or 'No description available.'}\n")
                # Show command usage
                with click.Context(command) as ctx:
                    click.echo(command.get_help(ctx))
                return False
            # Fall back to cmd module's help
            super().do_help(arg)
            return False

        # Show general help
        click.echo(
            click.style("\nGit-Mastery Commands:", bold=True, fg=ClickColor.BRIGHT_CYAN)
        )
        for name, command in GITMASTERY_COMMANDS.items():
            help_text = command.help or "No description available."
            click.echo(f"  {click.style(name, bold=True):20} {help_text}")

        click.echo(
            click.style("\nBuilt-in Commands:", bold=True, fg=ClickColor.BRIGHT_CYAN)
        )
        click.echo(f"  {click.style('help', bold=True):20} Show this help message")
        click.echo(f"  {click.style('exit', bold=True):20} Exit the REPL")
        click.echo(f"  {click.style('quit', bold=True):20} Exit the REPL")

        click.echo(
            click.style(
                "\nAll other commands are passed to the shell.",
                fg=ClickColor.BRIGHT_YELLOW,
            )
        )
        click.echo()
        return False

    def emptyline(self) -> bool:  # type: ignore[override]
        """Do nothing on empty line (don't repeat last command)."""
        return False

    def do_EOF(self, arg: str) -> bool:
        """Handle Ctrl+D."""
        click.echo()  # Print newline
        return self.do_exit(arg)


@click.command()
def repl() -> None:
    """Start an interactive REPL session."""
    repl_instance = GitMasteryREPL()

    try:
        repl_instance.cmdloop()
    except KeyboardInterrupt:
        click.echo(click.style("\nInterrupted. Goodbye!", fg=ClickColor.BRIGHT_CYAN))
        sys.exit(0)
