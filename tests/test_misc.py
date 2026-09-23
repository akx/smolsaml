import pytest

from smolsaml.models.saml_response import SAMLResponse
from smolsaml.models.saml_status import SAMLStatus
from tests.conftest import fixtures_path


def test_adfs_response_with_no_assertion() -> None:
    xml = (fixtures_path / "adfs-response-with-no-assertion.xml").read_text()
    r = SAMLResponse.from_xml(xml)
    assert not r.assertion
    assert r.status == "urn:oasis:names:tc:SAML:2.0:status:Responder"


def test_response_with_status_text() -> None:
    xml = (fixtures_path / "response-with-status-text.xml").read_text()
    r = SAMLResponse.from_xml(xml)
    assert not r.assertion
    status = r.status
    assert status.code == "urn:oasis:names:tc:SAML:2.0:status:Requester"
    assert status.message
    assert status.message.startswith("Unable to satisfy the requested subject")


def test_response_with_complex_status() -> None:
    xml = (fixtures_path / "response-with-complex-status.xml").read_text()
    r = SAMLResponse.from_xml(xml)
    assert not r.assertion
    status = r.status
    assert status.code == "urn:oasis:names:tc:SAML:2.0:status:Responder"
    assert status.message == "Authentication Failed"
    assert status.secondary_codes == ["urn:oasis:names:tc:SAML:2.0:status:AuthnFailed"]
    assert status.detail == {
        "Cause": "org.sourceid.websso.profiles.idp.FailedAuthnSsoException"
    }


def test_status_equality() -> None:
    a = SAMLStatus(code="x", message="m")
    assert a == SAMLStatus(code="x", message="m")
    assert a != SAMLStatus(code="x", message="other")
    assert a == "x"  # legacy
    assert a != "y"


def test_status_str() -> None:
    xml = (fixtures_path / "response-with-complex-status.xml").read_text()
    status_str = str(SAMLResponse.from_xml(xml).status)
    for bit in (
        "urn:oasis:names:tc:SAML:2.0:status:Responder",
        "urn:oasis:names:tc:SAML:2.0:status:AuthnFailed",
        "Authentication Failed",
    ):
        assert bit in status_str


def test_status_message_edge_cases() -> None:
    code = {"@Value": "x"}
    empty = {"samlp:StatusCode": code, "samlp:StatusMessage": None}
    assert SAMLStatus.from_xml_value(empty).message is None
    with_attrs = {
        "samlp:StatusCode": code,
        "samlp:StatusMessage": {"@foo": "bar", "#text": "hello"},
    }
    assert SAMLStatus.from_xml_value(with_attrs).message == "hello"


def test_status_without_code_raises() -> None:
    with pytest.raises(ValueError, match="no StatusCode"):
        SAMLStatus.from_xml_value({"samlp:StatusMessage": "hi"})
