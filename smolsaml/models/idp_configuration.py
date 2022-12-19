from __future__ import annotations

import base64
import dataclasses
from typing import Iterable

from smolsaml.models.utils import listify, only_one_or_raise
from smolsaml.utils.xml import parse_to_dict


@dataclasses.dataclass
class IDPConfiguration:
    entity_id: str
    want_authn_requests_signed: bool = False
    key_descriptors: list[dict] = dataclasses.field(default_factory=list)
    single_signon_service_url_descriptions: list[dict] = dataclasses.field(
        default_factory=list
    )
    single_logout_service_url_descriptions: list[dict] = dataclasses.field(
        default_factory=list
    )

    @classmethod
    def from_metadata_xml(cls, metadata_xml: str) -> IDPConfiguration:
        metadata_dict = parse_to_dict(metadata_xml)
        if metadata_dict.get("md:EntitiesDescriptor"):
            entity_descriptors = listify(
                metadata_dict["md:EntitiesDescriptor"]["md:EntityDescriptor"]
            )
        elif metadata_dict.get("md:EntityDescriptor"):
            entity_descriptors = listify(metadata_dict["md:EntityDescriptor"])
        else:
            raise ValueError("Could not find EntityDescriptor")
        entity_descriptor = only_one_or_raise(
            entity_descriptors, "Expected exactly one EntityDescriptor"
        )
        entity_id = entity_descriptor["@entityID"]
        idp_sso_descriptor = only_one_or_raise(
            listify(entity_descriptor["md:IDPSSODescriptor"]),
            "Expected exactly one IDPSSODescriptor",
        )
        want_authn_requests_signed = (
            idp_sso_descriptor.get("@WantAuthnRequestsSigned") == "true"
        )
        key_descriptors = listify(idp_sso_descriptor["md:KeyDescriptor"])
        sso_url_descriptions = listify(
            idp_sso_descriptor.get("md:SingleSignOnService", [])
        )
        slo_url_descriptions = listify(
            idp_sso_descriptor.get("md:SingleLogoutService", [])
        )
        return cls(
            entity_id=entity_id,
            want_authn_requests_signed=want_authn_requests_signed,
            key_descriptors=key_descriptors,
            single_signon_service_url_descriptions=sso_url_descriptions,
            single_logout_service_url_descriptions=slo_url_descriptions,
        )

    def get_single_signon_service_url(self, binding: str) -> str:
        for url_description in self.single_signon_service_url_descriptions:
            if url_description["@Binding"] == binding:
                return url_description["@Location"]
        raise ValueError(
            "Could not find a single sign-on service URL with the requested binding"
        )

    def get_signing_certificates(self) -> Iterable[bytes]:
        for key_descriptor in self.key_descriptors:
            if key_descriptor["@use"] == "signing":
                yield base64.b64decode(
                    key_descriptor["ds:KeyInfo"]["ds:X509Data"]["ds:X509Certificate"]
                )
