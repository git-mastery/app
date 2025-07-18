from dataclasses import dataclass


@dataclass
class Version:
    major: int
    minor: int
    patch: int

    @staticmethod
    def parse_version_string(version: str) -> "Version":
        only_version = version[1:]
        [major, minor, patch] = only_version.split(".")
        return Version(int(major), int(minor), int(patch))

    def is_behind(self, other: "Version") -> bool:
        """Returns if the current version is behind the other version based on major and minor versions."""
        return (other.major, other.minor) > (self.major, self.minor)

    def __repr__(self) -> str:
        return f"v{self.major}.{self.minor}.{self.patch}"
