from __future__ import annotations

import dataclasses
import datetime
import warnings
from collections import defaultdict
from typing import Any

from smolsaml.models.saml_attribute import SAMLAttribute
from smolsaml.models.saml_subject import SAMLSubject
from smolsaml.models.utils import listify
from smolsaml.utils.saml import from_saml_timestamp


@dataclasses.dataclass
class SAMLAssertion:
    id: str
    issue_instant: datetime.datetime
    issuer: str
    attributes: list[SAMLAttribute]
    subject: SAMLSubject | None
    raw_authn_statement: dict[str, Any]  # TODO: Parsing?
    raw_conditions: dict[str, Any]  # TODO: Parsing?
    raw_signature: Any

    @classmethod
    def from_xml_dict(cls, assertion_dict: dict[str, Any]) -> SAMLAssertion:
        # NB: destructively modifies assertion_dicts
        assert assertion_dict.pop("@Version") == "2.0"
        id = assertion_dict.pop("@ID")
        issue_instant = from_saml_timestamp(assertion_dict.pop("@IssueInstant"))
        issuer = assertion_dict.pop("saml:Issuer")
        attributes = [
            SAMLAttribute.from_xml_value(xd)
            for xd in listify(
                assertion_dict.pop("saml:AttributeStatement", {}).pop(
                    "saml:Attribute", []
                )
            )
        ]
        authn_statement = assertion_dict.pop("saml:AuthnStatement")
        conditions = assertion_dict.pop("saml:Conditions", {})
        raw_subject = assertion_dict.pop("saml:Subject", None)
        subject = SAMLSubject.from_xml_value(raw_subject) if raw_subject else None
        signature = assertion_dict.pop("ds:Signature", None)
        assertion_dict.pop("@xmlns", None)
        if assertion_dict:
            warnings.warn(f"Unparsed assertion elements: {assertion_dict}")
        return cls(
            id=id,
            issue_instant=issue_instant,
            issuer=issuer,
            attributes=attributes,
            subject=subject,
            raw_authn_statement=authn_statement,
            raw_conditions=conditions,
            raw_signature=signature,
        )

    def get_attribute_values(self) -> dict[str, list[Any]]:
        vd = defaultdict(list)
        for att in self.attributes:
            vd[att.name].extend(att.values)
        return dict(vd)
