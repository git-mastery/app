from collections.abc import Generator
from pathlib import Path

import pytest

from .constants import EXERCISE_NAME, HANDS_ON_NAME
from .utils import rmtree
from .runner import BinaryRunner
from .result import RunResult


@pytest.fixture(scope="session")
def runner() -> BinaryRunner:
    """
    BinaryRunner pointed at the gitmastery binary.
    """
    return BinaryRunner.from_env()


def _make_gitmastery_root(
    runner: BinaryRunner, tmp_path_factory: pytest.TempPathFactory
) -> Generator[Path, None, None]:
    work_dir = tmp_path_factory.mktemp("gitmastery-e2e-test-tmp")

    res = runner.run(["setup"], cwd=work_dir, stdin_text="\n")
    res.assert_success()

    gitmastery_root_folder = work_dir / "gitmastery-exercises"
    assert gitmastery_root_folder.is_dir()

    try:
        yield gitmastery_root_folder
    finally:
        rmtree(work_dir)


@pytest.fixture(scope="session")
def gitmastery_root(
    runner: BinaryRunner, tmp_path_factory: pytest.TempPathFactory
) -> Generator[Path, None, None]:
    """
    Run `setup` once per session, yield the exercises path.
    """
    yield from _make_gitmastery_root(runner, tmp_path_factory)


@pytest.fixture
def setup_gitmastery_root(
    runner: BinaryRunner, tmp_path_factory: pytest.TempPathFactory
) -> Generator[Path, None, None]:
    """
    For use by test_setup only, which must inspect pristine initial state.
    """
    yield from _make_gitmastery_root(runner, tmp_path_factory)


@pytest.fixture(scope="session")
def downloaded_exercise_dir(runner: BinaryRunner, gitmastery_root: Path) -> Path:
    """
    Run `download EXERCISE_NAME` once per session, return the exercise dir.
    """
    res = runner.run(["download", EXERCISE_NAME], cwd=gitmastery_root)
    res.assert_success()
    exercise_dir = gitmastery_root / EXERCISE_NAME
    return exercise_dir


@pytest.fixture(scope="session")
def downloaded_hands_on_dir(runner: BinaryRunner, gitmastery_root: Path) -> Path:
    """
    Run `download HANDS_ON_NAME` once per session, return the hands-on dir.
    """
    res = runner.run(["download", HANDS_ON_NAME], cwd=gitmastery_root)
    res.assert_success()
    return gitmastery_root / HANDS_ON_NAME


@pytest.fixture(scope="session")
def verified_exercise_dir(runner: BinaryRunner, downloaded_exercise_dir: Path) -> Path:
    """
    Run `verify` on the downloaded exercise once per session, return the exercise dir.
    """
    res = runner.run(["verify"], cwd=downloaded_exercise_dir)
    res.assert_success()
    return downloaded_exercise_dir


@pytest.fixture(scope="session")
def check_results(runner: BinaryRunner) -> RunResult:
    """version + check git/github — no setup required."""
    return runner.run_repl_session([
        (["version"], None),
        (["check", "git"], None),
        (["check", "github"], None),
    ])


@pytest.fixture(scope="session")
def progress_results(runner: BinaryRunner, gitmastery_root: Path) -> RunResult:
    """progress show + sync commands — requires gitmastery_root setup."""
    return runner.run_repl_session(
        [
            (["progress", "show"], None),
            (["progress", "sync", "on"], None),
            (["progress", "sync", "off"], "y\n"),
        ],
        cwd=gitmastery_root,
    )


@pytest.fixture(scope="session")
def reset_results(runner: BinaryRunner, verified_exercise_dir: Path) -> RunResult:
    """progress reset — requires verified exercise."""
    return runner.run_repl_session(
        [(["progress", "reset"], None)],
        cwd=verified_exercise_dir,
    )
