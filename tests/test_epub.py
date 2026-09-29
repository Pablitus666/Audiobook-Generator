from __future__ import annotations

from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

import pytest

from audiobook_generator.core.errors import DocumentReadError
from audiobook_generator.readers.epub import EpubReader


def _create_epub(
    path: Path,
    *,
    opf_path: str = "OEBPS/content.opf",
    title: str = "Libro de prueba",
) -> None:
    opf_path = opf_path.replace("\\", "/")
    opf_dir = str(Path(opf_path).parent).replace("\\", "/")

    container_xml = f"""\
<?xml version="1.0" encoding="UTF-8"?>
<container
    version="1.0"
    xmlns="urn:oasis:names:tc:opendocument:xmlns:container">
    <rootfiles>
        <rootfile
            full-path="{opf_path}"
            media-type="application/oebps-package+xml"/>
    </rootfiles>
</container>
"""

    opf_xml = f"""\
<?xml version="1.0" encoding="UTF-8"?>
<package
    xmlns="http://www.idpf.org/2007/opf"
    version="2.0">
    <metadata
        xmlns:dc="http://purl.org/dc/elements/1.1/">
        <dc:title>{title}</dc:title>
    </metadata>

    <manifest>
        <item
            id="chapter-1"
            href="text/chapter1.xhtml"
            media-type="application/xhtml+xml"/>
        <item
            id="chapter-2"
            href="text/chapter2.xhtml"
            media-type="application/xhtml+xml"/>
        <item
            id="cover"
            href="images/cover.jpg"
            media-type="image/jpeg"/>
    </manifest>

    <spine>
        <itemref idref="chapter-2"/>
        <itemref idref="chapter-1"/>
    </spine>
</package>
"""

    chapter_1 = """\
<?xml version="1.0" encoding="UTF-8"?>
<html xmlns="http://www.w3.org/1999/xhtml">
<head>
    <title>Ignorar este título</title>
    <style>body { color: red; }</style>
</head>
<body>
    <h1>Capítulo Uno</h1>
    <p>Este es el primer párrafo.</p>
    <p>Segundo párrafo<br/>con salto.</p>
    <script>esto no debe aparecer</script>
</body>
</html>
"""

    chapter_2 = """\
<?xml version="1.0" encoding="UTF-8"?>
<html xmlns="http://www.w3.org/1999/xhtml">
<body>
    <h1>Capítulo Dos</h1>
    <p>Este es el segundo capítulo.</p>
    <div>Texto adicional.</div>
</body>
</html>
"""

    with ZipFile(path, "w", ZIP_DEFLATED) as archive:
        archive.writestr(
            "META-INF/container.xml",
            container_xml,
        )

        archive.writestr(
            opf_path,
            opf_xml,
        )

        archive.writestr(
            f"{opf_dir}/text/chapter1.xhtml",
            chapter_1,
        )

        archive.writestr(
            f"{opf_dir}/text/chapter2.xhtml",
            chapter_2,
        )


def test_epub_reader_extracts_title_and_chapters(
    tmp_path: Path,
):
    epub = tmp_path / "libro.epub"

    _create_epub(epub)

    document = EpubReader().read(epub)

    assert document.title == "Libro de prueba"
    assert document.source == epub
    assert len(document.chapters) == 2


def test_epub_reader_preserves_spine_order(
    tmp_path: Path,
):
    epub = tmp_path / "libro.epub"

    _create_epub(epub)

    document = EpubReader().read(epub)

    assert [chapter.number for chapter in document.chapters] == [
        1,
        2,
    ]

    assert [chapter.title for chapter in document.chapters] == [
        "chapter2",
        "chapter1",
    ]

    assert (
        "Este es el segundo capítulo."
        in document.chapters[0].text
    )

    assert (
        "Este es el primer párrafo."
        in document.chapters[1].text
    )


def test_epub_reader_extracts_readable_xhtml(
    tmp_path: Path,
):
    epub = tmp_path / "libro.epub"

    _create_epub(epub)

    document = EpubReader().read(epub)

    text = document.chapters[1].text

    assert "Capítulo Uno" in text
    assert "Este es el primer párrafo." in text
    assert "Segundo párrafo" in text
    assert "con salto." in text

    assert "Ignorar este título" not in text
    assert "color: red" not in text
    assert "esto no debe aparecer" not in text


def test_epub_reader_resolves_paths_relative_to_opf(
    tmp_path: Path,
):
    epub = tmp_path / "libro.epub"

    _create_epub(
        epub,
        opf_path="Books/EPUB/content.opf",
    )

    document = EpubReader().read(epub)

    assert len(document.chapters) == 2

    assert (
        "Este es el segundo capítulo."
        in document.chapters[0].text
    )


