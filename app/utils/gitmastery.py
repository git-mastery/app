import json
import os
import sys
import tempfile
from dataclasses import asdict
from pathlib import Path
from typing import (
    Any,
    Dict,
    Optional,
    Self,
    Tuple,
    Type,
    TypeVar,
    Union,
)

import click
from git import Repo

from app.exercise_config import ExerciseConfig
from app.gitmastery_config import GIT_MASTERY_EXERCISES_SOURCE, GitMasteryConfig
from app.utils.click import (
    error,
    get_exercise_root_config,
    get_gitmastery_root_config,
    info,
)
from app.utils.general import ensure_str

GITMASTERY_CONFIG_NAME = ".gitmastery.json"
GITMASTERY_EXERCISE_CONFIG_NAME = ".gitmastery-exercise.json"


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
        contents = f.read()
        if contents.strip() == "":
            return {}
        return json.loads(contents)


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

    exercises_source_raw = raw_config.get("exercises_source", {})
    return GitMasteryConfig(
        path=gitmastery_config_path,
        cds=cds,
        progress_local=raw_config.get("progress_local", True),
        progress_remote=raw_config.get("progress_remote", False),
        exercises_source=GitMasteryConfig.ExercisesSource(
            username=exercises_source_raw.get("username", "git-mastery"),
            repository=exercises_source_raw.get("repository", "exercises"),
            branch=exercises_source_raw.get("branch", "main"),
        ),
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


T = TypeVar("T")


# We hardcode this list because to fetch it dynamically requires a Github API call
# which we only have 60/hour so it's unwise to do it
# TODO(woojiahao): Find a better way around this
EXERCISE_UTILS_FILES = ["__init__", "cli", "git", "file", "gitmastery", "github_cli"]


class ExercisesRepo:
    def __init__(self) -> None:
        """Creates a sparse clone of the exercises repository.

        Used to minimize Github API calls to the raw. domain as sparse clones will use
        the regular Git server calls which are not a part of the Github API calls.
        These greatly reduce the rate in which the Git-Mastery app will hit the Github
        API rate limit.
        """

        self.__repo: Optional[Repo] = None
        self.__temp_dir: Optional[tempfile.TemporaryDirectory] = None

    @property
    def repo(self) -> Repo:
        assert self.__repo is not None
        return self.__repo

    def checkout(self, file_path: Union[str, Path]) -> None:
        self.repo.git.sparse_checkout("set", "--skip-checks", file_path)

    def has_file(self, file_path: Union[str, Path]) -> bool:
        self.checkout(file_path)
        return os.path.exists(Path(self.repo.working_dir) / file_path)

    def fetch_file_contents(
        self, file_path: Union[str, Path], is_binary: bool
    ) -> str | bytes:
        self.checkout(file_path)
        read_mode = "rb" if is_binary else "rt"
        with open(Path(self.repo.working_dir) / file_path, read_mode) as file:
            return file.read()

    def download_file(
        self,
        file_path: Union[str, Path],
        download_to_path: Union[str, Path],
        is_binary: bool,
    ) -> None:
        contents = self.fetch_file_contents(file_path, is_binary)
        if is_binary:
            assert isinstance(contents, bytes)
            with open(download_to_path, "wb") as file:
                file.write(contents)
        else:
            assert isinstance(contents, str)
            with open(download_to_path, "w+") as file:
                file.write(contents)

    def __enter__(self) -> Self:
        self.__temp_dir = tempfile.TemporaryDirectory()

        gitmastery_config = get_gitmastery_root_config()
        if gitmastery_config is not None:
            exercises_source = gitmastery_config.exercises_source
        else:
            exercises_source = GIT_MASTERY_EXERCISES_SOURCE

        info(
            f"Fetching exercise information from {exercises_source.to_url()} on branch {exercises_source.branch}"
        )

        self.__repo = Repo.clone_from(
            exercises_source.to_url(),
            self.__temp_dir.name,
            depth=1,
            branch=exercises_source.branch,
            multi_options=["--filter=blob:none", "--sparse"],
        )
        return self

    def __exit__(
        self,
        exc_type: type | None,
        exc_val: BaseException | None,
        exc_tb: object | None,
    ) -> None:
        if self.__temp_dir is not None:
            self.__temp_dir.cleanup()


class Namespace:
    def __init__(self, namespace: Dict[str, Any]) -> None:
        self.namespace = namespace

    @classmethod
    def load_file_as_namespace(
        cls: Type[Self], exercises_repo: ExercisesRepo, file_path: Union[str, Path]
    ) -> Self:
        sys.dont_write_bytecode = True
        py_file = exercises_repo.fetch_file_contents(file_path, False)
        namespace: Dict[str, Any] = {}

        with tempfile.TemporaryDirectory() as tmpdir:
            package_root = os.path.join(tmpdir, "exercise_utils")
            os.makedirs(package_root, exist_ok=True)

            for filename in EXERCISE_UTILS_FILES:
                exercise_utils_src = exercises_repo.fetch_file_contents(
                    f"exercise_utils/{filename}.py", False
                )
                with open(f"{package_root}/{filename}.py", "w", encoding="utf-8") as f:
                    f.write(ensure_str(exercise_utils_src))

            sys.path.insert(0, tmpdir)
            try:
                exec(py_file, namespace)
            finally:
                sys.path.remove(tmpdir)

        sys.dont_write_bytecode = False
        return cls(namespace)

    def execute_function(
        self, function_name: str, params: Dict[str, Any]
    ) -> Optional[Any]:
        if function_name not in self.namespace:
            sys.dont_write_bytecode = False
            return None

        result = self.namespace[function_name](**params)
        sys.dont_write_bytecode = False
        return result

    def get_variable(
        self,
        variable_name: str,
        default_value: Optional[T] = None,
    ) -> Optional[T]:
        variable = self.namespace.get(variable_name, default_value)
        return variable
