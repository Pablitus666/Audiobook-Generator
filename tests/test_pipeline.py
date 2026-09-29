import asyncio
from pathlib import Path

import pytest

from audiobook_generator.core.config import (
    AudiobookConfig,
    OutputConfig,
    ProcessingConfig,
)
from audiobook_generator.core.models import Document
from audiobook_generator.core.pipeline import AudiobookPipeline


class FakeReader:
    def __init__(self, document=None):
        self.document = document

    def read(self, source):
        return self.document


class FakeTTS:
    def __init__(self):
        self.texts = []
        self.destinations = []

    async def synthesize(self, text, destination):
        self.texts.append(text)
        self.destinations.append(destination)

        destination.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        destination.write_bytes(b"fake mp3")

def fake_merge_mp3(
    chapter_files,
    destination,
    bitrate="128k",
    title=None,
    chapter_titles=None,
):    
    destination.write_bytes(b"fake merged mp3")
    return True


def test_pipeline_generates_each_chapter(
    tmp_path,
    monkeypatch,
):
    document = Document(
        title="Libro",
        source=Path("libro.txt"),
        chapters=[],
        text="Texto de prueba.",
    )

    reader = FakeReader(document)
    tts = FakeTTS()

    monkeypatch.setattr(
        "audiobook_generator.core.pipeline.merge_mp3",
        fake_merge_mp3,
    )

    pipeline = AudiobookPipeline(
        reader=reader,
        tts=tts,
    )

    result = asyncio.run(
        pipeline.run(
            Path("libro.txt"),
            tmp_path,
        )
    )

    assert len(result.chapter_files) == 1
    assert result.chapter_files[0].exists()
    assert result.merged_file is not None
    assert result.merged_file.exists()


def test_pipeline_writes_ocr_debug_files(
    tmp_path,
    monkeypatch,
):
    document = Document(
        title="Escaneado",
        source=Path("escaneado.pdf"),
        text="SENOR FISCAL\nLIBERACIÓON\nTexto real.",
        ocr_applied=True,
    )

    reader = FakeReader(document)
    tts = FakeTTS()

    monkeypatch.setattr(
        "audiobook_generator.core.pipeline.merge_mp3",
        fake_merge_mp3,
    )

    config = AudiobookConfig(
        processing=ProcessingConfig(debug_ocr=True),
    )
    pipeline = AudiobookPipeline(
        reader=reader,
        tts=tts,
        config=config,
    )

    asyncio.run(
        pipeline.run(
            Path("escaneado.pdf"),
            tmp_path,
        )
    )

    debug_dir = tmp_path / "escaneado_ocr_debug"
    assert (debug_dir / "original_ocr.txt").read_text(encoding="utf-8") == document.text
    cleaned = (debug_dir / "cleaned_ocr.txt").read_text(encoding="utf-8")
    assert "SEÑOR FISCAL" in cleaned
    assert "LIBERACIÓN" in cleaned


def test_pipeline_does_not_write_ocr_debug_for_native_text(
    tmp_path,
    monkeypatch,
):
    document = Document(
        title="Libro",
        source=Path("libro.txt"),
        text="Texto nativo.",
        ocr_applied=False,
    )

    reader = FakeReader(document)
    tts = FakeTTS()

    monkeypatch.setattr(
        "audiobook_generator.core.pipeline.merge_mp3",
        fake_merge_mp3,
    )

    config = AudiobookConfig(
        processing=ProcessingConfig(debug_ocr=True),
    )
    pipeline = AudiobookPipeline(
        reader=reader,
        tts=tts,
        config=config,
    )

    asyncio.run(
        pipeline.run(
            Path("libro.txt"),
            tmp_path,
        )
    )

    assert not (tmp_path / "libro_ocr_debug").exists()


def test_pipeline_splits_document_text(
    tmp_path,
    monkeypatch,
):
    document = Document(
        title="Libro",
        source=Path("libro.txt"),
        text=(
            "Capítulo 1\n"
            "Primero.\n\n"
            "Capítulo 2\n"
            "Segundo."
        ),
    )

    reader = FakeReader(document)
    tts = FakeTTS()

    monkeypatch.setattr(
        "audiobook_generator.core.pipeline.merge_mp3",
        fake_merge_mp3,
    )

    pipeline = AudiobookPipeline(
        reader=reader,
        tts=tts,
    )

    result = asyncio.run(
        pipeline.run(
            Path("libro.txt"),
            tmp_path,
        )
    )

    assert len(result.chapter_files) == 2
    assert tts.texts == [
        "Primero.",
        "Segundo.",
    ]


