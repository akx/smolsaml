from __future__ import annotations

import dataclasses
from typing import Any

from smolsaml.models.utils import listify, only_one_or_raise, tagify_bare_text


@dataclasses.dataclass
class SAMLAttribute:
    name: str
    name_format: str | None
    values: list[Any]
    types: list[str | None]

    @classmethod
    def from_xml_value(cls, attr_dict: dict) -> SAMLAttribute:
        value_tags = [
            tagify_bare_text(v) for v in listify(attr_dict.pop("saml:AttributeValue"))
        ]
        values = [v.pop("#text") for v in value_tags]
        types = [v.pop("@xsi:type", None) for v in value_tags]
        return cls(
            name=attr_dict.pop("@Name"),
            name_format=attr_dict.pop("@NameFormat", None),
            values=values,
            types=types,
        )

    @property
    def value(self) -> Any:
        return only_one_or_raise(self.values, "Attribute has multiple values")

    @property
    def type(self) -> str | None:
        return only_one_or_raise(self.types, "Attribute has multiple types")
