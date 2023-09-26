from smolsaml.models.saml_response import SAMLResponse
from tests.conftest import fixtures_path


def test_adfs_response_with_no_assertion() -> None:
    xml = (fixtures_path / "adfs-response-with-no-assertion.xml").read_text()
    r = SAMLResponse.from_xml(xml)
    assert not r.assertion
    assert r.status == "urn:oasis:names:tc:SAML:2.0:status:Responder"
