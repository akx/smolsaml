from __future__ import annotations

from smolsaml.models.saml_response import SAMLResponse


class SAMLResponseVerificationFailed(Exception):
    # This could be an ExceptionGroup when targeting Python 3.11+.

    def __init__(self, msg, saml_response: SAMLResponse, errors: list[Exception]):
        super().__init__(f"{msg}: {', '.join(str(e) for e in errors)}")
        self.saml_response = saml_response
        self.errors = errors
