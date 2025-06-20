from datetime import date
from enum import Enum
from typing import List
import click
import yaml

from cli.utils.click_utils import confirm, error, info, prompt, warn
from cli.utils.gitmastery_utils import (
    fetch_file_contents,
    fetch_file_contents_or_none,
    find_gitmastery_exercise_root,
    get_gitmastery_file_path,
    read_gitmastery_exercise_config,
)


class InstructionPart(Enum):
    DESCRIPTION = 0
    OUTCOMES = 1
    TASK = 2
    VERIFICATION = 3
    HINT = 4


@click.group()
def instructions():
    pass


@instructions.command()
@click.option("--all", is_flag=True, default=False)
@click.option("--description", is_flag=True, default=False)
@click.option("--outcomes", is_flag=True, default=False)
@click.option("--task", is_flag=True, default=False)
@click.option("--verification", is_flag=True, default=False)
def view(
    all: bool,
    description: bool,
    outcomes: bool,
    task: bool,
    verification: bool,
) -> None:
    gitmastery_exercise_root = find_gitmastery_exercise_root()
    if gitmastery_exercise_root is None:
        error("You are not inside a Git-Mastery exercise folder.")

    assert gitmastery_exercise_root is not None
    gitmastery_exercise_root_path, _ = gitmastery_exercise_root
    gitmastery_exercise_config = read_gitmastery_exercise_config(
        gitmastery_exercise_root_path
    )
    exercise_name = gitmastery_exercise_config["exercise_name"]
    formatted_exercise_name = exercise_name.replace("-", "_")

    instructions_yml = fetch_file_contents_or_none(
        get_gitmastery_file_path(f"{formatted_exercise_name}/instructions.yml"),
        is_binary=False,
    )
    if instructions_yml is None:
        warn(
            f"Exercise {click.style(exercise_name, bold=True, italic=True)} does not have an instructions.yml, displaying the README.md instead."
        )
        warn("Consider contacting the Git-Mastery team to add proper instructions.yml")
        readme_contents = fetch_file_contents(
            get_gitmastery_file_path(f"{formatted_exercise_name}/README.md"),
            is_binary=False,
        )
        click.echo_via_pager(str(readme_contents))
        return

    info("Reading instructions...")
    instructions = yaml.load(instructions_yml, yaml.FullLoader)

    to_display = []
    if all:
        to_display = [
            InstructionPart.DESCRIPTION,
            InstructionPart.OUTCOMES,
            InstructionPart.TASK,
            InstructionPart.VERIFICATION,
        ]
    else:
        if description:
            to_display.append(InstructionPart.DESCRIPTION)

        if outcomes:
            to_display.append(InstructionPart.OUTCOMES)

        if task:
            to_display.append(InstructionPart.TASK)

        if verification:
            to_display.append(InstructionPart.VERIFICATION)

    if not to_display:
        error(
            "Missing any of the flags, use at least one: --description, --outcomes, --task, --verification or --all to view everything"
        )

    content = []
    for display in to_display:
        if display == InstructionPart.DESCRIPTION:
            content.append(
                click.style("DESCRIPTION", bold=True, italic=True)
                + "\n"
                + instructions["description"]
            )

        if display == InstructionPart.OUTCOMES:
            content.append(
                click.style("OUTCOMES", bold=True, italic=True)
                + "\n"
                + "\n".join([f"- {outcome}" for outcome in instructions["outcomes"]])
            )

        if display == InstructionPart.TASK:
            content.append(
                click.style("TASK", bold=True, italic=True)
                + "\n"
                + instructions["task"]
            )

        if display == InstructionPart.VERIFICATION:
            content.append(
                click.style("VERIFICATION", bold=True, italic=True)
                + "\n"
                + instructions["verification"]
            )

    click.echo_via_pager("\n\n==============================\n\n".join(content))


@instructions.command()
def hints():
    gitmastery_exercise_root = find_gitmastery_exercise_root()
    if gitmastery_exercise_root is None:
        error("You are not inside a Git-Mastery exercise folder.")

    assert gitmastery_exercise_root is not None
    gitmastery_exercise_root_path, _ = gitmastery_exercise_root
    gitmastery_exercise_config = read_gitmastery_exercise_config(
        gitmastery_exercise_root_path
    )
    exercise_name = gitmastery_exercise_config["exercise_name"]
    formatted_exercise_name = exercise_name.replace("-", "_")

    instructions_yml = fetch_file_contents_or_none(
        get_gitmastery_file_path(f"{formatted_exercise_name}/instructions.yml"),
        is_binary=False,
    )
    if instructions_yml is None:
        warn(
            f"Exercise {click.style(exercise_name, bold=True, italic=True)} does not have an instructions.yml, displaying the README.md instead."
        )
        warn("Consider contacting the Git-Mastery team to add proper instructions.yml")
        readme_contents = fetch_file_contents(
            get_gitmastery_file_path(f"{formatted_exercise_name}/README.md"),
            is_binary=False,
        )
        click.echo_via_pager(str(readme_contents))
        return

    info("Reading instructions...")
    instructions = yaml.load(instructions_yml, yaml.FullLoader)
    hints = instructions["hints"]
    for i in range(len(hints)):
        show_hint = confirm(f"Do you want to see hint {i + 1}/{len(hints)}?")
        if show_hint:
            print(hints[i])
        else:
            break
