from __future__ import annotations

from html.parser import HTMLParser
from pathlib import Path
from posixpath import dirname, join, normpath
from urllib.parse import unquote, urlsplit
from xml.etree import ElementTree as ET
from zipfile import BadZipFile, ZipFile

from audiobook_generator.core.errors import (
    DocumentReadError,
    InputFileError,
)
from audiobook_generator.core.models import Chapter, Document
from audiobook_generator.readers.base import DocumentReader


class _XhtmlTextExtractor(HTMLParser):
    """Extrae texto legible de XHTML de un EPUB."""

    _BLOCK_TAGS = {
        "address",
        "article",
        "aside",
        "blockquote",
        "div",
        "h1",
        "h2",
        "h3",
        "h4",
        "h5",
        "h6",
        "header",
        "li",
        "main",
        "nav",
        "ol",
        "p",
        "section",
        "table",
        "td",
        "th",
        "tr",
        "ul",
    }

    _IGNORED_TAGS = {
        "head",
        "script",
        "style",
        "svg",
    }

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self._parts: list[str] = []
        self._ignored_depth = 0

    def handle_starttag(
        self,
        tag: str,
        attrs: list[tuple[str, str | None]],
    ) -> None:
        tag = tag.lower()

        if tag in self._IGNORED_TAGS:
            self._ignored_depth += 1
            return

        if self._ignored_depth:
            return

        if tag == "br" or tag in self._BLOCK_TAGS:
            self._newline()

    def handle_startendtag(
        self,
        tag: str,
        attrs: list[tuple[str, str | None]],
    ) -> None:
        if tag.lower() == "br":
            self._newline()

    def handle_endtag(self, tag: str) -> None:
        tag = tag.lower()

        if tag in self._IGNORED_TAGS:
            if self._ignored_depth:
                self._ignored_depth -= 1
            return

        if self._ignored_depth:
            return

        if tag in self._BLOCK_TAGS:
            self._newline()

    def handle_data(self, data: str) -> None:
        if self._ignored_depth:
            return

        text = " ".join(data.split())

        if text:
            self._parts.append(text)

    def _newline(self) -> None:
        if self._parts and self._parts[-1] != "\n":
            self._parts.append("\n")

    def get_text(self) -> str:
        text = "".join(self._parts)
        lines = [
            " ".join(line.split())
            for line in text.splitlines()
        ]

        return "\n\n".join(
            line
            for line in lines
            if line
        )


def _local_name(tag: str) -> str:
    """Devuelve el nombre local de una etiqueta XML."""
    return tag.rsplit("}", 1)[-1]


def _find_child(
    root: ET.Element,
    name: str,
) -> ET.Element | None:
    for child in root:
        if _local_name(child.tag) == name:
            return child

    return None


def _find_children(
    root: ET.Element,
    name: str,
) -> list[ET.Element]:
    return [
        child
        for child in root.iter()
        if _local_name(child.tag) == name
    ]


class EpubReader(DocumentReader):
    """Lector de libros EPUB2/EPUB3."""

    def read(self, source: Path) -> Document:
        if not source.is_file():
            raise InputFileError(
                f"no existe el archivo de entrada: {source}"
            )

        try:
            with ZipFile(source) as archive:
                opf_path = self._find_opf_path(archive)
                opf_data = archive.read(opf_path)

                root = ET.fromstring(opf_data)

                title = self._extract_title(root, source.stem)

                manifest = self._extract_manifest(root)
                spine = self._extract_spine(root)

                chapters: list[Chapter] = []

                for index, item_id in enumerate(spine, start=1):
                    item = manifest.get(item_id)

                    if item is None:
                        continue

                    media_type = item["media_type"]

                    if media_type not in {
                        "application/xhtml+xml",
                        "text/html",
                    }:
                        continue

                    href = item["href"]
                    chapter_path = self._resolve_path(
                        opf_path,
                        href,
                    )

                    try:
                        content = archive.read(chapter_path)
                    except KeyError:
                        continue

                    chapter_title, text = self._extract_chapter(
                        content,
                        href,
                    )

                    if not text:
                        continue

                    chapters.append(
                        Chapter(
                            number=index,
                            title=chapter_title,
                            text=text,
                        )
                    )

        except BadZipFile as exc:
            raise DocumentReadError(
                f"no se pudo leer el EPUB: {source}"
            ) from exc
        except (ET.ParseError, KeyError, OSError) as exc:
            raise DocumentReadError(
                f"no se pudo leer el EPUB: {source}"
            ) from exc

        return Document(
            title=title,
            source=source,
            chapters=chapters,
        )

    @staticmethod
    def _find_opf_path(archive: ZipFile) -> str:
        try:
            container_data = archive.read(
                "META-INF/container.xml"
            )

            root = ET.fromstring(container_data)

        except (KeyError, ET.ParseError) as exc:
            raise DocumentReadError(
                "el EPUB no contiene un container.xml válido"
            ) from exc

        for element in root.iter():
            if _local_name(element.tag) != "rootfile":
                continue

            full_path = element.attrib.get("full-path")

            if full_path:
                return unquote(full_path)

        raise DocumentReadError(
            "el EPUB no contiene una ruta OPF válida"
        )

    @staticmethod
    def _extract_title(
        root: ET.Element,
        fallback: str,
    ) -> str:
        for element in root.iter():
            if _local_name(element.tag) != "title":
                continue

            title = " ".join(
                "".join(element.itertext()).split()
            )

            if title:
                return title

        return fallback

    @staticmethod
    def _extract_manifest(
        root: ET.Element,
    ) -> dict[str, dict[str, str]]:
        manifest: dict[str, dict[str, str]] = {}

        for element in _find_children(root, "item"):
            item_id = element.attrib.get("id")
            href = element.attrib.get("href")
            media_type = element.attrib.get("media-type")

            if not item_id or not href or not media_type:
                continue

            manifest[item_id] = {
                "href": href,
                "media_type": media_type,
            }

        return manifest

    @staticmethod
    def _extract_spine(
        root: ET.Element,
    ) -> list[str]:
        spine = _find_child(root, "spine")

        if spine is None:
            raise DocumentReadError(
                "el EPUB no contiene un spine válido"
            )

        item_ids: list[str] = []

        for element in spine:
            if _local_name(element.tag) != "itemref":
                continue

            if element.attrib.get("linear", "yes") == "no":
                continue

            item_id = element.attrib.get("idref")

            if item_id:
                item_ids.append(item_id)

        return item_ids

    @staticmethod
    def _resolve_path(
        opf_path: str,
        href: str,
    ) -> str:
        href = urlsplit(href).path
        href = unquote(href)

        base_dir = dirname(opf_path)

        if base_dir:
            return normpath(join(base_dir, href))

        return normpath(href)

    @staticmethod
    def _extract_chapter(
        content: bytes,
        href: str,
    ) -> tuple[str, str]:
        parser = _XhtmlTextExtractor()

        try:
            parser.feed(
                content.decode(
                    "utf-8",
                    errors="replace",
                )
            )
            parser.close()
        except Exception as exc:
            raise DocumentReadError(
                f"no se pudo extraer texto del capítulo EPUB: {href}"
            ) from exc

        text = parser.get_text()

        title = Path(
            urlsplit(href).path
        ).stem.replace("_", " ").replace("-", " ")

        return title, text
