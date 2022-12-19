import pytest

from smolsaml.models.idp_configuration import IDPConfiguration
from tests.conftest import metadata_fixtures


@pytest.mark.parametrize("idp_config_path", metadata_fixtures)
def test_idp_config(idp_config_path):
    assert IDPConfiguration.from_metadata_xml(idp_config_path.read_text())
