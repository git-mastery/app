import json
import os
import sys
import tempfile
import urllib.parse
from pathlib import Path
from typing import Any, Dict, Optional, Tuple, TypeVar, Union

import click
import requests

from app.exercise_config import ExerciseConfig
from app.gitmastery_config import GitMasteryConfig
from app.utils.click import error, get_exercise_root_config, get_gitmastery_root_config
from app.utils.general import ensure_str

GITMASTERY_CONFIG_NAME = ".gitmastery.json"
GITMASTERY_EXERCISE_CONFIG_NAME = ".gitmastery-exercise.json"
GITMASTERY_EXERCISES_BASE_URL = (
    "https://raw.githubusercontent.com/git-mastery/exercises/refs/heads/main/"
)


def _find_root(filename: str) -> Optional[Tuple[Path, int]]:
    current = Path.cwd()
    steps = 0
    for parent in [current] + list(current.parents):
        if (parent / filename).is_file():
            return parent, steps
        steps += 1

    return None


def _read_config(path: Path, filename: str) -> Dict:
    with open(path / filename, "r") as f:
        return json.loads(f.read())


def find_gitmastery_root() -> Optional[Tuple[Path, int]]:
    return _find_root(GITMASTERY_CONFIG_NAME)


def is_in_gitmastery_root() -> GitMasteryConfig:
    config = get_gitmastery_root_config()
    if config is None:
        error(
            f"You are not in a Git-Mastery root folder. Navigate to an appropriate folder or use {click.style('gitmastery setup', bold=True, italic=True)}"
        )
    return config


def must_be_in_gitmastery_root() -> GitMasteryConfig:
    config = is_in_gitmastery_root()
    cds = config.cds
    if cds != 0:
        error(
            f"Use {click.style('cd ' + generate_cds_string(cds), bold=True, italic=True)} to move to the root of the Git-Mastery root folder."
        )
    return config


def read_gitmastery_config(gitmastery_config_path: Path, cds: int) -> GitMasteryConfig:
    raw_config = _read_config(gitmastery_config_path, GITMASTERY_CONFIG_NAME)
    return GitMasteryConfig(
        path=gitmastery_config_path,
        cds=cds,
        progress_local=raw_config.get("progress_local", False),
        progress_remote=raw_config.get("progress_remote", False),
    )


def find_exercise_root() -> Optional[Tuple[Path, int]]:
    return _find_root(GITMASTERY_EXERCISE_CONFIG_NAME)


def is_in_exercise_root() -> ExerciseConfig:
    config = get_exercise_root_config()
    if config is None:
        error("You are not inside a Git-Mastery exercise folder.")
    return config


def must_be_in_exercise_root() -> ExerciseConfig:
    config = is_in_exercise_root()
    cds = config.cds
    if cds != 0:
        exercise_name = config.exercise_name
        error(
            f"Use {click.style('cd ' + generate_cds_string(cds), bold=True, italic=True)} to move to the root of the {click.style(exercise_name, bold=True, italic=True)} exercise folder."
        )
    return config


def read_exercise_config(exercise_config_path: Path, cds: int) -> ExerciseConfig:
    raw_config = _read_config(exercise_config_path, GITMASTERY_EXERCISE_CONFIG_NAME)
    exercise_repo = raw_config["exercise_repo"]
    return ExerciseConfig(
        path=exercise_config_path,
        cds=cds,
        exercise_name=raw_config["exercise_name"],
        tags=raw_config["tags"],
        requires_git=raw_config["requires_git"],
        requires_github=raw_config["requires_github"],
        base_files=raw_config["base_files"],
        exercise_repo=ExerciseConfig.ExerciseRepoConfig(
            repo_type=exercise_repo["repo_type"],  # type: ignore
            repo_name=exercise_repo["repo_name"],
            repo_title=exercise_repo["repo_title"],
            create_fork=exercise_repo["create_fork"],
            init=exercise_repo["init"],
        ),
        downloaded_at=None,
    )


