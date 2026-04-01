import cmd
import os
import shlex
import subprocess
import sys
from typing import List

import click

from app.aliases import COMMAND_ALIASES, resolve_alias
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

    intro_msg = r"""
 _____ _ _  ___  ___          _                  
|  __ (_) | |  \/  |         | |                 
| |  \/_| |_| .  . | __ _ ___| |_ ___ _ __ _   _ 
| | __| | __| |\/| |/ _` / __| __/ _ \ '__| | | |
| |_\ \ | |_| |  | | (_| \__ \ ||  __/ |  | |_| |
 \____/_|\__\_|  |_/\__,_|___/\__\___|_|   \__, |
                                            __/ |
                                           |___/ 

Welcome to the Git-Mastery REPL!
Type '/help' for available commands, or '/exit' to quit.
Use /command to run Git-Mastery commands (e.g. /verify), or 'gitmastery command'.
Shell commands are also supported.
     """

    intro = click.style(
        intro_msg,
        bold=True,
        fg=ClickColor.BRIGHT_CYAN,
    )

    def __init__(self) -> None:
        super().__init__()
        self._update_prompt()

    def _update_prompt(self) -> None:
        """Update prompt to show current directory."""
        cwd = os.path.basename(os.getcwd()) or os.getcwd()
        self.prompt = f"gitmastery [{cwd}]> "

    def postcmd(self, stop: bool, line: str) -> bool:
        """Update prompt after each command."""
        self._update_prompt()
        return stop

    def precmd(self, line: str) -> str:
        """Pre-process command line before execution."""
        stripped = line.strip()
        if stripped.startswith("/"):
            return "gitmastery " + stripped[1:]
        return line

    def default(self, line: str) -> None:
        """Handle commands not recognized by cmd module."""
        try:
            parts = shlex.split(line)
        except ValueError as e:
            click.echo(click.style(f"Input error: {e}", fg=ClickColor.BRIGHT_RED))
            return

        if not parts:
            return

        command_name = parts[0]
        args = parts[1:]

        if command_name.lower() == "gitmastery":
            if not args:
                return
            gitmastery_command = resolve_alias(args[0])
            if gitmastery_command in ("exit", "quit"):
                return self.do_exit("")  # type: ignore[return-value]
            elif gitmastery_command == "help":
                self.do_help("")
            elif gitmastery_command in GITMASTERY_COMMANDS:
                self._run_gitmastery_command(gitmastery_command, args[1:])
            else:
                click.echo(
                    click.style(
                        f"Unknown Git-Mastery command: {gitmastery_command}",
                        fg=ClickColor.BRIGHT_RED,
                    )
                )
            return

        self._run_shell_command(line)

    def _run_gitmastery_command(self, command_name: str, args: List[str]) -> None:
        """Execute a gitmastery command."""
        command = GITMASTERY_COMMANDS[command_name]
        original_cwd = os.getcwd()
        try:
            ctx = command.make_context(f"/{command_name}", args)
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
            try:
                os.chdir(original_cwd)
            except (FileNotFoundError, PermissionError, OSError) as e:
                click.echo(
                    click.style(
                        f"Warning: Could not restore original directory: {e}",
                        fg=ClickColor.BRIGHT_YELLOW,
                    )
                )

    def _run_shell_command(self, line: str) -> None:
        """Execute a shell command via subprocess."""
        try:
            subprocess.run(line, shell=True)
        except Exception as e:
            click.echo(click.style(f"Shell error: {e}", fg=ClickColor.BRIGHT_RED))

    def do_cd(self, path: str) -> bool:
        """Change directory."""
        if not path:
            path = os.path.expanduser("~")
        else:
            try:
                parts = shlex.split(path)
                path = parts[0] if parts else ""
            except ValueError:
                pass
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
        except OSError as e:
            click.echo(
                click.style(f"Cannot change directory: {e}", fg=ClickColor.BRIGHT_RED)
            )
        return False

    def do_exit(self, args: str) -> bool:
        """Exit the Git-Mastery REPL."""
        click.echo(click.style("Goodbye!", fg=ClickColor.BRIGHT_CYAN))
        return True

    def do_quit(self, args: str) -> bool:
        """Exit the Git-Mastery REPL."""
        return self.do_exit(args)

    def do_help(self, arg: str) -> bool:
        """Show help for commands."""
        click.echo(
            click.style("\nGit-Mastery Commands:", bold=True, fg=ClickColor.BRIGHT_CYAN)
        )
        for name, command in GITMASTERY_COMMANDS.items():
            help_text = (command.help or "No description available.").strip()
            aliases = COMMAND_ALIASES.get(name, [])
            alias_str = f" (/{', /'.join(aliases)})" if aliases else ""
            label = f"/{name}{alias_str}"
            click.echo(f"  {click.style(f'{label:<25}', bold=True)} {help_text}")

        click.echo(
            click.style("\nBuilt-in Commands:", bold=True, fg=ClickColor.BRIGHT_CYAN)
        )
        for name, desc in [
            ("/help", "Show this help message"),
            ("/exit", "Exit the REPL"),
            ("/quit", "Exit the REPL"),
        ]:
            click.echo(f"  {click.style(f'{name:<20}', bold=True)} {desc}")
        click.echo()
        return False

    def emptyline(self) -> bool:
        """Do nothing on empty line (don't repeat last command)."""
        return False

    def do_EOF(self, _arg: str) -> bool:
        """Handle Ctrl+D."""
        click.echo()
        return self.do_exit(_arg)


@click.command()
def repl() -> None:
    """Start an interactive REPL session."""
    repl_instance = GitMasteryREPL()

    try:
        repl_instance.cmdloop()
    except KeyboardInterrupt:
        click.echo(click.style("\nInterrupted. Goodbye!", fg=ClickColor.BRIGHT_CYAN))
        sys.exit(0)