def test_pipeline_keeps_chapters_when_enabled(
    tmp_path,
    monkeypatch,
):
    document = Document(
        title="Libro",
        source=Path("libro.txt"),
        text="Texto de prueba.",
    )

    config = AudiobookConfig(
        processing=ProcessingConfig(
            keep_chapters=True,
        ),
    )

    reader = FakeReader(document)
    tts = FakeTTS()

    monkeypatch.setattr(
        "audiobook_generator.core.pipeline.merge_mp3",
        fake_merge_mp3,
    )

    pipeline = AudiobookPipeline(
        reader=reader,
        tts=tts,
        config=config,
    )

    result = asyncio.run(
        pipeline.run(
            Path("libro.txt"),
            tmp_path,
        )
    )

    assert result.merged_file is not None
    assert all(
        chapter_file.exists()
        for chapter_file in result.chapter_files
    )


def test_pipeline_removes_chapters_when_disabled(
    tmp_path,
    monkeypatch,
):
    document = Document(
        title="Libro",
        source=Path("libro.txt"),
        text="Texto de prueba.",
    )

    config = AudiobookConfig(
        processing=ProcessingConfig(
            keep_chapters=False,
        ),
    )

    reader = FakeReader(document)
    tts = FakeTTS()

    monkeypatch.setattr(
        "audiobook_generator.core.pipeline.merge_mp3",
        fake_merge_mp3,
    )

    pipeline = AudiobookPipeline(
        reader=reader,
        tts=tts,
        config=config,
    )

    result = asyncio.run(
        pipeline.run(
            Path("libro.txt"),
            tmp_path,
        )
    )

    assert result.merged_file is not None
    assert all(
        not chapter_file.exists()
        for chapter_file in result.chapter_files
    )


def test_pipeline_keeps_chapters_when_merge_fails(
    tmp_path,
    monkeypatch,
):
    document = Document(
        title="Libro",
        source=Path("libro.txt"),
        text="Texto de prueba.",
    )

    config = AudiobookConfig(
        processing=ProcessingConfig(
            keep_chapters=False,
        ),
    )

    reader = FakeReader(document)
    tts = FakeTTS()

    monkeypatch.setattr(
        "audiobook_generator.core.pipeline.merge_mp3",
        lambda *args, **kwargs: False,
    )

    pipeline = AudiobookPipeline(
        reader=reader,
        tts=tts,
        config=config,
    )

    result = asyncio.run(
        pipeline.run(
            Path("libro.txt"),
            tmp_path,
        )
    )

    assert result.merged_file is None
    assert all(
        chapter_file.exists()
        for chapter_file in result.chapter_files
    )


def test_pipeline_passes_configured_bitrate_to_ffmpeg(
    tmp_path,
    monkeypatch,
):
    document = Document(
        title="Libro",
        source=Path("libro.txt"),
        text="Texto de prueba.",
    )

    config = AudiobookConfig(
        output=OutputConfig(
            bitrate="96k",
        ),
    )

    reader = FakeReader(document)
    tts = FakeTTS()

    captured = {}

    def fake_merge(
        chapter_files,
        destination,
        bitrate="128k",
        title=None,
        chapter_titles=None,
    ):    
        captured["chapter_files"] = chapter_files
        captured["destination"] = destination
        captured["bitrate"] = bitrate
        captured["chapter_titles"] = chapter_titles

        destination.write_bytes(
            b"fake merged mp3"
        )

        return True

    monkeypatch.setattr(
        "audiobook_generator.core.pipeline.merge_mp3",
        fake_merge,
    )

    pipeline = AudiobookPipeline(
        reader=reader,
        tts=tts,
        config=config,
    )

    result = asyncio.run(
        pipeline.run(
            Path("libro.txt"),
            tmp_path,
        )
    )

    assert result.merged_file is not None
    assert captured["bitrate"] == "96k"
    assert captured["chapter_titles"] == ["Libro"]