def generate_cds_string(cds: int) -> str:
    # TODO: Maybe support Windows as well?
    return "/".join([".."] * cds)


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


def fetch_file_contents_or_none(
    url: str, is_binary: bool
) -> Optional[Union[str, bytes]]:
    response = requests.get(url)

    if response.status_code == 200:
        if is_binary:
            return response.content
        return response.text
    return None


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


T = TypeVar("T")


def get_variable_from_url(
    exercise: str,
    file_path: str,
    variable_name: str,
    default_value: Optional[T] = None,
) -> Optional[T]:
    namespace = load_namespace_with_exercise_utils(f"{exercise}/{file_path}")
    variable = namespace.get(variable_name, default_value)
    return variable


def exercise_exists(exercise: str, timeout: int = 5) -> bool:
    try:
        response = requests.head(
            get_gitmastery_file_path(
                f"{exercise.replace('-', '_')}/.gitmastery-exercise.json"
            ),
            allow_redirects=True,
            timeout=timeout,
        )
        return response.status_code < 400
    except requests.RequestException:
        return False


def hands_on_exists(hands_on: str, timeout: int = 5) -> bool:
    if hands_on.startswith("hp-"):
        hands_on = hands_on[3:]

    try:
        response = requests.head(
            get_gitmastery_file_path(f"hands_on/{hands_on.replace('-', '_')}.py"),
            allow_redirects=True,
            timeout=timeout,
        )
        return response.status_code < 400
    except requests.RequestException:
        return False


# We hardcode this list because to fetch it dynamically requires a Github API call
# which we only have 60/hour so it's unwise to do it
# TODO(woojiahao): Find a better way around this
EXERCISE_UTILS_FILES = ["__init__", "cli", "git", "file", "gitmastery", "github_cli"]


def execute_py_file_function_from_url(
    exercise: str, file_path: str, function_name: str, params: Dict[str, Any]
) -> Optional[Any]:
    sys.dont_write_bytecode = True
    py_file = fetch_file_contents(
        get_gitmastery_file_path(f"{exercise}/{file_path}"), False
    )
    namespace: Dict[str, Any] = {}

    with tempfile.TemporaryDirectory() as tmpdir:
        package_root = os.path.join(tmpdir, "exercise_utils")
        os.makedirs(package_root, exist_ok=True)

        for filename in EXERCISE_UTILS_FILES:
            exercise_utils_path = get_gitmastery_file_path(
                f"exercise_utils/{filename}.py"
            )
            exercise_utils_src = fetch_file_contents(exercise_utils_path, False)
            with open(f"{package_root}/{filename}.py", "w", encoding="utf-8") as f:
                f.write(ensure_str(exercise_utils_src))

        sys.path.insert(0, tmpdir)
        try:
            exec(py_file, namespace)
            if function_name not in namespace:
                sys.dont_write_bytecode = False
                return None

            result = namespace[function_name](**params)
            sys.dont_write_bytecode = False
            return result
        except Exception as e:
            error(str(e))
            return None
        finally:
            sys.path.remove(tmpdir)


def load_namespace_with_exercise_utils(file_path: str) -> Dict[str, Any]:
    sys.dont_write_bytecode = True
    py_file = fetch_file_contents(get_gitmastery_file_path(file_path), False)
    namespace: Dict[str, Any] = {}

    with tempfile.TemporaryDirectory() as tmpdir:
        package_root = os.path.join(tmpdir, "exercise_utils")
        os.makedirs(package_root, exist_ok=True)

        for filename in EXERCISE_UTILS_FILES:
            exercise_utils_path = get_gitmastery_file_path(
                f"exercise_utils/{filename}.py"
            )
            exercise_utils_src = fetch_file_contents(exercise_utils_path, False)
            with open(f"{package_root}/{filename}.py", "w", encoding="utf-8") as f:
                f.write(ensure_str(exercise_utils_src))

        sys.path.insert(0, tmpdir)
        try:
            exec(py_file, namespace)
        finally:
            sys.path.remove(tmpdir)

    sys.dont_write_bytecode = False
    return namespace
