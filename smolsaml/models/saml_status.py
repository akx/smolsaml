from __future__ import annotations

from typing import Any


def parse_saml_status(param: Any) -> str:
    if isinstance(param, str):
        return param
    if isinstance(param, dict) and "samlp:StatusCode" in param:
        return parse_saml_status(param["samlp:StatusCode"]["@Value"])
    raise ValueError(f"Cannot parse status: {param!r}")
