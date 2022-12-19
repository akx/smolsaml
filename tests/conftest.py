from __future__ import annotations

import pathlib

import pytest

from smolsaml.models.idp_configuration import IDPConfiguration
from smolsaml.models.sp_configuration import SPConfiguration

fixtures_path = pathlib.Path(__file__).parent / "fixtures"


# We may not always have all metadata/response fixtures
# (some may contain private information and are not shipped with the codebase).
# Thus, let's find all that we do have, and use them in the tests.
def _get_metadata_response_fixture_pairs():
    for metadata_path in fixtures_path.glob("*-idp-metadata.xml"):
        response_path = _metadata_path_to_response_path(metadata_path)
        if metadata_path.exists() and response_path.exists():
            yield (metadata_path, response_path)


def _metadata_path_to_response_path(metadata_path: pathlib.Path) -> pathlib.Path:
    return metadata_path.with_name(
        metadata_path.name.replace("-idp-metadata.xml", "-response.txt")
    )


metadata_response_fixture_pairs = list(_get_metadata_response_fixture_pairs())
metadata_fixtures: list[pathlib.Path] = [
    pair[0] for pair in metadata_response_fixture_pairs
]


@pytest.fixture()
def keycloak_idp_configuration() -> IDPConfiguration:
    metadata_xml = (fixtures_path / "keycloak-idp-metadata.xml").read_text()
    return IDPConfiguration.from_metadata_xml(metadata_xml)


@pytest.fixture()
def keycloak_saml_response() -> str:
    return (fixtures_path / "keycloak-response.txt").read_text()


@pytest.fixture()
def example_sp_configuration() -> SPConfiguration:
    # This corresponds to what example_flask_app.py does,
    # which is what the fixtures were generated from.
    return SPConfiguration(
        entity_id="http://127.0.0.1:5000/",
        acs_url="http://127.0.0.1:5000/acs",
    )
