from typing import List, Optional

from app.utils.click import get_tag_cache, get_verbose
from app.utils.command import run
from app.utils.version import Version


def get_exercises_tags() -> List[str]:
    tag_cache = get_tag_cache()
    if len(tag_cache) != 0:
        if get_verbose():
            print("Fetching tags from cache")
        # Use the in-memory, per command cache for tags to avoid re-querying
        return tag_cache

    result = run(
        [
            "git",
            "ls-remote",
            "--tags",
            "--refs",
            "https://github.com/git-mastery/exercises",
        ]
    )
    versions = []
    if result.is_success() and result.stdout:
        lines = result.stdout.split("\n")
        for line in lines:
            tag_raw = line.split()[1]
            if tag_raw.startswith("refs/tags/"):
                tag = tag_raw[len("refs/tags/") :]
                versions.append(tag)
    tag_cache = versions
    if get_verbose():
        print("Queried for tags to store in cache")
    return versions


def get_all_exercise_tags() -> List[Version]:
    tags = get_exercises_tags()
    return list(sorted([Version.parse_version_string(t) for t in tags], reverse=True))


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
