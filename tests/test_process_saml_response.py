import pytest

from smolsaml.login import process_saml_response
from smolsaml.models.idp_configuration import IDPConfiguration
from smolsaml.models.sp_configuration import SPConfiguration
from tests.conftest import metadata_response_fixture_pairs


@pytest.mark.parametrize(
    "metadata_path,response_path",
    metadata_response_fixture_pairs,
    ids=[path.stem for path, _ in metadata_response_fixture_pairs],
)
def test_verify_login_response(
    example_sp_configuration: SPConfiguration,
    metadata_path,
    response_path,
    monkeypatch,
):
    idp_configuration = IDPConfiguration.from_metadata_xml(metadata_path.read_text())
    if "google" in str(metadata_path):
        # Hack the ACS URL because Google (wisely) doesn't allow HTTP URLs
        # in production environments.
        monkeypatch.setattr(
            example_sp_configuration,
            "acs_url",
            example_sp_configuration.acs_url.replace("http", "https"),
        )

    assert process_saml_response(
        idp_configuration=idp_configuration,
        sp_configuration=example_sp_configuration,
        saml_response=response_path.read_text(),
    )


def test_keycloak_login_response(
    example_sp_configuration: SPConfiguration,
    keycloak_idp_configuration: IDPConfiguration,
    keycloak_saml_response: str,
):
    resp = process_saml_response(
        idp_configuration=keycloak_idp_configuration,
        sp_configuration=example_sp_configuration,
        saml_response=keycloak_saml_response,
    )
    assert (
        resp.assertion.subject
        and resp.assertion.subject.name_id == "G-580a44b3-c874-4cc5-b70e-d484cb49f9b5"
    )
    assert len(resp.assertion.get_attribute_values()["Role"]) == 42 + 1
