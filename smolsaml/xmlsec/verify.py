from __future__ import annotations

import itertools
import subprocess
from contextlib import ExitStack
from tempfile import NamedTemporaryFile
from typing import Iterable

from smolsaml.consts import SAML_NS_ASSERTION, SAML_NS_PROTOCOL
from smolsaml.xmlsec.exceptions import XMLSecError
from smolsaml.xmlsec.utils import find_xmlsec

ID_ATTRS = [
    ("ID", f"{SAML_NS_PROTOCOL}:Response"),  # Keycloak and Okta sign the Response
    ("ID", f"{SAML_NS_ASSERTION}:Assertion"),  # Google signs the Assertion
]

XMLSEC_VERIFY_ARGS = [
    # Add `--id-attr` "hack" arguments to tell the xmlsec too
    # where to look for the ID attribute (in terms of namespace and attribute name).
    *itertools.chain(*([f"--id-attr:{attr}", tag] for (attr, tag) in ID_ATTRS)),
]


def verify_xml_signature(
    xml: bytes,
    trusted_signing_certificates: Iterable[bytes],
) -> bool:
    # TODO: this needs to be tested hard!
    if not trusted_signing_certificates:
        raise ValueError("No trusted signing certificates provided")
    with ExitStack() as stack:
        xml_file = stack.enter_context(
            NamedTemporaryFile("wb", prefix="smolsaml", suffix=".xml")
        )
        xml_file.write(xml)
        xml_file.flush()
        cert_paths = []
        for cert in trusted_signing_certificates:
            cert_file = stack.enter_context(
                NamedTemporaryFile(prefix="smolsaml", suffix=".crt")
            )
            cert_file.write(cert)
            cert_file.flush()
            cert_paths.append(cert_file.name)
        result = _run_xmlsec_verify(xml_file.name, cert_paths)
    if result.returncode == 0:
        return True
    raise XMLSecError("Failed to verify XML signature", results=[result])


def _run_xmlsec_verify(
    xml_path: str, cert_paths: list[str]
) -> subprocess.CompletedProcess:
    args = [
        find_xmlsec(),
        "verify",
        *itertools.chain(*(["--trusted-der", cert_path] for cert_path in cert_paths)),
        *XMLSEC_VERIFY_ARGS,
        xml_path,
    ]
    return subprocess.run(
        args,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        errors="replace",
        encoding="utf-8",
        timeout=10,
    )
