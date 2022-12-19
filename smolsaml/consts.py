from __future__ import annotations

SAML_BINDING_POST = "urn:oasis:names:tc:SAML:2.0:bindings:HTTP-POST"
SAML_BINDING_REDIRECT = "urn:oasis:names:tc:SAML:2.0:bindings:HTTP-Redirect"
SAML_NAMEID_FORMAT_ENTITY = "urn:oasis:names:tc:SAML:2.0:nameid-format:entity"
SAML_NAMEID_FORMAT_UNSPECIFIED = "urn:oasis:names:tc:SAML:1.1:nameid-format:unspecified"
SAML_NS_ASSERTION = "urn:oasis:names:tc:SAML:2.0:assertion"
SAML_NS_METADATA = "urn:oasis:names:tc:SAML:2.0:metadata"
SAML_NS_PROTOCOL = "urn:oasis:names:tc:SAML:2.0:protocol"
SAML_SUCCESS_STATUS = "urn:oasis:names:tc:SAML:2.0:status:Success"

XML_NAMESPACES = {
    "ds": "http://www.w3.org/2000/09/xmldsig#",
    "md": SAML_NS_METADATA,
    "saml": SAML_NS_ASSERTION,
    "samlp": SAML_NS_PROTOCOL,
    "xenc": "http://www.w3.org/2001/04/xmlenc#",
    "xs": "http://www.w3.org/2001/XMLSchema",
    "xsi": "http://www.w3.org/2001/XMLSchema-instance",
}
INVERSE_XML_NAMESPACES = {uri: mnemonic for mnemonic, uri in XML_NAMESPACES.items()}
SAML_CM_BEARER = "urn:oasis:names:tc:SAML:2.0:cm:bearer"
