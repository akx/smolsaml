from __future__ import annotations

import dataclasses
import warnings
from typing import Any

from smolsaml.models.saml_name_id import SAMLNameID


@dataclasses.dataclass
class SAMLSubject:
    name_id: SAMLNameID | None = None
    raw_subject_confirmation: dict[str, None] | None = None

    @classmethod
    def from_xml_value(cls, val: Any) -> SAMLSubject:
        if not isinstance(val, dict):
            raise ValueError("Subject must be a dict")
        # Destructively parses `val`
        name_id = None
        if "saml:NameID" in val:
            name_id = SAMLNameID.from_xml_value(val.pop("saml:NameID"))
        raw_subject_confirmation = val.pop("saml:SubjectConfirmation", None)
        if val:
            warnings.warn(f"Unparsed subject elements: {val}")
        return cls(name_id=name_id, raw_subject_confirmation=raw_subject_confirmation)
