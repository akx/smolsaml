import pathlib
import traceback
from functools import cache
from uuid import uuid4

from flask import Flask, redirect, request

from smolsaml.login import initiate_login, process_saml_response
from smolsaml.models.idp_configuration import IDPConfiguration
from smolsaml.models.sp_configuration import SPConfiguration

app = Flask(__name__)
app.config.update(
    {
        "IDP_METADATA_URL": None,
        "IDP_METADATA_PATH": None,
    }
)
app.config.from_prefixed_env("SMOLSAML")

sp_configuration = SPConfiguration(
    entity_id="http://127.0.0.1:5000/",
    acs_url="http://127.0.0.1:5000/acs",
)


@cache
def get_metadata_xml() -> str:
    metadata_path = app.config.get("IDP_METADATA_PATH")
    if metadata_path:
        return pathlib.Path(metadata_path).read_text()
    metadata_url = app.config.get("IDP_METADATA_URL")
    if metadata_url:
        import requests

        resp = requests.get(metadata_url)
        resp.raise_for_status()
        return resp.text
    raise RuntimeError(
        "No IDP metadata found "
        "(set SMOLSAML_IDP_METADATA_PATH or SMOLSAML_IDP_METADATA_URL)"
    )


@app.get("/")
def home():
    return f"""
    Metadata URL: {app.config['IDP_METADATA_URL']}<br />
    Metadata Path: {app.config['IDP_METADATA_PATH']}
    <hr />
    <a href="/login">Initiate login</a>
    """


@app.get("/login")
def login():
    idp_configuration = IDPConfiguration.from_metadata_xml(get_metadata_xml())
    redir = initiate_login(
        idp_configuration=idp_configuration,
        sp_configuration=sp_configuration,
        request_id=f"RID_{uuid4()}",
        relay_state="/foo-relay/",
    )
    return redirect(redir.full_url)


@app.post("/acs")
def acs():
    idp_configuration = IDPConfiguration.from_metadata_xml(get_metadata_xml())
    try:
        resp = process_saml_response(
            idp_configuration=idp_configuration,
            sp_configuration=sp_configuration,
            saml_response=request.form["SAMLResponse"],
        )
    except Exception:
        resp = traceback.format_exc()
    return f"""
    Data:
    <pre>{dict(request.form)}</pre>
    <hr />
    Response:
    <pre>{resp}</pre>
    """


if __name__ == "__main__":
    if not (app.config["IDP_METADATA_URL"] or app.config["IDP_METADATA_PATH"]):
        raise ValueError("IDP_METADATA_URL or IDP_METADATA_PATH must be set")
    app.run(debug=True)
