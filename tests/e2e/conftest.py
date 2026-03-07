from collections.abc import Generator
from pathlib import Path

import pytest

from .constants import EXERCISE_NAME
from .utils import rmtree
from .runner import BinaryRunner


@pytest.fixture(scope="session")
def runner() -> BinaryRunner:
    """
    BinaryRunner pointed at the gitmastery binary.
    """
    return BinaryRunner.from_env()


@pytest.fixture
def gitmastery_root(
    runner: BinaryRunner, tmp_path_factory: pytest.TempPathFactory
) -> Generator[Path, None, None]:
    """
    Run `setup` in a pytest base temp dir, yield the exercises path.
    """
    work_dir = tmp_path_factory.mktemp("gitmastery-e2e-test-tmp")
    res = runner.run(["setup"], cwd=work_dir, stdin_text="\n") # setup with default options
    res.assert_success()

    exercises_path = work_dir / "gitmastery-exercises"
    assert exercises_path.is_dir()
    
    try:
        yield exercises_path
    finally:
        rmtree(work_dir)


@pytest.fixture
def downloaded_exercise_dir(runner: BinaryRunner, gitmastery_root: Path) -> Path:
    """
    Run `download EXERCISE_NAME`, return the exercise dir.
    """
    res = runner.run(["download", EXERCISE_NAME], cwd=gitmastery_root)
    res.assert_success()
    return gitmastery_root / EXERCISE_NAME


@pytest.fixture
def verified_exercise_dir(runner: BinaryRunner, downloaded_exercise_dir: Path) -> Path:
    """
    Run `verify` on the downloaded exercise, return the exercise dir.
    """
    res = runner.run(["verify"], cwd=downloaded_exercise_dir)
    res.assert_success()
    return downloaded_exercise_dir
