from pathlib import Path
import tomllib


def _project() -> dict:
    return tomllib.loads(
        Path("pyproject.toml").read_text(encoding="utf-8")
    )["project"]


def test_requirements_include_reportlab_for_pdf_test_support():
    requirements = Path("requirements.txt").read_text(encoding="utf-8")
    assert "reportlab>=5.0.0" in requirements


def test_runtime_dependencies_keep_only_tts_engine():
    assert _project()["dependencies"] == ["edge-tts>=7.2.0"]


def test_dev_extra_contains_test_dependencies():
    assert _project()["optional-dependencies"]["dev"] == [
        "pytest>=9.0",
        "pytest-asyncio>=1.0",
        "reportlab>=5.0",
    ]


def test_docs_extra_contains_document_reader_dependencies():
    docs = _project()["optional-dependencies"]["docs"]
    assert docs == [
        "pypdf>=6.0.0",
        "python-docx>=1.2.0",
    ]


def test_ocr_extra_is_self_contained_for_pdf_ocr():
    ocr = _project()["optional-dependencies"]["ocr"]
    assert ocr == [
        "pypdf>=6.0.0",
        "pymupdf>=1.26.5",
        "pytesseract>=0.3.13",
        "Pillow>=11.0.0",
    ]


def test_ocr_requirements_do_not_pull_unrelated_docx_dependency():
    requirements = Path("requirements-ocr.txt").read_text(encoding="utf-8")
    assert "-r requirements.txt" in requirements
    assert "pypdf>=6.0.0" in requirements
    assert "pymupdf>=1.26.5" in requirements
    assert "pytesseract>=0.3.13" in requirements
    assert "Pillow>=11.0.0" in requirements
    assert "requirements-docs.txt" not in requirements
    assert "python-docx" not in requirements
