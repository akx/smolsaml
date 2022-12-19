from __future__ import annotations

from typing import Any
from xml.etree.ElementTree import Element

import xmltodict

from smolsaml.consts import INVERSE_XML_NAMESPACES, XML_NAMESPACES
from smolsaml.utils.data import compact_dict


def NSElement(
    namespace: str,
    tag: str,
    *,
    text: str | None = None,
    attrib: dict[str, str | None] | None = None,
) -> Element:
    qualified_tag = f"{{{XML_NAMESPACES.get(namespace, namespace)}}}{tag}"
    el = Element(qualified_tag, compact_dict(attrib or {}))
    if text is not None:
        el.text = text
    return el


def parse_to_dict(xml: str | bytes) -> dict[str, Any]:
    if isinstance(xml, str):
        xml = xml.encode("utf-8")
    return xmltodict.parse(
        xml, process_namespaces=True, namespaces=INVERSE_XML_NAMESPACES
    )
