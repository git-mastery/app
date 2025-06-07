import importlib.util
import json
import sys
import urllib.parse
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

import click
import requests

from cli.utils.click_utils import error

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


def read_gitmastery_config(gitmastery_config_path: Path) -> Dict:
    return read_config(gitmastery_config_path, GITMASTERY_CONFIG_NAME)


def find_gitmastery_exercise_root() -> Optional[Tuple[Path, int]]:
    return find_root(GITMASTERY_EXERCISE_CONFIG_NAME)


def read_gitmastery_exercise_config(gitmastery_exercise_config_path: Path) -> Dict:
    return read_config(gitmastery_exercise_config_path, GITMASTERY_EXERCISE_CONFIG_NAME)


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
