from typing import Optional, Union


def merge_dict(src: Optional[dict], dst: Union[dict, str]) -> dict:
    if src is None:
        src = {}

    out = dst.copy()

    for k, v in src.items():
        if isinstance(v, dict):
            v = merge_dict(v, dst.setdefault(k, {}))
        out[k] = v

    return out
