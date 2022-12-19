from __future__ import annotations

import dataclasses
from typing import Any


@dataclasses.dataclass
class SAMLNameID:
    value: str
    format: str | None = None

    @classmethod
    def from_xml_value(cls, val: str | dict[str, Any]) -> SAMLNameID:
        if isinstance(val, str):
            return cls(value=val)
        return cls(value=val["#text"], format=val.get("@Format"))

    def __eq__(self, other):
        if isinstance(other, str):
            return self.value == other
        return super().__eq__(other)
