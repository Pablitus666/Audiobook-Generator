from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path


class PdfPageRenderer(ABC):
    """Interfaz para renderizar páginas PDF como imágenes."""

    @abstractmethod
    def render_page(self, source: Path, page_number: int, dpi: int) -> bytes:
        """Renderiza una página y devuelve una imagen PNG."""
        raise NotImplementedError


class PyMuPdfPageRenderer(PdfPageRenderer):
    """Renderizador PDF basado en PyMuPDF."""

    def render_page(
        self,
        source: Path,
        page_number: int,
        dpi: int,
    ) -> bytes:
        try:
            import pymupdf
        except ImportError as exc:
            raise RuntimeError(
                "PyMuPDF no está instalado. "
                "Instala: pip install -r requirements-ocr.txt"
            ) from exc

        try:
            with pymupdf.open(str(source)) as document:
                page = document.load_page(page_number)
                scale = dpi / 72.0
                matrix = pymupdf.Matrix(scale, scale)
                pixmap = page.get_pixmap(
                    matrix=matrix,
                    alpha=False,
                )
                return pixmap.tobytes("png")
        except Exception as exc:
            raise RuntimeError(
                f"no se pudo renderizar la página {page_number + 1} del PDF"
            ) from exc
