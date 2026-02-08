import pytest

from .runner import BinaryRunner


@pytest.fixture(scope="session")
def runner() -> BinaryRunner:
    return BinaryRunner.from_env()
