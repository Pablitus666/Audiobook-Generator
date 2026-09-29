from __future__ import annotations

from pathlib import Path

import pytest

from audiobook_generator.core.config import OcrConfig
from audiobook_generator.core.errors import OcrError
from audiobook_generator.ocr.base import OcrEngine
from audiobook_generator.readers.pdf import PdfReader


class FakeOcrEngine(OcrEngine):
    def __init__(self, text: str = "Texto reconocido por OCR.") -> None:
        self.text = text
        self.calls: list[bytes] = []

    def is_available(self) -> bool:
        return True

    def recognize(self, image_bytes: bytes) -> str:
        self.calls.append(image_bytes)
        return self.text


class FakeRenderer:
    def __init__(self, image_bytes: bytes = b"fake image") -> None:
        self.calls: list[tuple[Path, int, int]] = []
        self.image_bytes = image_bytes

    def render_page(self, source: Path, page_number: int, dpi: int) -> bytes:
        self.calls.append((source, page_number, dpi))
        return self.image_bytes


def _create_text_pdf(path: Path) -> None:
    from reportlab.lib.pagesizes import A4
    from reportlab.pdfgen import canvas

    pdf = canvas.Canvas(str(path), pagesize=A4)
    pdf.drawString(
        72,
        780,
        "Este PDF contiene suficiente texto extraíble para no necesitar OCR.",
    )
    pdf.save()


def _create_image_pdf(path: Path, image_path: Path) -> None:
    from reportlab.lib.pagesizes import A4
    from reportlab.pdfgen import canvas

    pdf = canvas.Canvas(str(path), pagesize=A4)
    pdf.drawImage(str(image_path), 72, 500, width=400, height=150)
    pdf.save()


def _create_test_image(path: Path) -> None:
    from PIL import Image, ImageDraw

    image = Image.new("RGB", (1200, 400), "white")
    draw = ImageDraw.Draw(image)
    draw.text((60, 120), "Texto escaneado de prueba", fill="black")
    image.save(path)


def test_pdf_auto_mode_does_not_require_ocr_for_text_pdf(tmp_path: Path):
    source = tmp_path / "texto.pdf"
    _create_text_pdf(source)

    engine = FakeOcrEngine()
    renderer = FakeRenderer()

    document = PdfReader(
        ocr_engine=engine,
        renderer=renderer,
        ocr_config=OcrConfig(mode="auto"),
    ).read(source)

    assert "Este PDF contiene suficiente texto" in document.text
    assert engine.calls == []
    assert document.ocr_applied is False
    assert renderer.calls == []


def test_pdf_auto_mode_uses_ocr_for_image_page(tmp_path: Path):
    source = tmp_path / "escaneado.pdf"
    image = tmp_path / "pagina.png"
    _create_test_image(image)
    _create_image_pdf(source, image)

    engine = FakeOcrEngine("Texto obtenido mediante OCR.")
    renderer = FakeRenderer()

    document = PdfReader(
        ocr_engine=engine,
        renderer=renderer,
        ocr_config=OcrConfig(mode="auto", language="spa", dpi=250),
    ).read(source)

    assert document.text == "Texto obtenido mediante OCR."
    assert document.ocr_applied is True
    assert len(engine.calls) == 1
    assert renderer.calls[0][1] == 0
    assert renderer.calls[0][2] == 250


def test_pdf_auto_mode_skips_effectively_blank_image_page(tmp_path: Path):
    source = tmp_path / "pagina_vacia.pdf"
    image = tmp_path / "pagina_vacia.png"

    from PIL import Image

    Image.new("RGB", (1200, 1600), (252, 252, 252)).save(image)

    from reportlab.lib.pagesizes import A4
    from reportlab.pdfgen import canvas

    pdf = canvas.Canvas(str(source), pagesize=A4)
    pdf.drawImage(str(image), 0, 0, width=A4[0], height=A4[1])
    pdf.save()

    engine = FakeOcrEngine("Texto que no debería producirse.")
    renderer = FakeRenderer(image.read_bytes())

    document = PdfReader(
        ocr_engine=engine,
        renderer=renderer,
        ocr_config=OcrConfig(mode="auto"),
    ).read(source)

    assert document.text == ""
    assert document.ocr_applied is True
    assert engine.calls == []
    assert len(renderer.calls) == 1


def test_pdf_never_mode_reports_scanned_document(tmp_path: Path):
    source = tmp_path / "escaneado.pdf"
    image = tmp_path / "pagina.png"
    _create_test_image(image)
    _create_image_pdf(source, image)

    with pytest.raises(
        OcrError,
        match="no contiene texto extraíble",
    ):
        PdfReader(
            ocr_config=OcrConfig(mode="never"),
        ).read(source)


def test_pdf_always_mode_uses_ocr_for_text_page(tmp_path: Path):
    source = tmp_path / "texto.pdf"
    _create_text_pdf(source)

    engine = FakeOcrEngine("OCR forzado.")
    renderer = FakeRenderer()

    document = PdfReader(
        ocr_engine=engine,
        renderer=renderer,
        ocr_config=OcrConfig(mode="always", dpi=300),
    ).read(source)

    assert document.text == "OCR forzado."
    assert len(engine.calls) == 1
    assert renderer.calls[0][2] == 300


def test_pdf_rejects_invalid_ocr_mode():
    with pytest.raises(ValueError, match="modo OCR no soportado"):
        PdfReader(
            ocr_config=OcrConfig(mode="invalid"),
        )


def test_pdf_rejects_invalid_ocr_psm():
    with pytest.raises(ValueError, match="modo PSM de OCR"):
        PdfReader(ocr_config=OcrConfig(psm=14))


def test_tesseract_engine_reports_missing_executable(monkeypatch):
    from audiobook_generator.ocr.tesseract import TesseractOcrEngine

    monkeypatch.setattr(
        "audiobook_generator.ocr.tesseract.shutil.which",
        lambda command: None,
    )

    engine = TesseractOcrEngine()

    assert engine.is_available() is False


def test_tesseract_engine_rejects_invalid_psm():
    from audiobook_generator.ocr.tesseract import TesseractOcrEngine

    with pytest.raises(ValueError, match="psm debe estar entre 1 y 13"):
        TesseractOcrEngine(psm=14)
