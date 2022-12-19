from __future__ import annotations

import shutil
from functools import lru_cache

XMLSEC_BINARY_NAMES = ["xmlsec1", "xmlsec1-openssl", "xmlsec"]


@lru_cache(None)
def find_xmlsec() -> str:
    for binary_name in XMLSEC_BINARY_NAMES:
        path = shutil.which(binary_name)
        if path:
            return path
    raise RuntimeError(f"xmlsec not found in PATH, tried: {XMLSEC_BINARY_NAMES}")