def test_pipeline_joins_wrapped_lines(
    tmp_path,
    monkeypatch,
):
    text = (
        "Este es un párrafo que fue\n"
        "partido por el PDF y continúa aquí.\n\n"
        "Este es otro párrafo."
    )

    document = Document(
        title="Libro",
        source=Path("libro.txt"),
        text=text,
    )

    reader = FakeReader(document)
    tts = FakeTTS()

    monkeypatch.setattr(
        "audiobook_generator.core.pipeline.merge_mp3",
        fake_merge_mp3,
    )

    pipeline = AudiobookPipeline(
        reader=reader,
        tts=tts,
    )

    result = asyncio.run(
        pipeline.run(
            Path("libro.txt"),
            tmp_path,
        )
    )

    assert result.merged_file is not None

    assert tts.texts == [
        (
            "Este es un párrafo que fue "
            "partido por el PDF y continúa aquí.\n\n"
            "Este es otro párrafo."
        )
    ]


def test_pipeline_preserves_chapters_when_joining_wrapped_lines(
    tmp_path,
    monkeypatch,
):
    text = (
        "CAPÍTULO 1: La llegada\n"
        "Este es el primer párrafo\n"
        "que continúa en la siguiente línea.\n\n"
        "CAPÍTULO 2: El viaje\n"
        "Este es el segundo capítulo\n"
        "y continúa aquí."
    )

    document = Document(
        title="Libro",
        source=Path("libro.txt"),
        text=text,
    )

    reader = FakeReader(document)
    tts = FakeTTS()

    monkeypatch.setattr(
        "audiobook_generator.core.pipeline.merge_mp3",
        fake_merge_mp3,
    )

    pipeline = AudiobookPipeline(
        reader=reader,
        tts=tts,
    )

    result = asyncio.run(
        pipeline.run(
            Path("libro.txt"),
            tmp_path,
        )
    )

    assert result.merged_file is not None

    assert tts.texts == [
        (
            "Este es el primer párrafo "
            "que continúa en la siguiente línea."
        ),
        (
            "Este es el segundo capítulo "
            "y continúa aquí."
        ),
    ]


def test_pipeline_tags_each_chapter_with_metadata(
    tmp_path,
    monkeypatch,
):
    document = Document(
        title="Libro",
        source=Path("libro.txt"),
        text="Capítulo 1\nPrimero.\n\nCapítulo 2\nSegundo.",
    )

    calls = []

    def fake_tag(path, **kwargs):
        calls.append((path, kwargs))
        return True

    monkeypatch.setattr(
        "audiobook_generator.core.pipeline.tag_mp3",
        fake_tag,
    )
    monkeypatch.setattr(
        "audiobook_generator.core.pipeline.merge_mp3",
        fake_merge_mp3,
    )

    pipeline = AudiobookPipeline(
        reader=FakeReader(document),
        tts=FakeTTS(),
    )

    result = asyncio.run(
        pipeline.run(
            Path("libro.txt"),
            tmp_path,
        )
    )

    assert result.merged_file is not None
    assert [call[1]["title"] for call in calls] == [
        "Capítulo 1",
        "Capítulo 2",
    ]
    assert [call[1]["track_number"] for call in calls] == [1, 2]
    assert all(call[1]["track_total"] == 2 for call in calls)
    assert all(call[1]["album"] == "Libro" for call in calls)

@pytest.mark.asyncio
async def test_pipeline_rejects_empty_document(tmp_path):
    from audiobook_generator.core.errors import EmptyDocumentError
    from audiobook_generator.core.models import Document

    class EmptyReader:
        def read(self, source):
            return Document(
                title="Documento vacío",
                source=source,
                text="",
            )

    class FakeTTS:
        async def synthesize(self, text, destination):
            raise AssertionError(
                "TTS no debería ejecutarse para un documento vacío."
            )

    pipeline = AudiobookPipeline(
        reader=EmptyReader(),
        tts=FakeTTS(),
    )

    source = tmp_path / "vacio.txt"
    source.write_text("", encoding="utf-8")

    with pytest.raises(
        EmptyDocumentError,
        match="no contiene texto utilizable",
    ):
        await pipeline.run(
            source,
            tmp_path / "output",
        )


