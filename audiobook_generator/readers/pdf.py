from __future__ import annotations

import io
import re
from pathlib import Path

from audiobook_generator.core.config import OcrConfig
from audiobook_generator.core.errors import (
    DocumentReadError,
    InputFileError,
    OcrError,
)
from audiobook_generator.core.models import Document
from audiobook_generator.ocr.base import OcrEngine
from audiobook_generator.readers.base import DocumentReader
from audiobook_generator.readers.pdf_renderer import (
    PdfPageRenderer,
    PyMuPdfPageRenderer,
)


_MIN_TEXT_CHARACTERS = 20
_VALID_OCR_MODES = {"auto", "always", "never"}
_VALID_OCR_PSM = range(1, 14)

# El aumento de tamaño ayuda especialmente con texto pequeño en
# documentos escaneados. Se mantiene moderado para no disparar
# innecesariamente el consumo de memoria.
_OCR_SCALE_FACTOR = 1.0
# Evita sobreampliar escaneos que ya vienen a 250–300 DPI.
# Tesseract suele segmentar mejor texto jurídico a una resolución efectiva
# cercana a 180–220 DPI que una imagen artificialmente enorme.
_OCR_MAX_DIMENSION = 3000


def _text_character_count(text: str) -> int:
    return len(re.sub(r"\s+", "", text))


def _page_has_images(page: object) -> bool:
    try:
        images = getattr(page, "images", ())
        return bool(images)
    except Exception:
        return False


def _image_is_effectively_blank(image_bytes: bytes) -> bool:
    """Detecta páginas escaneadas prácticamente vacías antes de mejorar la imagen.

    Es importante hacer esta comprobación antes de autocontraste: en un
    reverso casi vacío, el autocontraste puede amplificar marcas tenues,
    transparencias o texto del otro lado de la hoja y convertirlas en falso
    texto para Tesseract.
    """
    try:
        from PIL import Image
    except ImportError:
        return False

    try:
        import numpy as np
    except ImportError:
        try:
            with Image.open(io.BytesIO(image_bytes)) as image:
                gray = image.convert("L")
                gray.thumbnail((400, 400))
                histogram = gray.histogram()
                total = sum(histogram) or 1
                dark = sum(histogram[:220]) / total
                return dark < 0.005
        except Exception:
            return False

    try:
        with Image.open(io.BytesIO(image_bytes)) as image:
            gray = image.convert("L")
            gray.thumbnail((500, 500))
            pixels = np.asarray(gray, dtype=np.uint8)
            if pixels.size == 0:
                return True

            # Conservador: no descartar escaneos claros que sí contienen texto.
            dark_ratio = float((pixels < 220).mean())
            return float(pixels.std()) < 8.0 and dark_ratio < 0.005
    except Exception:
        return False


def _preprocess_ocr_image(image_bytes: bytes) -> bytes:
    """Mejora una imagen de página antes de enviarla a Tesseract.

    El procesamiento es deliberadamente conservador:
    - escala de grises;
    - autocontraste;
    - ampliación moderada;
    - enfoque suave.

    Si Pillow no está disponible o el procesamiento falla, devuelve
    la imagen original para no impedir el OCR.
    """
    try:
        from PIL import Image, ImageEnhance, ImageFilter, ImageOps
    except ImportError:
        return image_bytes

    try:
        with Image.open(io.BytesIO(image_bytes)) as image:
            # El OCR de documentos normalmente funciona mejor con una
            # imagen monocromática que con información de color innecesaria.
            processed = image.convert("L")

            # Mejora el contraste cuando el escaneo tiene fondo gris,
            # iluminación irregular o texto poco definido.
            processed = ImageOps.autocontrast(
                processed,
                cutoff=1,
            )

            # No sobreampliamos páginas que ya fueron renderizadas a alta
            # resolución. Una imagen excesivamente grande puede empeorar la
            # segmentación de Tesseract y aumenta mucho el coste de OCR.
            width, height = processed.size
            scale = _OCR_SCALE_FACTOR
            longest_side = max(width, height)
            if longest_side > _OCR_MAX_DIMENSION:
                scale = min(scale, _OCR_MAX_DIMENSION / longest_side)

            if abs(scale - 1.0) > 0.01:
                new_size = (
                    max(1, round(width * scale)),
                    max(1, round(height * scale)),
                )
                processed = processed.resize(
                    new_size,
                    Image.Resampling.LANCZOS,
                )

            # Enfoque suave para recuperar bordes de caracteres.
            processed = processed.filter(
                ImageFilter.UnsharpMask(
                    radius=1.2,
                    percent=120,
                    threshold=3,
                )
            )

            # Un pequeño refuerzo de contraste después del escalado.
            processed = ImageEnhance.Contrast(processed).enhance(1.10)

            output = io.BytesIO()
            processed.save(output, format="PNG")
            return output.getvalue()

    except Exception:
        # El preprocesamiento nunca debe impedir que Tesseract intente
        # reconocer la imagen original.
        return image_bytes


