from typing import List
from unittest import mock

import pytest
from app.utils.exercises import (
    get_latest_exercise_version_within_pin,
    get_latest_release_exercise_version,
)
from app.utils.version import Version


def test_get_latest_release_exercise_version():
    exercises = [
        "0.0.1-beta.0",
        "0.9.9",
        "v1.0.0",
        "1.1.1",
        "12.1.1-beta.1",
        "12.1.1-beta.4",
    ]
    with mock.patch(
        "app.utils.version.get_all_exercise_tags", return_value=_get_versions(exercises)
    ):
        assert get_latest_release_exercise_version() == Version(
            0, 9, 9, None, None, False, False, False
        )


@pytest.mark.parametrize(
    "pin,expected",
    [
        ("^1.1.0", Version(1, 1, 1, None, None, False, False, False)),
        ("^12.0.0", None),
    ],
)
def test_get_latest_exercise_version_within_pin(pin, expected):
    exercises = [
        "0.0.1-beta.0",
        "0.9.9",
        "v1.0.0",
        "1.1.1",
        "12.1.1-beta.1",
        "12.1.1-beta.4",
    ]
    with mock.patch(
        "app.utils.version.get_all_exercise_tags",
        return_value=_get_versions(exercises),
    ):
        version = get_latest_exercise_version_within_pin(
            Version.parse_version_string(pin)
        )
        assert version == expected


def _get_versions(version_strings: List[str]) -> List[Version]:
    return [Version.parse_version_string(v) for v in version_strings]
