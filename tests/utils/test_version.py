import pytest
from app.utils.version import Version


def test_parse_version_string_pinned_with_build():
    with pytest.raises(
        ValueError,
        match="Version pinning is not supported for version strings with a build string",
    ):
        Version.parse_version_string("^1.0.0-X+build")


@pytest.mark.parametrize(
    "s, expected",
    [
        ("v^1.0.0", Version(1, 0, 0, None, None, True, False, False)),
        ("^1.0.0", Version(1, 0, 0, None, None, True, False, False)),
        ("v^1.12.0-beta.1", Version(1, 12, 0, "beta.1", None, True, False, False)),
        ("^1.12.0-beta.2", Version(1, 12, 0, "beta.2", None, True, False, False)),
        (
            "1.12.0-beta.2+build.12",
            Version(1, 12, 0, "beta.2", "build.12", False, False, False),
        ),
        ("1.12.0-beta.2", Version(1, 12, 0, "beta.2", None, False, False, False)),
        ("1.12.0", Version(1, 12, 0, None, None, False, False, False)),
        ("release", Version.RELEASE),
        ("development", Version.DEVELOPMENT),
    ],
)
def test_parse_version_string_regular(s, expected):
    v = Version.parse_version_string(s)
    assert v == expected


@pytest.mark.parametrize(
    "left,right",
    [
        ("release", "release"),
        ("release", "1.0.0"),
    ],
)
def test_version_lt_release(left, right):
    assert not Version.parse_version_string(left) < Version.parse_version_string(right)


@pytest.mark.parametrize(
    "left,right",
    [
        ("development", "release"),
        ("development", "1.0.0"),
    ],
)
def test_version_lt_development(left, right):
    assert not Version.parse_version_string(left) < Version.parse_version_string(right)


@pytest.mark.parametrize(
    "left,right",
    [
        ("v1.0.0", "v1.1.1"),
        ("v1.0.0", "v1.0.1"),
        ("v1.0.0", "v2.0.0"),
        ("1.0.0", "release"),
        ("1.0.0", "development"),
        ("1.1.0-beta.0", "1.1.0-beta.1"),
        ("1.1.0-beta.0+build", "1.1.0-beta.1+a"),
    ],
)
def test_version_lt_regular(left, right):
    assert Version.parse_version_string(left) < Version.parse_version_string(right)


def test_version_eq_different_type():
    assert not (Version.parse_version_string("1.0.0") == 1)


@pytest.mark.parametrize(
    "left,right,expected",
    [
        ("release", "release", True),
        ("development", "development", True),
        ("release", "development", False),
        ("development", "release", False),
        ("development", "v1.1.1", False),
    ],
)
def test_version_lt_track(left, right, expected):
    assert (
        Version.parse_version_string(left) == Version.parse_version_string(right)
    ) == expected


def test_version_sort():
    version_strings = [
        "v1.0.0",
        "12.1.1-beta.4",
        "1.1.1",
        "12.1.1-beta.1",
        "0.9.9",
    ]

    versions = [Version.parse_version_string(v) for v in version_strings]
    versions.sort()

    expected_version_strings = [
        "0.9.9",
        "v1.0.0",
        "1.1.1",
        "12.1.1-beta.1",
        "12.1.1-beta.4",
    ]
    assert versions == [
        Version.parse_version_string(v) for v in expected_version_strings
    ]


@pytest.mark.parametrize(
    "version,expected",
    [
        ("1.0.0", False),
        ("1.11.2", True),
        ("1.12.0", True),
        ("1.11.2-beta.1", False),
        ("2.0.0", False),
    ],
)
def test_within_pin_without_prerelease(version, expected):
    pin_version = Version.parse_version_string("^1.11.1")
    version_v = Version.parse_version_string(version)
    assert version_v.within_pin(pin_version) == expected


@pytest.mark.parametrize(
    "version,expected",
    [
        ("1.0.0", False),
        ("1.11.2", True),
        ("1.12.0", True),
        ("1.11.2-beta.2", True),
        ("1.11.2-beta.0", True),
        ("2.0.0", False),
    ],
)
def test_within_pin_with_prerelease(version, expected):
    pin_version = Version.parse_version_string("^1.11.1-beta.1")
    version_v = Version.parse_version_string(version)
    assert version_v.within_pin(pin_version) == expected