def test_epub_reader_ignores_non_linear_items(
    tmp_path: Path,
):
    epub = tmp_path / "libro.epub"

    container_xml = """\
<?xml version="1.0" encoding="UTF-8"?>
<container
    version="1.0"
    xmlns="urn:oasis:names:tc:opendocument:xmlns:container">
    <rootfiles>
        <rootfile
            full-path="OEBPS/content.opf"
            media-type="application/oebps-package+xml"/>
    </rootfiles>
</container>
"""

    opf_xml = """\
<?xml version="1.0" encoding="UTF-8"?>
<package
    xmlns="http://www.idpf.org/2007/opf"
    version="2.0">
    <metadata
        xmlns:dc="http://purl.org/dc/elements/1.1/">
        <dc:title>Libro</dc:title>
    </metadata>

    <manifest>
        <item
            id="cover"
            href="cover.xhtml"
            media-type="application/xhtml+xml"/>
        <item
            id="chapter"
            href="chapter.xhtml"
            media-type="application/xhtml+xml"/>
    </manifest>

    <spine>
        <itemref
            idref="cover"
            linear="no"/>
        <itemref idref="chapter"/>
    </spine>
</package>
"""

    chapter = """\
<html>
<body>
    <h1>Capítulo</h1>
    <p>Contenido.</p>
</body>
</html>
"""

    cover = """\
<html>
<body>
    <h1>Portada</h1>
</body>
</html>
"""

    with ZipFile(epub, "w", ZIP_DEFLATED) as archive:
        archive.writestr(
            "META-INF/container.xml",
            container_xml,
        )

        archive.writestr(
            "OEBPS/content.opf",
            opf_xml,
        )

        archive.writestr(
            "OEBPS/chapter.xhtml",
            chapter,
        )

        archive.writestr(
            "OEBPS/cover.xhtml",
            cover,
        )

    document = EpubReader().read(epub)

    assert len(document.chapters) == 1
    assert document.chapters[0].title == "chapter"
    assert "Contenido." in document.chapters[0].text
    assert "Portada" not in document.chapters[0].text


def test_epub_reader_rejects_invalid_zip(
    tmp_path: Path,
):
    epub = tmp_path / "corrupto.epub"

    epub.write_bytes(b"esto no es un epub")

    with pytest.raises(
        DocumentReadError,
        match="no se pudo leer el EPUB",
    ):
        EpubReader().read(epub)


def test_epub_reader_rejects_missing_container(
    tmp_path: Path,
):
    epub = tmp_path / "sin-container.epub"

    with ZipFile(epub, "w", ZIP_DEFLATED) as archive:
        archive.writestr(
            "OEBPS/content.opf",
            "<package/>",
        )

    with pytest.raises(
        DocumentReadError,
        match="container.xml válido",
    ):
        EpubReader().read(epub)

def test_epub_reader_numbers_only_loaded_chapters_contiguously(tmp_path: Path):
    epub = tmp_path / "libro.epub"

    container_xml = """<?xml version="1.0" encoding="UTF-8"?>
<container xmlns="urn:oasis:names:tc:opendocument:xmlns:container">
  <rootfiles><rootfile full-path="OEBPS/content.opf" media-type="application/oebps-package+xml"/></rootfiles>
</container>
"""
    opf_xml = """<?xml version="1.0" encoding="UTF-8"?>
<package xmlns="http://www.idpf.org/2007/opf" version="2.0">
  <metadata xmlns:dc="http://purl.org/dc/elements/1.1/"><dc:title>Libro</dc:title></metadata>
  <manifest>
    <item id="missing" href="missing.xhtml" media-type="application/xhtml+xml"/>
    <item id="chapter" href="chapter.xhtml" media-type="application/xhtml+xml"/>
  </manifest>
  <spine>
    <itemref idref="missing"/>
    <itemref idref="chapter"/>
  </spine>
</package>
"""
    chapter = "<html><body><h1>Capítulo</h1><p>Contenido.</p></body></html>"

    with ZipFile(epub, "w", ZIP_DEFLATED) as archive:
        archive.writestr("META-INF/container.xml", container_xml)
        archive.writestr("OEBPS/content.opf", opf_xml)
        archive.writestr("OEBPS/chapter.xhtml", chapter)

    document = EpubReader().read(epub)

    assert len(document.chapters) == 1
    assert document.chapters[0].number == 1
