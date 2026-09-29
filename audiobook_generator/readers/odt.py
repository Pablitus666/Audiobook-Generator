from __future__ import annotations

from pathlib import Path
from zipfile import BadZipFile, ZipFile
from xml.etree import ElementTree as ET

from audiobook_generator.core.errors import (
    DocumentReadError,
    InputFileError,
)
from audiobook_generator.core.models import Document
from audiobook_generator.readers.base import DocumentReader


_TEXT_TAGS = {"p", "h", "list-item"}
_BREAK_TAGS = {"p", "h", "list-item", "tab", "line-break"}


def _local_name(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


class OdtReader(DocumentReader):
    """Lector de documentos OpenDocument Text (.odt)."""

    def read(self, source: Path) -> Document:
        if not source.is_file():
            raise InputFileError(
                f"no existe el archivo de entrada: {source}"
            )

        try:
            with ZipFile(source) as archive:
                content = archive.read("content.xml")
                root = ET.fromstring(content)
        except BadZipFile as exc:
            raise DocumentReadError(
                f"no se pudo leer el documento ODT: {source}"
            ) from exc
        except (KeyError, ET.ParseError, OSError) as exc:
            raise DocumentReadError(
                f"no se pudo leer el documento ODT: {source}"
            ) from exc

        try:
            text = self._extract_text(root)
            title = self._extract_title(root) or source.stem
        except Exception as exc:
            raise DocumentReadError(
                f"no se pudo extraer texto del documento ODT: {source}"
            ) from exc

        return Document(
            title=title,
            source=source,
            text=text,
        )

    @classmethod
    def _extract_text(cls, root: ET.Element) -> str:
        paragraphs: list[str] = []

        for element in root.iter():
            if _local_name(element.tag) not in _TEXT_TAGS:
                continue

            text = cls._element_text(element).strip()
            if text:
                paragraphs.append(text)

        return "\n\n".join(paragraphs)

    @classmethod
    def _element_text(cls, element: ET.Element) -> str:
        parts: list[str] = []

        def visit(node: ET.Element) -> None:
            name = _local_name(node.tag)

            if node.text:
                parts.append(node.text)

            for child in node:
                child_name = _local_name(child.tag)
                if child_name in {"tab"}:
                    parts.append("\t")
                elif child_name in {"line-break"}:
                    parts.append("\n")
                visit(child)
                if child.tail:
                    parts.append(child.tail)

        visit(element)
        return " ".join("".join(parts).split())

    @staticmethod
    def _extract_title(root: ET.Element) -> str:
        for element in root.iter():
            if _local_name(element.tag) == "title":
                title = " ".join("".join(element.itertext()).split())
                if title:
                    return title

        return ""


