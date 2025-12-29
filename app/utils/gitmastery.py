import inspect
import os
import sys
import tempfile
from pathlib import Path
from typing import (
    Any,
    Dict,
    Optional,
    Self,
    Type,
    TypeVar,
    Union,
)

from git import Repo

from app.configs.gitmastery_config import GIT_MASTERY_EXERCISES_SOURCE
from app.utils.click import get_gitmastery_root_config, info
from app.utils.general import ensure_str

T = TypeVar("T")


EXERCISE_UTILS_FILES = [
    "__init__",
    "cli",
    "git",
    "file",
    "gitmastery",
    "github_cli",
    "test",
]


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

        func = self.namespace[function_name]
        sig = inspect.signature(func)
        valid_params = {k: v for k, v in params.items() if k in sig.parameters}
        result = self.namespace[function_name](**valid_params)
        sys.dont_write_bytecode = False
        return result

    def get_variable(
        self,
        variable_name: str,
        default_value: Optional[T] = None,
    ) -> Optional[T]:
        variable = self.namespace.get(variable_name, default_value)
        return variable
