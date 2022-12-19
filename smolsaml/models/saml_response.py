from __future__ import annotations

import dataclasses
import datetime
import warnings
from typing import Any

from smolsaml.consts import SAML_NAMEID_FORMAT_ENTITY
from smolsaml.models.saml_assertion import SAMLAssertion
from smolsaml.models.saml_name_id import SAMLNameID
from smolsaml.models.saml_status import parse_saml_status
from smolsaml.utils.saml import from_saml_timestamp
from smolsaml.utils.xml import parse_to_dict


@dataclasses.dataclass
class SAMLResponse:
    destination: str
    id: str
    in_response_to: str | None
    issue_instant: datetime.datetime
    assertion: SAMLAssertion
    issuer: SAMLNameID
    status: str
    raw_signature: Any

    @classmethod
    def from_xml(cls, xml: bytes) -> SAMLResponse:
        data = parse_to_dict(xml)
        response = data.pop("samlp:Response")
        assert not data  # no other elements
        assert response.pop("@Version") == "2.0"
        destination = response.pop("@Destination")
        id = response.pop("@ID")
        in_response_to = response.pop("@InResponseTo", None)
        issue_instant = from_saml_timestamp(response.pop("@IssueInstant"))
        issuer = SAMLNameID.from_xml_value(response.pop("saml:Issuer"))
        status = parse_saml_status(response.pop("samlp:Status"))
        assertion = SAMLAssertion.from_xml_dict(response.pop("saml:Assertion"))
        signature = response.pop("ds:Signature", None)
        response.pop("@xmlns", None)
        if response:
            warnings.warn(f"Unparsed response elements: {response}")
        return cls(
            destination=destination,
            id=id,
            in_response_to=in_response_to,
            issue_instant=issue_instant,
            assertion=assertion,
            issuer=issuer,
            status=status,
            raw_signature=signature,
        )

    def check_issuer(self, issuer: str) -> bool:
        if (
            isinstance(self.issuer, dict)
            and self.issuer.get("@Format") == SAML_NAMEID_FORMAT_ENTITY
        ):
            issuer_str = self.issuer["#text"]
        else:
            issuer_str = self.issuer
        return issuer_str == issuer
