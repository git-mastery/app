from dataclasses import dataclass
from typing import ClassVar, List, Optional, Self, Type

import requests
import semver  # type: ignore


@dataclass
class Version:
    major: int
    minor: int
    patch: int
    prerelease: Optional[str]
    build: Optional[str]

    pinned: bool
    release: bool
    development: bool

    RELEASE: ClassVar[Self]
    DEVELOPMENT: ClassVar[Self]

    @classmethod
    def parse_version_string(cls: Type[Self], version: str) -> Self:
        if version == "release":
            return cls.RELEASE

        if version == "development":
            return cls.DEVELOPMENT

        if version.startswith("v"):
            version = version[1:]
        pinned = False
        if version.startswith("^"):
            pinned = True
            version = version[1:]
        semver_version = semver.Version.parse(version)

        if pinned and semver_version.build is not None:
            raise ValueError(
                "Version pinning is not supported for version strings with a build string"
            )

        return cls(
            major=semver_version.major,
            minor=semver_version.minor,
            patch=semver_version.patch,
            prerelease=semver_version.prerelease,
            build=semver_version.build,
            pinned=pinned,
            release=False,
            development=False,
        )

    def __lt__(self, other: Self) -> bool:
        if self.release or self.development:
            # The release or development versions will always never be less than
            # anything else
            # There is a caveat in the logic where the release may be < development,
            # but this is unlikely to occur
            return False
        if other.release or other.development:
            # If the other is release or development, whatever this is - assuming not
            # release or development - will always be behind
            return True
        self_version = self.__to_semver_version__(self)
        other_version = self.__to_semver_version__(other)

        # This comparison will also use the prerelease version
        # Build is ignored
        return self_version < other_version

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, type(self)):
            return False

        if self.release:
            return self.release == other.release

        if self.development:
            return self.development == other.development

        self_version = self.__to_semver_version__(self)
        other_version = self.__to_semver_version__(other)

        # This comparison will also use the prerelease version
        # Build is ignored
        return self_version == other_version

    def is_behind(self, other: Self) -> bool:
        """Returns if the current version is behind the other version based on major and minor versions."""
        return (other.major, other.minor) > (self.major, self.minor)

    def to_version_string(self) -> str:
        if self.release:
            return "release"

        if self.development:
            return "development"

        version = self.__to_semver_version__(self)
        if self.pinned:
            return "^" + str(version)
        return str(version)

    def within_pin(self, pin_version: Self) -> bool:
        if not pin_version.pinned:
            raise ValueError("Version provided should be pinned")

        if pin_version.prerelease is None and self.prerelease is not None:
            # Not looking to check against prerelease versions, so ignore a prerelease
            # version
            return False

        min_bound = f">={pin_version.major}.{pin_version.minor}.{pin_version.patch}"
        max_bound = f"<{pin_version.major + 1}.0.0"
        self_version = self.__to_semver_version__(self)
        within_min_bound = self_version.match(min_bound)
        within_max_bound = self_version.match(max_bound)
        return within_min_bound and within_max_bound

    def __to_semver_version__(self, version: Self) -> semver.Version:
        parts = (
            version.major,
            version.minor,
            version.patch,
            version.prerelease,
            version.build,
        )
        v = semver.VersionInfo(*parts)
        return v

    def __repr__(self) -> str:
        if self.release:
            return "release"
        if self.development:
            return "development"

        return f"v{self.major}.{self.minor}.{self.patch}"


Version.RELEASE = Version(
    major=0,
    minor=0,
    patch=0,
    prerelease="",
    build="",
    pinned=False,
    release=True,
    development=False,
)

Version.DEVELOPMENT = Version(
    major=0,
    minor=0,
    patch=0,
    prerelease="",
    build="",
    pinned=False,
    release=False,
    development=True,
)


def get_all_exercise_tags() -> List[Version]:
    url = "https://api.github.com/repos/git-mastery/exercises/tags"
    tags = requests.get(url, timeout=10).json()
    return list(
        sorted(
            [Version.parse_version_string(t["name"].lstrip("v")) for t in tags],
            reverse=True,
        )
    )


def get_latest_release_exercise_version() -> Optional[Version]:
    all_tags = get_all_exercise_tags()
    if len(all_tags) == 0:
        # Although this should not be happening, we will let the callsite handle this
        return None

    # These should always ignore the development versions, just focus on the release
    # versions
    for tag in all_tags:
        if tag.prerelease is None:
            return tag

    return None


def get_latest_development_exercise_version() -> Optional[Version]:
    all_tags = get_all_exercise_tags()
    if len(all_tags) == 0:
        # Although this should not be happening, we will let the callsite handle this
        return None

    for tag in all_tags:
        if tag.build is None:
            return tag
    return None


def get_latest_exercise_version_within_pin(pin_version: Version) -> Optional[Version]:
    all_tags = get_all_exercise_tags()
    for tag in all_tags:
        if tag.within_pin(pin_version):
            return tag
    return None
