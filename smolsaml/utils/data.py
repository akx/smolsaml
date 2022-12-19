from __future__ import annotations


def compact_dict(dct: dict[str, str | None]) -> dict[str, str]:
    return {key: value for (key, value) in dct.items() if value is not None}
