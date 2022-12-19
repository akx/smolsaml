from __future__ import annotations

import datetime
from xml.etree.ElementTree import Element

from smolsaml.consts import (
    SAML_BINDING_POST,
    SAML_BINDING_REDIRECT,
    SAML_CM_BEARER,
    SAML_NAMEID_FORMAT_UNSPECIFIED,
)
from smolsaml.exceptions import SAMLResponseVerificationFailed
from smolsaml.models.http import Redirect
from smolsaml.models.idp_configuration import IDPConfiguration
from smolsaml.models.saml_response import SAMLResponse
from smolsaml.models.sp_configuration import SPConfiguration
from smolsaml.response_validation import get_saml_response_validation_errors
from smolsaml.utils.data import compact_dict
from smolsaml.utils.saml import saml_serialize, saml_unserialize, to_saml_timestamp
from smolsaml.utils.xml import NSElement


def get_login_query_parameters(
    authn_request_xml: Element,
    relay_state: str | None = None,
) -> dict[str, str]:
    return compact_dict(
        {
            "SAMLRequest": saml_serialize(authn_request_xml, deflate=True),
            "RelayState": relay_state,
        }
    )


def initiate_login(
    idp_configuration: IDPConfiguration,
    sp_configuration: SPConfiguration,
    request_id: str,
    subject_nameid: str | None = None,
    relay_state: str | None = None,
) -> Redirect:
    sso_url = idp_configuration.get_single_signon_service_url(
        binding=SAML_BINDING_REDIRECT
    )
    authn_request_xml = build_authn_request_xml(
        acs_url=sp_configuration.acs_url,
        destination=sso_url,
        sp_entity_id=sp_configuration.entity_id,
        request_id=request_id,
        subject_nameid=subject_nameid,
    )
    parameters = get_login_query_parameters(
        authn_request_xml=authn_request_xml,
        relay_state=relay_state,
    )
    if idp_configuration.want_authn_requests_signed:
        pass  # TODO: support request signing
    return Redirect(
        url=sso_url,
        parameters=parameters,
    )


def process_saml_response(
    idp_configuration: IDPConfiguration,
    sp_configuration: SPConfiguration,
    saml_response: str,
    request_id: str | None = None,
) -> SAMLResponse:
    xml = saml_unserialize(saml_response)
    parsed_saml_response = SAMLResponse.from_xml(xml)
    errors = list(
        get_saml_response_validation_errors(
            idp_configuration=idp_configuration,
            sp_configuration=sp_configuration,
            xml=xml,
            saml_response=parsed_saml_response,
            request_id=request_id,
        )
    )
    if errors:
        raise SAMLResponseVerificationFailed(
            f"SAML response verification failed with {len(errors)} errors",
            saml_response=parsed_saml_response,
            errors=errors,
        )
    return parsed_saml_response


def build_authn_request_xml(
    *,
    acs_url: str,
    destination: str,
    sp_entity_id: str,
    request_id: str,
    force_authn: bool = False,
    is_passive: bool = False,
    subject_nameid: str | None = None,
    subject_nameid_format: str = SAML_NAMEID_FORMAT_UNSPECIFIED,
) -> Element:
    issued_at = datetime.datetime.utcnow()

    doc = NSElement(
        "samlp",
        "AuthnRequest",
        attrib={
            "ID": request_id,
            "Version": "2.0",
            "IssueInstant": to_saml_timestamp(issued_at),
            "Destination": destination,
            "ProtocolBinding": SAML_BINDING_POST,
            "AssertionConsumerServiceURL": acs_url,
            "ForceAuthn": "true" if force_authn else None,
            "IsPassive": "true" if is_passive else None,
        },
    )
    doc.append(NSElement("saml", "Issuer", text=sp_entity_id))

    if subject_nameid:
        subject = NSElement("saml", "Subject")
        doc.append(subject)
        subject.append(
            NSElement(
                "saml",
                "NameID",
                text=subject_nameid,
                attrib={
                    "Format": subject_nameid_format,
                },
            )
        )
        # TODO: is this necessary?
        subject.append(
            NSElement(
                "saml",
                "SubjectConfirmation",
                attrib={
                    "Method": SAML_CM_BEARER,
                },
            )
        )

    # TODO: RequestedAuthnContext?

    return doc
