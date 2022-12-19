import pytest

from smolsaml.models.idp_configuration import IDPConfiguration
from smolsaml.xmlsec.exceptions import XMLSecError
from smolsaml.xmlsec.verify import verify_xml_signature

BAD_XMLS = [
    # TODO: Add more bad XMLs
    b"<xml></xml>",  # No signature
]


@pytest.mark.parametrize("xml", BAD_XMLS)
def test_bad_sig(xml, keycloak_idp_configuration: IDPConfiguration):
    with pytest.raises(XMLSecError):
        certs = keycloak_idp_configuration.get_signing_certificates()
        verify_xml_signature(
            xml=xml,
            trusted_signing_certificates=certs,
        )
