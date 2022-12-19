from __future__ import annotations

import base64
import datetime
import zlib
from xml.etree import ElementTree
from xml.etree.ElementTree import Element


def to_saml_timestamp(dt: datetime.datetime) -> str:
    utc_dt = datetime.datetime.utcfromtimestamp(dt.timestamp())
    timestamp = utc_dt.isoformat(timespec="seconds")
    if not timestamp.endswith("Z"):
        timestamp += "Z"
    return timestamp


def from_saml_timestamp(s: str) -> datetime.datetime:
    assert s[-1] == "Z"
    assert s[10] == "T"
    return datetime.datetime.fromisoformat(s[:-1].replace("T", " "))


def saml_serialize(data: bytes | Element, deflate: bool) -> str:
    if isinstance(data, Element):
        data = ElementTree.tostring(data, encoding="utf-8")
    assert isinstance(data, bytes)
    if deflate:
        data = zlib.compress(data)[2:-4]
    return base64.b64encode(data).decode("ascii")


def saml_unserialize(data: str, try_deflate: bool = True) -> bytes:
    bin_data = base64.b64decode(data)
    if try_deflate:
        try:
            bin_data = zlib.decompress(bin_data, -15)
        except zlib.error:
            pass
    return bin_data
