from collections.abc import Generator
from pathlib import Path

import pytest

from .utils import rmtree
from .runner import BinaryRunner


@pytest.fixture(scope="session")
def runner() -> BinaryRunner:
    """
    Return a BinaryRunner instance for the gitmastery binary.
    """
    return BinaryRunner.from_env()


@pytest.fixture(scope="session")
def exercises_dir(
    runner: BinaryRunner, tmp_path_factory: pytest.TempPathFactory
) -> Generator[Path, None, None]:
    """
    Run setup once and return the path to the exercises directory.
    Tears down by deleting the entire working directory after all tests complete.
    """
    work_dir = tmp_path_factory.mktemp("e2e-tests-tmp")

    # Send newline to accept the default directory name prompt
    res = runner.run(["setup"], cwd=work_dir, stdin_text="\n")
    assert res.returncode == 0, (
        f"Setup failed with exit code {res.returncode}\n"
        f"stdout:\n{res.stdout}\nstderr:\n{res.stderr}"
    )

    exercises_path = work_dir / "gitmastery-exercises"
    assert exercises_path.is_dir(), (
        f"Expected directory {exercises_path} to exist after setup"
    )

    try:
        yield exercises_path
    finally:
        rmtree(work_dir)  # ensure cleanup even if tests fail
