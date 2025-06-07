import importlib.util
import json
import os
import subprocess
import sys
import urllib.parse
from datetime import datetime
from pathlib import Path
from sys import exit
from typing import Any, Dict, List, Optional, Tuple

import click
import pytz
import requests
from git_autograder import (
    GitAutograderInvalidStateException,
    GitAutograderRepo,
    GitAutograderStatus,
    GitAutograderWrongAnswerException,
)
from git_autograder.output import GitAutograderOutput

GITMASTERY_EXERCISES_BASE_URL = (
    "https://raw.githubusercontent.com/git-mastery/exercises/refs/heads/main/"
)


def error(message: str) -> None:
    click.echo(
        f"{click.style(' ERROR ', fg='black', bg='bright_red', bold=True)} {message}"
    )
    exit()


def info(message: str) -> None:
    click.echo(
        f"{click.style(' INFO ', fg='black', bg='bright_blue', bold=True)} {message}"
    )


def debug(message: str) -> None:
    click.echo(f"{click.style(' DEBUG ', fg='white', bg='black', bold=True)} {message}")


def warn(message: str) -> None:
    click.echo(
        f"{click.style(' WARN ', fg='black', bg='bright_yellow', bold=True)} {message}"
    )


def prompt(message: str, default: Optional[Any] = None) -> Any:
    return click.prompt(f"\n{message}", default=default)


def confirm(message: str, abort: bool = False) -> bool:
    return click.confirm(f"\n{message}", abort=abort)


def execute_py_file_function_from_url(
    exercise: str, file_path: str, function_name: str, **params: Dict[str, Any]
) -> Optional[Any]:
    sys.dont_write_bytecode = True
    py_file = fetch_file_contents(
        get_gitmastery_file_path(f"{exercise}/{file_path}"), False
    )
    namespace: Dict[str, Any] = {}
    exec(py_file, namespace)
    result = namespace[function_name](**params)
    sys.dont_write_bytecode = False
    return result


