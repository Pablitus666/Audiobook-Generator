from pathlib import Path

import pytest

from audiobook_generator.readers.docx import DocxReader
from audiobook_generator.readers.epub import EpubReader
from audiobook_generator.readers.factory import ReaderFactory
from audiobook_generator.readers.html import HtmlReader
from audiobook_generator.readers.odt import OdtReader
from audiobook_generator.readers.pdf import PdfReader
from audiobook_generator.readers.rtf import RtfReader
from audiobook_generator.readers.text import TextReader


@pytest.mark.parametrize(
    ("filename", "reader_type"),
    [
        ("libro.txt", TextReader),
        ("libro.md", TextReader),
        ("libro.markdown", TextReader),
        ("libro.pdf", PdfReader),
        ("libro.docx", DocxReader),
        ("libro.epub", EpubReader),
        ("libro.rtf", RtfReader),
        ("libro.html", HtmlReader),
        ("libro.htm", HtmlReader),
        ("libro.xhtml", HtmlReader),
        ("libro.odt", OdtReader),
    ],
)
def test_reader_factory_selects_reader(
    filename: str,
    reader_type: type,
):
    reader = ReaderFactory.create(Path(filename))
    assert isinstance(reader, reader_type)


@pytest.mark.parametrize(
    ("filename", "reader_type"),
    [
        ("LIBRO.TXT", TextReader),
        ("LIBRO.PDF", PdfReader),
        ("LIBRO.DOCX", DocxReader),
        ("LIBRO.EPUB", EpubReader),
        ("LIBRO.RTF", RtfReader),
        ("LIBRO.HTML", HtmlReader),
        ("LIBRO.HTM", HtmlReader),
        ("LIBRO.XHTML", HtmlReader),
        ("LIBRO.ODT", OdtReader),
    ],
)
def test_reader_factory_is_case_insensitive(filename, reader_type):
    assert isinstance(ReaderFactory.create(Path(filename)), reader_type)


def test_reader_factory_rejects_unsupported_format():
    with pytest.raises(
        ValueError,
        match="Formato no soportado",
    ):
        ReaderFactory.create(Path("libro.xyz"))
