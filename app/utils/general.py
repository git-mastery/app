from typing import Union


def ensure_str(val: Union[str, bytes]) -> str:
    if isinstance(val, bytes):
        return val.decode("utf-8", errors="replace").strip()
    return str(val).strip()
