from __future__ import annotations

from typing import Any
from xml.etree.ElementTree import Element
from xml.parsers import expat

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


class _DictBuilder:
    NS_SEPARATOR = " "

    def __init__(self) -> None:
        self.stack: list[tuple[dict[str, Any] | None, list[str]]] = []
        self.item: dict[str, Any] | None = None
        self.data: list[str] = []

    def _build_name(self, full_name: str) -> str:
        namespace, sep, name = full_name.rpartition(self.NS_SEPARATOR)
        if not sep:
            return full_name
        return f"{INVERSE_XML_NAMESPACES.get(namespace, namespace)}:{name}"

    def start_element(self, full_name: str, attrs: dict[str, str]) -> None:
        self.stack.append((self.item, self.data))
        self.item = {f"@{self._build_name(k)}": v for k, v in attrs.items()} or None
        self.data = []

    def end_element(self, full_name: str) -> None:
        name = self._build_name(full_name)
        data: str | None = "".join(self.data).strip() or None
        item = self.item
        self.item, self.data = self.stack.pop()
        if item is not None:
            if data:
                _push(item, "#text", data)
            self.item = _push(self.item, name, item)
        else:
            self.item = _push(self.item, name, data)

    def characters(self, data: str) -> None:
        self.data.append(data)


def _push(item: dict[str, Any] | None, key: str, value: Any) -> dict[str, Any]:
    if item is None:
        item = {}
    if key not in item:
        item[key] = value
    elif isinstance(item[key], list):
        item[key].append(value)
    else:
        item[key] = [item[key], value]
    return item


def _forbid_doctype(*_args: Any) -> None:
    # SAML documents have no business having DTDs;
    # forbidding them outright sidesteps entity expansion attacks and the like.
    raise ValueError("DTDs are not allowed")


def parse_to_dict(xml: str | bytes) -> dict[str, Any]:
    if isinstance(xml, str):
        xml = xml.encode("utf-8")
    builder = _DictBuilder()
    parser = expat.ParserCreate(namespace_separator=_DictBuilder.NS_SEPARATOR)
    parser.StartDoctypeDeclHandler = _forbid_doctype
    parser.EntityDeclHandler = _forbid_doctype
    parser.StartElementHandler = builder.start_element
    parser.EndElementHandler = builder.end_element
    parser.CharacterDataHandler = builder.characters
    parser.buffer_text = True
    parser.Parse(xml, True)
    return builder.item or {}
