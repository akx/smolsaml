from __future__ import annotations

from typing import Any


def listify(value):
    if isinstance(value, list):
        return value
    return [value]


def only_one_or_raise(value, message):
    if len(value) != 1:
        raise ValueError(message)
    return value[0]


def tagify_bare_text(v: str | dict[str, Any]) -> dict[str, Any]:
    if isinstance(v, str):
        return {"#text": v}
    return v
