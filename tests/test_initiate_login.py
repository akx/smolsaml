from smolsaml.login import initiate_login
from smolsaml.models.idp_configuration import IDPConfiguration
from smolsaml.models.sp_configuration import SPConfiguration


def test_initiate_login(
    example_sp_configuration: SPConfiguration,
    keycloak_idp_configuration: IDPConfiguration,
):
    redir = initiate_login(
        idp_configuration=keycloak_idp_configuration,
        sp_configuration=example_sp_configuration,
        request_id="123",
        relay_state="456",
    )
    # We know this magic from the test fixtures
    assert redir.full_url.startswith(
        "http://127.0.0.1:8080/auth/realms/master/protocol/saml"
    )
    assert "RelayState=456" in redir.full_url
