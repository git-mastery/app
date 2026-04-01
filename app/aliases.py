COMMAND_ALIASES: dict[str, list[str]] = {
    "download": ["d"],
    "verify": ["v"],
    "setup": ["s"],
    "check": ["c"],
    "progress": ["p"],
    "version": ["ver"],
}


def resolve_alias(name: str) -> str:
    """Resolve an alias to its full command name, or return the name unchanged."""
    for command, aliases in COMMAND_ALIASES.items():
        if name in aliases:
            return command
    return name