def execute_py_file_function_from_file(
    file_path: str, function_name: str, **params: Dict[Any, Any]
) -> Optional[Any]:
    path = Path(file_path)
    sys.dont_write_bytecode = True
    spec = importlib.util.spec_from_file_location(function_name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    func = getattr(module, function_name, None)
    if callable(func):
        result = func(**params)
        sys.dont_write_bytecode = False
        return result
    sys.dont_write_bytecode = False
    return None


def get_gitmastery_file_path(path: str):
    return urllib.parse.urljoin(GITMASTERY_EXERCISES_BASE_URL, path)


def fetch_file_contents(url: str, is_binary: bool) -> str | bytes:
    response = requests.get(url)

    if response.status_code == 200:
        if is_binary:
            return response.content
        return response.text
    else:
        error(
            f"Failed to fetch resource {click.style(url, bold=True, italic=True)}. Inform the Git-Mastery team."
        )
    return ""


def download_file(url: str, path: str, is_binary: bool) -> None:
    contents = fetch_file_contents(url, is_binary)
    if is_binary:
        assert isinstance(contents, bytes)
        with open(path, "wb") as file:
            file.write(contents)
    else:
        assert isinstance(contents, str)
        with open(path, "w+") as file:
            file.write(contents)


def check_binary(binary: str, error_message: str, verbose: bool = False) -> None:
    stdout = None if verbose else subprocess.DEVNULL
    stderr = None if verbose else subprocess.DEVNULL
    if subprocess.call(["which", binary], stdout=stdout, stderr=stderr) != 0:
        error(error_message)


def is_authenticated(verbose: bool = False) -> bool:
    stdout = None if verbose else subprocess.DEVNULL
    stderr = None if verbose else subprocess.DEVNULL
    return subprocess.call(["gh", "auth", "status"], stdout=stdout, stderr=stderr) == 0


def has_fork(fork_name: str, verbose: bool = False) -> bool:
    stdout = None if verbose else subprocess.DEVNULL
    stderr = None if verbose else subprocess.DEVNULL
    try:
        subprocess.run(
            ["gh", "repo", "view", fork_name], check=True, stdout=stdout, stderr=stderr
        )
        return True
    except subprocess.CalledProcessError:
        return False


def get_username(verbose: bool = False) -> str:
    try:
        result = subprocess.run(
            ["gh", "api", "user", "-q", ".login"],
            capture_output=True,
            text=True,
            check=True,
        )
        username = result.stdout.strip().splitlines()[0]
        if verbose:
            info(username)
        return username
    except subprocess.CalledProcessError as e:
        if verbose:
            error(e.stderr)
        return ""


def get_user_orgs(verbose: bool = False) -> List[str]:
    try:
        result = subprocess.run(
            [
                "gh",
                "api",
                "-H",
                "Accept: application/vnd.github+json",
                "/user/orgs",
                "--jq",
                ".[].login",
                "--paginate",
            ],
            capture_output=True,
            text=True,
            check=True,
        )
        org_names = result.stdout.strip().splitlines()
        if verbose:
            info(", ".join(org_names))
        return org_names
    except subprocess.CalledProcessError as e:
        if verbose:
            error(e.stderr)
        return []


def get_user_prs(repo: str, owner: str, verbose: bool = False) -> List[str]:
    try:
        result = subprocess.run(
            [
                "gh",
                "pr",
                "list",
                "--repo",
                repo,
                "--author",
                "@me",
                "--head",
                "submission",
                "--json",
                "headRepositoryOwner",
                "--json",
                "url",
                "-q",
                f'.[] | select ( .headRepositoryOwner.login == "{owner}" ) | .url',
            ],
            capture_output=True,
            text=True,
            check=True,
            env=dict(os.environ, **{"GH_PAGER": "cat"}),
        )
        prs = result.stdout.strip().splitlines()
        if verbose:
            info(", ".join(prs))
        return prs
    except subprocess.CalledProcessError as e:
        if verbose:
            error(e.stderr)
        return []


def find_gitmastery_root() -> Optional[Tuple[Path, int]]:
    current = Path.cwd()
    steps = 0
    for parent in [current] + list(current.parents):
        if (parent / ".gitmastery.json").is_file():
            return parent, steps
        steps += 1

    return None


def read_gitmastery_config(gitmastery_config_path: Path) -> Dict:
    with open(gitmastery_config_path / ".gitmastery.json", "r") as f:
        return json.loads(f.read())


def find_gitmastery_exercise_root() -> Optional[Tuple[Path, int]]:
    current = Path.cwd()
    steps = 0
    for parent in [current] + list(current.parents):
        if (parent / ".gitmastery-exercise.json").is_file():
            return parent, steps
        steps += 1

    return None


def read_gitmastery_exercise_config(gitmastery_exercise_config_path: Path) -> Dict:
    with open(gitmastery_exercise_config_path / ".gitmastery-exercise.json", "r") as f:
        return json.loads(f.read())


@click.group()
@click.option("--verbose", "-v", is_flag=True, help="Enable verbose output")
@click.pass_context
def cli(ctx, verbose) -> None:
    """Git Mastery CLI"""
    ctx.ensure_object(dict)
    ctx.obj["VERBOSE"] = verbose


@cli.command()
@click.pass_context
def setup(_: click.Context) -> None:
    info(
        "Welcome to Git-Mastery! We will be setting up several components of Git-Mastery to ensure an optimal experience working on the various exercises."
    )
    directory_name = prompt(
        "What do you want to name your exercises directory?",
        default="gitmastery-exercises",
    )

    if os.path.isdir(directory_name):
        error(
            f"Directory {directory_name} already exists in this folder, specify a new folder name."
        )

    directory_path = os.path.join(os.getcwd(), directory_name)

    info(f"Creating directory {click.style(directory_path, italic=True, bold=True)}")
    os.makedirs(directory_name, exist_ok=True)
    open(os.path.join(directory_name, ".gitmastery.json"), "a").close()

    info(
        f"Setup complete. Your directory is: {click.style(directory_name, bold=True, italic=True)}"
    )


@cli.command()
@click.argument("exercise")
@click.pass_context
def download(ctx: click.Context, exercise: str) -> None:
    """Download an exercise"""
    verbose = ctx.obj["VERBOSE"]

    formatted_exercise = exercise.replace("-", "_")

    # Check to make sure that they are currently in the root of a gitmastery exercises
    # folder, denoted by the .gitmastery.json file
    gitmastery_root = find_gitmastery_root()
    if gitmastery_root is None:
        error(
            f"You are not in a Git-Mastery exercises folder. Navigate to an appropriate folder or use {click.style('gitmastery setup', bold=True, italic=True)}"
        )

    # Just asserting since mypy doesn't recognize that error will exit the program
    assert gitmastery_root is not None
    _, steps_to_cd = gitmastery_root
    if steps_to_cd != 0:
        cd = "/".join([".."] * steps_to_cd)
        error(
            f"Use {click.style('cd ' + cd, bold=True, italic=True)} the root of the Git-Mastery exercises folder to download a new exercise."
        )

    info(f"Downloading {exercise}...")

    stdout = None if verbose else subprocess.DEVNULL
    stderr = None if verbose else subprocess.DEVNULL

    info(
        f"Downloaded {exercise} to {click.style(formatted_exercise + '/', bold=True, italic=True)}, setting it up now..."
    )
    if not os.path.isdir(formatted_exercise):
        os.makedirs(formatted_exercise)

    os.chdir(formatted_exercise)
    info("Downloading base files...")
    base_files = [
        ".gitmastery-exercise.json",
        "README.md",
    ]
    for file in base_files:
        download_file(
            get_gitmastery_file_path(f"{formatted_exercise}/{file}"), f"./{file}", False
        )
    config = read_gitmastery_exercise_config(Path("./"))

    if len(config.get("resources", {})) > 0:
        info("Downloading resources...")

    for resource, path in config.get("resources", {}).items():
        os.makedirs(Path(path).parent, exist_ok=True)
        is_binary = Path(path).suffix in [".png", ".jpg", ".jpeg", ".gif"]
        # Download and load all of these resources
        download_file(
            get_gitmastery_file_path(f"{formatted_exercise}/res/{resource}"),
            path,
            is_binary,
        )

    if config.get("requires_repo", True):
        info("Setting up exercise with Git")
        subprocess.run(["git", "init"], stdout=stdout, stderr=stderr)
        subprocess.run(["git", "add", "."], stdout=stdout, stderr=stderr)
        subprocess.run(
            ["git", "commit", "-m", "Initial commit"], stdout=stdout, stderr=stderr
        )
    info("Executing download setup")
    execute_py_file_function_from_url(
        formatted_exercise, "download.py", "setup", verbose=verbose
    )
    info(f"Completed setting up {click.style(exercise, bold=True, italic=True)}")
    info("Start working on it:")
    info(click.style(f"cd {formatted_exercise}", bold=True, italic=True))


@cli.command()
@click.pass_context
def verify(_ctx: click.Context) -> None:
    # Locally verify the changes
    # Check that current folder is exercise
    gitmastery_exercise_root = find_gitmastery_exercise_root()
    if gitmastery_exercise_root is None:
        error("You are not inside a Git-Mastery exercise folder.")

    started_at = datetime.now(tz=pytz.UTC)

    assert gitmastery_exercise_root is not None
    gitmastery_exercise_root_path, _ = gitmastery_exercise_root
    gitmastery_exercise_config = read_gitmastery_exercise_config(
        gitmastery_exercise_root_path
    )
    exercise_name = gitmastery_exercise_config["exercise_name"]
    formatted_exercise_name = exercise_name.replace("-", "_")

    info(
        f"Starting verification of {click.style(exercise_name, bold=True, italic=True)}"
    )

    requires_repo = gitmastery_exercise_config.get("requires_repo", True)
    output: Optional[GitAutograderOutput]
    try:
        if requires_repo:
            current_repo = GitAutograderRepo(exercise_name, ".")
            output = execute_py_file_function_from_url(
                formatted_exercise_name,
                "verify.py",
                "verify",
                repo=current_repo,  # type: ignore
            )
        else:
            output = execute_py_file_function_from_url(
                formatted_exercise_name, "verify.py", "verify"
            )
    except (
        GitAutograderInvalidStateException,
        GitAutograderWrongAnswerException,
    ) as e:
        output = GitAutograderOutput(
            exercise_name=exercise_name,
            started_at=started_at,
            completed_at=datetime.now(tz=pytz.UTC),
            comments=[e.message] if isinstance(e.message, str) else e.message,
            status=(
                GitAutograderStatus.ERROR
                if isinstance(e, GitAutograderInvalidStateException)
                else GitAutograderStatus.UNSUCCESSFUL
            ),
        )
    except Exception as e:
        # Unexpected exception
        output = GitAutograderOutput(
            exercise_name=exercise_name,
            started_at=None,
            completed_at=None,
            comments=[str(e)],
            status=GitAutograderStatus.ERROR,
        )

    assert output is not None
    info("Verification completed.")
    info("")
    info(f"{click.style('Status:', bold=True)} {output.status}")
    info(click.style("Comments:", bold=True))
    print("\n".join([f"\t- {comment}" for comment in (output.comments or [])]))


if __name__ == "__main__":
    cli(obj={})
