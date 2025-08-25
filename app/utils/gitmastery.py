import importlib.util
import json
import sys
import urllib.parse
from pathlib import Path
from typing import Any, Dict, Optional, Tuple, TypeVar, Union

import click
import requests

from app.exercise_config import ExerciseConfig
from app.utils.click import error

GITMASTERY_CONFIG_NAME = ".gitmastery.json"
GITMASTERY_EXERCISE_CONFIG_NAME = ".gitmastery-exercise.json"
GITMASTERY_EXERCISES_BASE_URL = (
    "https://raw.githubusercontent.com/git-mastery/exercises/refs/heads/main/"
)


def find_root(filename: str) -> Optional[Tuple[Path, int]]:
    current = Path.cwd()
    steps = 0
    for parent in [current] + list(current.parents):
        if (parent / filename).is_file():
            return parent, steps
        steps += 1

    return None


def read_config(path: Path, filename: str) -> Dict:
    with open(path / filename, "r") as f:
        return json.loads(f.read())


def find_gitmastery_root() -> Optional[Tuple[Path, int]]:
    return find_root(GITMASTERY_CONFIG_NAME)


def require_gitmastery_root(requires_root: bool = False) -> Tuple[Path, Dict]:
    root = find_gitmastery_root()
    if root is None:
        error(
            f"You are not in a Git-Mastery exercise folder. Navigate to an appropriate folder or use {click.style('gitmastery setup', bold=True, italic=True)}"
        )

    # Just asserting since mypy doesn't recognize that error will exit the program
    assert root is not None
    root_path, cds = root

    if requires_root and cds != 0:
        error(
            f"Use {click.style('cd ' + generate_cds_string(cds), bold=True, italic=True)} to move to the root of the Git-Mastery exercises folder."
        )

    config = read_gitmastery_config(root_path)
    return root_path, config


def read_gitmastery_config(gitmastery_config_path: Path) -> Dict:
    return read_config(gitmastery_config_path, GITMASTERY_CONFIG_NAME)


def find_gitmastery_exercise_root() -> Optional[Tuple[Path, int]]:
    return find_root(GITMASTERY_EXERCISE_CONFIG_NAME)


def read_gitmastery_exercise_config(
    gitmastery_exercise_config_path: Path,
) -> ExerciseConfig:
    raw_config = read_config(
        gitmastery_exercise_config_path, GITMASTERY_EXERCISE_CONFIG_NAME
    )
    exercise_repo = raw_config["exercise_repo"]
    return ExerciseConfig(
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


def require_gitmastery_exercise_root(
    requires_root: bool = False,
) -> Tuple[Path, ExerciseConfig]:
    root = find_gitmastery_exercise_root()
    if root is None:
        error("You are not inside a Git-Mastery exercise folder.")

    assert root is not None
    root_path, cds = root

    config = read_gitmastery_exercise_config(root_path)

    if requires_root and cds != 0:
        exercise_name = config.exercise_name
        error(
            f"Use {click.style('cd ' + generate_cds_string(cds), bold=True, italic=True)} to move to the root of the {click.style(exercise_name, bold=True, italic=True)} exercise folder."
        )

    return root_path, config


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


def load_file_namespace(file_path: str) -> dict[str, Any]:
    sys.dont_write_bytecode = True
    py_file = fetch_file_contents(get_gitmastery_file_path(file_path), False)
    namespace: Dict[str, Any] = {}
    exec(py_file, namespace)
    sys.dont_write_bytecode = False
    return namespace


def get_variable_from_url(
    exercise: str,
    file_path: str,
    variable_name: str,
    default_value: Optional[T] = None,
) -> Optional[T]:
    sys.dont_write_bytecode = True
    py_file = fetch_file_contents(
        get_gitmastery_file_path(f"{exercise}/{file_path}"), False
    )
    namespace: Dict[str, Any] = {}
    exec(py_file, namespace)
    variable = namespace.get(variable_name, default_value)
    sys.dont_write_bytecode = False
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


def execute_py_file_function_from_url(
    exercise: str, file_path: str, function_name: str, params: Dict[str, Any]
) -> Optional[Any]:
    sys.dont_write_bytecode = True
    py_file = fetch_file_contents(
        get_gitmastery_file_path(f"{exercise}/{file_path}"), False
    )
    namespace: Dict[str, Any] = {}
    exec(py_file, namespace)
    if function_name not in namespace:
        return None
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
