from dataclasses import dataclass
from typing import Self, Type

import semver  # type: ignore


@dataclass
class Version:
    major: int
    minor: int
    patch: int
    prerelease: str
    build: str

    pinned: bool

    @classmethod
    def parse_version_string(cls: Type[Self], version: str) -> Self:
        if version.startswith("v"):
            version = version[1:]
        pinned = False
        if version.startswith("^"):
            pinned = True
            version = version[1:]
        semver_version = semver.Version.parse(version)
        return cls(
            major=semver_version.major,
            minor=semver_version.minor,
            patch=semver_version.patch,
            prerelease=semver_version.prerelease,
            build=semver_version.build,
            pinned=pinned,
        )

    def __lt__(self, other: Self) -> bool:
        self_version = self.__to_semver_version__(self)
        other_version = self.__to_semver_version__(other)
        return self_version < other_version

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, type(self)):
            return False

        self_version = self.__to_semver_version__(self)
        other_version = self.__to_semver_version__(other)
        return self_version == other_version

    def is_behind(self, other: "Version") -> bool:
        """Returns if the current version is behind the other version based on major and minor versions."""
        return (other.major, other.minor) > (self.major, self.minor)

    def to_version_string(self) -> str:
        version = self.__to_semver_version__(self)
        if self.pinned:
            return "^" + str(version)
        return str(version)

    def __to_semver_version__(self, version: Self) -> semver.Version:
        parts = (self.major, self.minor, self.patch, self.prerelease, self.build)
        version = semver.VersionInfo(*parts)
        return version

    def __repr__(self) -> str:
        return f"v{self.major}.{self.minor}.{self.patch}"
