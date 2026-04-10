from dataclasses import dataclass
from typing import Optional


@dataclass
class Version:
    major: int
    minor: int
    patch: int
    prerelease: Optional[int]

    @staticmethod
    def parse_version_string(version: str) -> "Version":
        """Parse a version string with 'v' prefix (e.g., 'v1.2.3')."""
        only_version = version[1:]
        if "beta" in only_version:
            [major, minor, patch, prerelease] = [part[0] for part in only_version.split(".")]
            return Version(int(major), int(minor), int(patch), int(prerelease))
        [major, minor, patch] = only_version.split(".")
        return Version(int(major), int(minor), int(patch), None)

    @staticmethod
    def parse(version: str) -> "Version":
        """Parse a plain version string (e.g., '1.2.3')."""
        parts = version.split(".")
        if ("beta" in version and len(parts) != 4) or len(parts) != 3:
            raise ValueError(
                f"Invalid version string (expected 'MAJOR.MINOR.PATCH[-beta.PRERELEASE]'): {version!r}"
            )
        try:
            if len(parts) == 4:
                major, minor, patch, prerelease = (int(part[0]) for part in parts)
            else:
                major, minor, patch = (int(part) for part in parts)
                prerelease = None
        except ValueError as exc:
            raise ValueError(
                f"Invalid numeric components in version string: {version!r}"
            ) from exc
        return Version(major, minor, patch, prerelease)

    def is_behind(self, other: "Version") -> bool:
        """Returns if the current version is behind the other version based on major and minor versions."""
        if self.prerelease and other.prerelease:
            return (other.major, other.minor, other.prerelease) > (self.major, self.minor, self.prerelease)
        return (other.major, other.minor) > (self.major, self.minor)

    def __repr__(self) -> str:
        if self.prerelease:
            return f"v{self.major}.{self.minor}.{self.patch}-beta.{self.prerelease}"
        return f"v{self.major}.{self.minor}.{self.patch}"
