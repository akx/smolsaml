from __future__ import annotations

from typing import Iterable

from smolsaml.consts import SAML_SUCCESS_STATUS
from smolsaml.models.idp_configuration import IDPConfiguration
from smolsaml.models.saml_response import SAMLResponse
from smolsaml.models.sp_configuration import SPConfiguration
from smolsaml.xmlsec.verify import verify_xml_signature


def get_saml_response_validation_errors(
    *,
    idp_configuration: IDPConfiguration,
    sp_configuration: SPConfiguration,
    saml_response: SAMLResponse,
    xml: bytes,
    request_id: str | None,
) -> Iterable[Exception]:
    if saml_response.status != SAML_SUCCESS_STATUS:
        yield ValueError(f"SAML response status {saml_response.status} is not success")
    if saml_response.destination != sp_configuration.acs_url:
        yield ValueError(
            f"SAMLResponse destination {saml_response.destination!r} "
            f"does not match ACS URL {sp_configuration.acs_url!r}"
        )
    if not saml_response.check_issuer(idp_configuration.entity_id):
        yield ValueError(
            f"SAMLResponse issuer {saml_response.issuer!r} "
            f"does not match IDP entity ID {idp_configuration.entity_id!r}"
        )
    if request_id and saml_response.in_response_to != request_id:
        yield ValueError(
            f"SAMLResponse InResponseTo {saml_response.in_response_to} "
            f"does not match request ID {request_id!r}"
        )
    # TODO: verify datetimes
    try:
        verify_xml_signature(
            xml,
            trusted_signing_certificates=list(
                idp_configuration.get_signing_certificates()
            ),
        )
    except Exception as e:
        yield e
