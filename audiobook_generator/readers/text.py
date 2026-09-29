from __future__ import annotations

from pathlib import Path

from audiobook_generator.core.errors import (
    DocumentReadError,
    InputFileError,
)
from audiobook_generator.core.models import Document
from audiobook_generator.readers.base import DocumentReader


class TextReader(DocumentReader):
    """Lector para archivos de texto plano."""

    def read(self, source: Path) -> Document:
        if not source.is_file():
            raise InputFileError(
                f"no existe el archivo de entrada: {source}"
            )

        try:
            text = source.read_text(encoding="utf-8-sig")
        except UnicodeDecodeError as exc:
            raise DocumentReadError(
                f"no se pudo decodificar el archivo como UTF-8: {source}"
            ) from exc
        except OSError as exc:
            raise DocumentReadError(
                f"no se pudo leer el archivo: {source}"
            ) from exc

        return Document(
            title=source.stem,
            source=source,
            text=text,
        )