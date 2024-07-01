from __future__ import annotations

import dataclasses
import warnings
from typing import Any

from smolsaml.models.utils import listify, tagify_bare_text


@dataclasses.dataclass
class SAMLStatus:
    code: str
    message: str | None = None
    detail: Any = None
    secondary_codes: list[str] = dataclasses.field(default_factory=list)

    def __eq__(self, other) -> bool:
        # Legacy compatibility: allow comparison with code strings.
        if isinstance(other, str):
            return self.code == other
        if isinstance(other, SAMLStatus):
            return dataclasses.asdict(self) == dataclasses.asdict(other)
        return super().__eq__(other)

    def __str__(self) -> str:
        s = self.code
        if self.secondary_codes:
            s += f" ({', '.join(self.secondary_codes)})"
        if self.message:
            s += f": {self.message}"
        return s

    @classmethod
    def from_xml_value(cls, param: dict) -> SAMLStatus:
        if not isinstance(param, dict):
            raise ValueError(f"Cannot parse status: {param!r}")
        code = message = detail = None
        secondary_codes: list[str] = []
        if "samlp:StatusCode" in param:
            status_code_el = param["samlp:StatusCode"]
            code = status_code_el["@Value"]
            # "The <StatusCode> element MAY contain subordinate second-level <StatusCode>
            #  elements that provide additional information on the error condition."
            if "samlp:StatusCode" in status_code_el:
                secondary_codes.extend(
                    el["@Value"] for el in listify(status_code_el["samlp:StatusCode"])
                )
        if "samlp:StatusMessage" in param:
            message_el = param["samlp:StatusMessage"]
            if message_el:  # An empty element is parsed as None
                message = tagify_bare_text(message_el).get("#text")
        if "samlp:StatusDetail" in param:
            # "The additional information consists of zero or more elements from any namespace,
            #  with no requirement for a schema to be present or for schema validation of the
            #  <StatusDetail> contents."
            # IOW, we don't know what to expect here, so just store it as-is.
            detail = param["samlp:StatusDetail"]
        if not code:
            raise ValueError(f"Cannot parse status (no StatusCode): {param!r}")
        return cls(
            code=code,
            message=message,
            detail=detail,
            secondary_codes=secondary_codes,
        )


def parse_saml_status(param: Any) -> str:
    warnings.warn(
        "parse_saml_status is deprecated, use SAMLStatus.from_xml_value instead",
        DeprecationWarning,
    )
    if isinstance(param, str):
        return param
    return SAMLStatus.from_xml_value(param).code
