from dataclasses import dataclass


@dataclass
class Version:
    major: int
    minor: int
    patch: int

    @staticmethod
    def parse_version_string(version: str) -> "Version":
        """Parse a version string with 'v' prefix (e.g., 'v1.2.3')."""
        only_version = version[1:]
        [major, minor, patch] = only_version.split(".")
        return Version(int(major), int(minor), int(patch))

    @staticmethod
    def parse(version: str) -> "Version":
        """Parse a plain version string (e.g., '1.2.3')."""
        parts = version.split(".")
        if len(parts) != 3:
            raise ValueError(
                f"Invalid version string (expected 'MAJOR.MINOR.PATCH'): {version!r}"
            )
        try:
            major, minor, patch = (int(part) for part in parts)
        except ValueError as exc:
            raise ValueError(
                f"Invalid numeric components in version string: {version!r}"
            ) from exc
        return Version(major, minor, patch)

    def is_behind(self, other: "Version") -> bool:
        """Returns if the current version is behind the other version based on major and minor versions."""
        return (other.major, other.minor) > (self.major, self.minor)

    def __repr__(self) -> str:
        return f"v{self.major}.{self.minor}.{self.patch}"