@pytest.mark.asyncio
async def test_pipeline_rejects_whitespace_only_document(tmp_path):
    from audiobook_generator.core.errors import EmptyDocumentError
    from audiobook_generator.core.models import Document

    class EmptyReader:
        def read(self, source):
            return Document(
                title="Documento vacío",
                source=source,
                text="   \n\n\t  ",
            )

    class FakeTTS:
        async def synthesize(self, text, destination):
            raise AssertionError(
                "TTS no debería ejecutarse para un documento vacío."
            )

    pipeline = AudiobookPipeline(
        reader=EmptyReader(),
        tts=FakeTTS(),
    )

    source = tmp_path / "vacio.txt"
    source.write_text(
        "   \n\n\t  ",
        encoding="utf-8",
    )

    with pytest.raises(
        EmptyDocumentError,
        match="no contiene texto utilizable",
    ):
        await pipeline.run(
            source,
            tmp_path / "output",
        )    


def test_pipeline_cleans_ocr_text_before_tts(
    tmp_path,
    monkeypatch,
):
    document = Document(
        title="Libro",
        source=Path("libro.pdf"),
        text="SENOR FISCAL. LIBERACIÓON definitiva.",
        ocr_applied=True,
    )

    reader = FakeReader(document)
    tts = FakeTTS()

    monkeypatch.setattr(
        "audiobook_generator.core.pipeline.merge_mp3",
        fake_merge_mp3,
    )

    pipeline = AudiobookPipeline(
        reader=reader,
        tts=tts,
    )

    asyncio.run(
        pipeline.run(
            Path("libro.pdf"),
            tmp_path,
        )
    )

    assert tts.texts == [
        "SEÑOR FISCAL. LIBERACIÓN definitiva.",
    ]


def test_pipeline_uses_isolated_temp_directory_per_run(
    tmp_path,
    monkeypatch,
):
    document = Document(
        title="Libro",
        source=Path("libro.txt"),
        text="Texto de prueba.",
    )

    reader = FakeReader(document)
    tts = FakeTTS()

    monkeypatch.setattr(
        "audiobook_generator.core.pipeline.merge_mp3",
        fake_merge_mp3,
    )

    config = AudiobookConfig(
        processing=ProcessingConfig(
            temp_dir=tmp_path / "temp",
            keep_chapters=True,
        ),
    )

    pipeline = AudiobookPipeline(
        reader=reader,
        tts=tts,
        config=config,
    )

    output_a = tmp_path / "output_a"
    output_b = tmp_path / "output_b"

    asyncio.run(pipeline.run(Path("libro.txt"), output_a))
    first_destination = tts.destinations[-1]

    asyncio.run(pipeline.run(Path("libro.txt"), output_b))
    second_destination = tts.destinations[-1]

    assert first_destination.parent != second_destination.parent
    assert first_destination.parent.name.startswith("run-")
    assert second_destination.parent.name.startswith("run-")

@pytest.mark.asyncio
async def test_pipeline_preserves_run_directory_when_tts_fails(
    tmp_path,
    monkeypatch,
):
    document = Document(
        title="Libro",
        source=Path("libro.txt"),
        text="Capítulo 1\nPrimero.\n\nCapítulo 2\nSegundo.",
    )

    class FailingTTS:
        async def synthesize(self, text, destination):
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_bytes(b"partial mp3")
            raise RuntimeError("TTS failure")

    merge_called = False

    def fake_merge(*args, **kwargs):
        nonlocal merge_called
        merge_called = True
        return True

    monkeypatch.setattr(
        "audiobook_generator.core.pipeline.merge_mp3",
        fake_merge,
    )

    config = AudiobookConfig(
        processing=ProcessingConfig(
            temp_dir=tmp_path / "temp",
            keep_chapters=True,
        ),
    )

    pipeline = AudiobookPipeline(
        reader=FakeReader(document),
        tts=FailingTTS(),
        config=config,
    )

    with pytest.raises(RuntimeError, match="TTS failure"):
        await pipeline.run(
            Path("libro.txt"),
            tmp_path / "output",
        )

    run_dirs = list((tmp_path / "temp").glob("run-*"))
    assert len(run_dirs) == 1
    assert list(run_dirs[0].glob("*.mp3"))
    assert not merge_called


