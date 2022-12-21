from __future__ import annotations

import dataclasses
import uuid

from smolsaml.consts import SAML_NAMEID_FORMAT_UNSPECIFIED


@dataclasses.dataclass
class AuthnRequestConfiguration:
    request_id: str = dataclasses.field(default_factory=lambda: f"R-{uuid.uuid4()}")
    force_authn: bool = False
    is_passive: bool = False
    subject_nameid: str | None = None
    subject_nameid_format: str = SAML_NAMEID_FORMAT_UNSPECIFIED