class PdfReader(DocumentReader):
    """Lector PDF con detección y OCR opcional por página."""

    def __init__(
        self,
        ocr_engine: OcrEngine | None = None,
        renderer: PdfPageRenderer | None = None,
        ocr_config: OcrConfig | None = None,
    ) -> None:
        self.ocr_engine = ocr_engine
        self.renderer = renderer
        self.ocr_config = ocr_config or OcrConfig()

        if self.ocr_config.mode not in _VALID_OCR_MODES:
            raise ValueError(
                "modo OCR no soportado: "
                f"{self.ocr_config.mode}. "
                "Valores permitidos: auto, always, never."
            )

        if self.ocr_config.dpi <= 0:
            raise ValueError("la resolución OCR debe ser mayor que cero.")

        if self.ocr_config.psm not in _VALID_OCR_PSM:
            raise ValueError("el modo PSM de OCR debe estar entre 1 y 13.")

    def _get_ocr_engine(self) -> OcrEngine:
        if self.ocr_engine is None:
            from audiobook_generator.ocr.tesseract import TesseractOcrEngine

            self.ocr_engine = TesseractOcrEngine(
                language=self.ocr_config.language,
                psm=self.ocr_config.psm,
            )

        return self.ocr_engine

    def _get_renderer(self) -> PdfPageRenderer:
        if self.renderer is None:
            self.renderer = PyMuPdfPageRenderer()

        return self.renderer

    def _ocr_page(
        self,
        source: Path,
        page_number: int,
    ) -> str:
        engine = self._get_ocr_engine()

        if not engine.is_available():
            raise OcrError(
                "El PDF contiene páginas sin texto extraíble y necesita OCR, "
                "pero OCR no está disponible. "
                "Instala los componentes con "
                "'pip install -r requirements-ocr.txt' y asegúrate de tener "
                "Tesseract OCR instalado y disponible en PATH."
            )

        renderer = self._get_renderer()

        try:
            image = renderer.render_page(
                source,
                page_number,
                self.ocr_config.dpi,
            )

            # Evitamos OCR sobre reversos o páginas prácticamente vacías.
            # La comprobación ocurre antes de autocontraste para que el ruido
            # tenue no sea amplificado artificialmente.
            if _image_is_effectively_blank(image):
                return ""

            # Preprocesamos la imagen antes de enviarla a Tesseract.
            # La función tiene fallback automático a la imagen original.
            processed_image = _preprocess_ocr_image(image)

            return engine.recognize(processed_image)

        except OcrError:
            raise
        except Exception as exc:
            raise OcrError(
                f"no se pudo aplicar OCR a la página {page_number + 1} "
                f"del PDF: {exc}"
            ) from exc

    def read(self, source: Path) -> Document:
        if not source.is_file():
            raise InputFileError(
                f"no existe el archivo de entrada: {source}"
            )

        try:
            from pypdf import PdfReader as PypdfReader
        except ImportError as exc:
            raise DocumentReadError(
                "Para PDF instala las dependencias de documentos: "
                "pip install -r requirements-docs.txt"
            ) from exc

        try:
            reader = PypdfReader(str(source))
            pages: list[str] = []
            ocr_candidates = 0
            ocr_applied = False

            for page_number, page in enumerate(reader.pages):
                text = (page.extract_text() or "").strip()
                text_count = _text_character_count(text)
                has_images = _page_has_images(page)

                needs_ocr = (
                    self.ocr_config.mode == "always"
                    or (
                        self.ocr_config.mode == "auto"
                        and has_images
                        and text_count < _MIN_TEXT_CHARACTERS
                    )
                )

                if (
                    self.ocr_config.mode == "never"
                    and has_images
                    and text_count < _MIN_TEXT_CHARACTERS
                ):
                    ocr_candidates += 1

                if needs_ocr and self.ocr_config.mode != "never":
                    ocr_applied = True
                    ocr_text = self._ocr_page(
                        source,
                        page_number,
                    ).strip()

                    if ocr_text:
                        text = ocr_text

                if text:
                    pages.append(text)

            if (
                self.ocr_config.mode == "never"
                and ocr_candidates > 0
                and not pages
            ):
                raise OcrError(
                    "El PDF no contiene texto extraíble. "
                    f"Se detectaron {ocr_candidates} página(s) con imágenes "
                    "que probablemente requieren OCR. "
                    "Usa '--ocr auto' o '--ocr always', o habilita OCR "
                    "en la configuración."
                )

        except OcrError:
            raise
        except Exception as exc:
            raise DocumentReadError(
                f"no se pudo leer el PDF: {source}"
            ) from exc

        return Document(
            title=source.stem,
            source=source,
            text="\n\n".join(pages),
            ocr_applied=ocr_applied,
        )