@pytest.mark.asyncio
async def test_pipeline_preserves_completed_chapters_when_later_tts_fails(
    tmp_path,
    monkeypatch,
):
    document = Document(
        title="Libro",
        source=Path("libro.txt"),
        text="Capítulo 1\nPrimero.\n\nCapítulo 2\nSegundo.",
    )

    class PartiallyFailingTTS:
        def __init__(self):
            self.calls = 0

        async def synthesize(self, text, destination):
            self.calls += 1
            destination.parent.mkdir(parents=True, exist_ok=True)
            if self.calls == 1:
                destination.write_bytes(b"chapter 1")
                return
            raise RuntimeError("second chapter failed")

    monkeypatch.setattr(
        "audiobook_generator.core.pipeline.merge_mp3",
        lambda *args, **kwargs: pytest.fail(
            "merge_mp3 no debe ejecutarse si falla el TTS"
        ),
    )

    config = AudiobookConfig(
        processing=ProcessingConfig(
            temp_dir=tmp_path / "temp",
            keep_chapters=True,
        ),
    )

    pipeline = AudiobookPipeline(
        reader=FakeReader(document),
        tts=PartiallyFailingTTS(),
        config=config,
    )

    with pytest.raises(RuntimeError, match="second chapter failed"):
        await pipeline.run(
            Path("libro.txt"),
            tmp_path / "output",
        )

    run_dirs = list((tmp_path / "temp").glob("run-*"))
    assert len(run_dirs) == 1
    preserved = sorted(run_dirs[0].glob("*.mp3"))
    assert [path.name for path in preserved] == ["CAPITULO_001.mp3"]
    assert preserved[0].read_bytes() == b"chapter 1"


@pytest.mark.asyncio
async def test_pipeline_continues_when_chapter_tagging_fails(
    tmp_path,
    monkeypatch,
):
    document = Document(
        title="Libro",
        source=Path("libro.txt"),
        text="Texto de prueba.",
    )

    monkeypatch.setattr(
        "audiobook_generator.core.pipeline.tag_mp3",
        lambda *args, **kwargs: False,
    )
    monkeypatch.setattr(
        "audiobook_generator.core.pipeline.merge_mp3",
        fake_merge_mp3,
    )

    pipeline = AudiobookPipeline(
        reader=FakeReader(document),
        tts=FakeTTS(),
    )

    result = await pipeline.run(
        Path("libro.txt"),
        tmp_path / "output",
    )

    assert result.merged_file is not None
    assert result.merged_file.exists()


@pytest.mark.asyncio
async def test_pipeline_keeps_temporary_files_when_merge_raises(
    tmp_path,
    monkeypatch,
):
    document = Document(
        title="Libro",
        source=Path("libro.txt"),
        text="Texto de prueba.",
    )

    monkeypatch.setattr(
        "audiobook_generator.core.pipeline.merge_mp3",
        lambda *args, **kwargs: (_ for _ in ()).throw(
            RuntimeError("merge crashed")
        ),
    )

    config = AudiobookConfig(
        processing=ProcessingConfig(
            temp_dir=tmp_path / "temp",
            keep_chapters=False,
        ),
    )

    pipeline = AudiobookPipeline(
        reader=FakeReader(document),
        tts=FakeTTS(),
        config=config,
    )

    with pytest.raises(RuntimeError, match="merge crashed"):
        await pipeline.run(
            Path("libro.txt"),
            tmp_path / "output",
        )

    run_dirs = list((tmp_path / "temp").glob("run-*"))
    assert len(run_dirs) == 1
    assert list(run_dirs[0].glob("*.mp3"))
    assert not (tmp_path / "output" / "libro_Audiobook.mp3").exists()


def test_pipeline_renumbers_split_fragments_sequentially(
    tmp_path,
    monkeypatch,
):
    document = Document(
        title="Libro",
        source=Path("libro.txt"),
        text=(
            "CAPÍTULO 1\n"
            "Uno.\n\n"
            "CAPÍTULO 2\n"
            "Dos."
        ),
    )

    tts = FakeTTS()
    monkeypatch.setattr(
        "audiobook_generator.core.pipeline.merge_mp3",
        fake_merge_mp3,
    )

    config = AudiobookConfig(
        processing=ProcessingConfig(max_characters=5),
    )

    result = asyncio.run(
        AudiobookPipeline(
            reader=FakeReader(document),
            tts=tts,
            config=config,
        ).run(
            Path("libro.txt"),
            tmp_path / "output",
        )
    )

    assert [path.name for path in result.chapter_files] == [
        "CAPITULO_001.mp3",
        "CAPITULO_002.mp3",
    ]
    assert len(tts.texts) == 2
