from __future__ import annotations

from html.parser import HTMLParser
import re
from pathlib import Path
from typing import Final

from audiobook_generator.core.errors import (
    DocumentReadError,
    InputFileError,
)
from audiobook_generator.core.models import Document
from audiobook_generator.readers.base import DocumentReader


class _HtmlTextExtractor(HTMLParser):
    """Extrae texto legible de HTML y XHTML."""

    _BLOCK_TAGS: Final = {
        "address", "article", "aside", "blockquote", "br", "div",
        "dl", "dt", "dd", "figcaption", "figure", "footer", "h1",
        "h2", "h3", "h4", "h5", "h6", "header", "hr", "li", "main",
        "nav", "ol", "p", "pre", "section", "table", "td", "th", "tr",
        "ul",
    }
    _IGNORED_TAGS: Final = {"head", "script", "style", "svg", "noscript"}
    _INLINE_TEXT_TAGS: Final = {
        "a", "b", "code", "em", "i", "mark", "s", "small",
        "span", "strong", "sub", "sup", "u",
    }

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.parts: list[str] = []
        self.ignored_depth = 0
        self.title_parts: list[str] = []
        self.in_title = False

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        tag = tag.lower()
        if tag in self._IGNORED_TAGS:
            self.ignored_depth += 1
            return
        if tag == "title":
            self.in_title = True
            return
        if self.ignored_depth:
            return
        if tag in self._BLOCK_TAGS:
            self._newline()
        elif tag in self._INLINE_TEXT_TAGS and self.parts and self.parts[-1] != "\n":
            self.parts.append(" ")

    def handle_startendtag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag.lower() in self._BLOCK_TAGS:
            self._newline()

    def handle_endtag(self, tag: str) -> None:
        tag = tag.lower()
        if tag == "title":
            self.in_title = False
            return
        if tag in self._IGNORED_TAGS:
            self.ignored_depth = max(0, self.ignored_depth - 1)
            return
        if not self.ignored_depth and tag in self._BLOCK_TAGS:
            self._newline()

    def handle_data(self, data: str) -> None:
        if self.in_title:
            self.title_parts.append(data)
        if self.ignored_depth:
            return
        text = " ".join(data.split())
        if text:
            self.parts.append(text)

    def _newline(self) -> None:
        if self.parts and self.parts[-1] != "\n":
            self.parts.append("\n")

    def get_text(self) -> str:
        raw = "".join(self.parts)
        lines = [" ".join(line.split()) for line in raw.splitlines()]
        return "\n\n".join(line for line in lines if line)

    def get_title(self) -> str:
        return " ".join("".join(self.title_parts).split())


class HtmlReader(DocumentReader):
    """Lector de archivos HTML/XHTML."""

    def read(self, source: Path) -> Document:
        if not source.is_file():
            raise InputFileError(
                f"no existe el archivo de entrada: {source}"
            )

        try:
            raw = source.read_bytes()
        except OSError as exc:
            raise DocumentReadError(
                f"no se pudo leer el archivo HTML: {source}"
            ) from exc

        try:
            encoding = self._detect_encoding(raw)
            content = raw.decode(encoding, errors="replace")
            parser = _HtmlTextExtractor()
            parser.feed(content)
            parser.close()
            text = parser.get_text()
            title = parser.get_title() or source.stem
        except Exception as exc:
            raise DocumentReadError(
                f"no se pudo leer el archivo HTML: {source}"
            ) from exc

        return Document(
            title=title,
            source=source,
            text=text,
        )

    @staticmethod
    def _detect_encoding(raw: bytes) -> str:
        """Detecta la codificación habitual de documentos HTML.

        Prioriza BOM y después revisa las declaraciones ``charset`` de
        ``meta``. Si no existe ninguna, UTF-8 sigue siendo el valor por
        defecto moderno y seguro.
        """
        if raw.startswith(b"\xef\xbb\xbf"):
            return "utf-8-sig"
        if raw.startswith(b"\xff\xfe") or raw.startswith(b"\xfe\xff"):
            return "utf-16"

        head = raw[:8192].decode("ascii", errors="ignore")

        match = re.search(
            r"<meta\b[^>]+charset\s*=\s*[\"']?\s*([a-zA-Z0-9._:-]+)",
            head,
            flags=re.IGNORECASE,
        )
        if match:
            return match.group(1)

        match = re.search(
            r"<meta\b[^>]+content\s*=\s*[\"'][^\"']*?charset\s*=\s*([a-zA-Z0-9._:-]+)",
            head,
            flags=re.IGNORECASE,
        )
        if match:
            return match.group(1)

        return "utf-8"


