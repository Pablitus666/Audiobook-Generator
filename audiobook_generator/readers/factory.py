from __future__ import annotations

from pathlib import Path

from audiobook_generator.core.errors import UnsupportedFormatError
from audiobook_generator.readers.base import DocumentReader
from audiobook_generator.readers.docx import DocxReader
from audiobook_generator.readers.epub import EpubReader
from audiobook_generator.readers.html import HtmlReader
from audiobook_generator.readers.odt import OdtReader
from audiobook_generator.readers.rtf import RtfReader
from audiobook_generator.readers.pdf import PdfReader
from audiobook_generator.readers.text import TextReader


class ReaderFactory:
    """Crea el lector adecuado según la extensión del archivo."""

    _READERS: dict[str, type[DocumentReader]] = {
        ".txt": TextReader,
        ".md": TextReader,
        ".markdown": TextReader,
        ".pdf": PdfReader,
        ".docx": DocxReader,
        ".epub": EpubReader,
        ".rtf": RtfReader,
        ".html": HtmlReader,
        ".htm": HtmlReader,
        ".xhtml": HtmlReader,
        ".odt": OdtReader,
    }

    @classmethod
    def create(
        cls,
        source: Path,
        *,
        pdf_reader: DocumentReader | None = None,
    ) -> DocumentReader:
        suffix = source.suffix.lower()

        if suffix == ".pdf" and pdf_reader is not None:
            return pdf_reader

        reader_class = cls._READERS.get(suffix)

        if reader_class is None:
            supported = ", ".join(sorted(cls._READERS))
            raise UnsupportedFormatError(
                f"Formato no soportado: {suffix or '[sin extensión]'}. "
                f"Soportados: {supported}"
            )

        return reader_class()
