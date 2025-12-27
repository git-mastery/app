import os


def generate_cds_string(cds: int) -> str:
    return os.sep.join([".."] * cds)
