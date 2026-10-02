import asyncio
from pathlib import Path

from audiobook_generator.core.config import (
    AudiobookConfig,
    ProcessingConfig,
)
from audiobook_generator.core.models import Chapter, Document
from audiobook_generator.core.pipeline import AudiobookPipeline


class FakeReader:
    def __init__(self, document):
        self.document = document

    def read(self, source):
        return self.document


class FakeTTS:
    async def synthesize(self, text, destination):
        destination.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        destination.write_bytes(b"fake mp3")


def test_keep_chapters_true_moves_chapter_files_to_output(
    tmp_path,
    monkeypatch,
):
    document = Document(
        title="MiLibro",
        source=Path("libro.txt"),
        text="Texto de prueba.",
    )

    temp_dir = tmp_path / "temp"

    config = AudiobookConfig(
        processing=ProcessingConfig(
            temp_dir=temp_dir,
            keep_chapters=True,
        ),
    )

    reader = FakeReader(document)
    tts = FakeTTS()

    def fake_merge(
        files,
        destination,
        bitrate="192k",
        title=None,
        chapter_titles=None,
    ):
        assert all(
            file.parent == temp_dir / "MiLibro"
            for file in files
        )

        destination.write_bytes(b"merged-mp3")
        return True

    monkeypatch.setattr(
        "audiobook_generator.core.pipeline.merge_mp3",
        fake_merge,
    )

    output_dir = tmp_path / "output"

    pipeline = AudiobookPipeline(
        reader=reader,
        tts=tts,
        config=config,
    )

    result = asyncio.run(
        pipeline.run(
            Path("libro.txt"),
            output_dir,
        )
    )

    assert result.merged_file is not None
    assert result.merged_file.exists()

    assert result.chapter_files
    assert all(
        chapter_file.parent == output_dir / "chapters"
        for chapter_file in result.chapter_files
    )
    assert all(
        chapter_file.exists()
        for chapter_file in result.chapter_files
    )

    assert not (temp_dir / "MiLibro").exists()


def test_keep_chapters_false_removes_temporary_files(
    tmp_path,
    monkeypatch,
):
    document = Document(
        title="MiLibro",
        source=Path("libro.txt"),
        text="Texto de prueba.",
    )

    temp_dir = tmp_path / "temp"

    config = AudiobookConfig(
        processing=ProcessingConfig(
            temp_dir=temp_dir,
            keep_chapters=False,
        ),
    )

    reader = FakeReader(document)
    tts = FakeTTS()

    def fake_merge(
        files,
        destination,
        bitrate="192k",
        title=None,
        chapter_titles=None,
    ):
        assert all(
            file.parent == temp_dir / "MiLibro"
            for file in files
        )

        destination.write_bytes(b"merged-mp3")
        return True

    monkeypatch.setattr(
        "audiobook_generator.core.pipeline.merge_mp3",
        fake_merge,
    )

    output_dir = tmp_path / "output"

    pipeline = AudiobookPipeline(
        reader=reader,
        tts=tts,
        config=config,
    )

    result = asyncio.run(
        pipeline.run(
            Path("libro.txt"),
            output_dir,
        )
    )

    assert result.merged_file is not None
    assert result.merged_file.exists()

    assert result.chapter_files
    assert all(
        not chapter_file.exists()
        for chapter_file in result.chapter_files
    )

    assert not (temp_dir / "MiLibro").exists()
    assert not (output_dir / "chapters").exists()


def test_keep_chapters_true_preserves_temporary_files_when_merge_fails(
    tmp_path,
    monkeypatch,
):
    document = Document(
        title="MiLibro",
        source=Path("libro.txt"),
        text="Texto de prueba.",
    )

    temp_dir = tmp_path / "temp"

    config = AudiobookConfig(
        processing=ProcessingConfig(
            temp_dir=temp_dir,
            keep_chapters=True,
        ),
    )

    reader = FakeReader(document)
    tts = FakeTTS()

    monkeypatch.setattr(
        "audiobook_generator.core.pipeline.merge_mp3",
        lambda files, destination, bitrate="192k", title=None, chapter_titles=None: False,
    )

    output_dir = tmp_path / "output"

    pipeline = AudiobookPipeline(
        reader=reader,
        tts=tts,
        config=config,
    )

    result = asyncio.run(
        pipeline.run(
            Path("libro.txt"),
            output_dir,
        )
    )

    assert result.merged_file is None

    assert result.chapter_files
    assert all(
        chapter_file.exists()
        for chapter_file in result.chapter_files
    )

    assert (temp_dir / "MiLibro").exists()
    assert not (output_dir / "chapters").exists()


def test_keep_chapters_false_preserves_temporary_files_when_merge_fails(
    tmp_path,
    monkeypatch,
):
    document = Document(
        title="MiLibro",
        source=Path("libro.txt"),
        text="Texto de prueba.",
    )

    temp_dir = tmp_path / "temp"

    config = AudiobookConfig(
        processing=ProcessingConfig(
            temp_dir=temp_dir,
            keep_chapters=False,
        ),
    )

    reader = FakeReader(document)
    tts = FakeTTS()

    monkeypatch.setattr(
        "audiobook_generator.core.pipeline.merge_mp3",
        lambda files, destination, bitrate="192k", title=None, chapter_titles=None: False,
    )

    output_dir = tmp_path / "output"

    pipeline = AudiobookPipeline(
        reader=reader,
        tts=tts,
        config=config,
    )

    result = asyncio.run(
        pipeline.run(
            Path("libro.txt"),
            output_dir,
        )
    )

    assert result.merged_file is None

    assert result.chapter_files
    assert all(
        chapter_file.exists()
        for chapter_file in result.chapter_files
    )

    assert (temp_dir / "MiLibro").exists()
    assert not (output_dir / "chapters").exists()


def test_pipeline_passes_title_to_merge(
    tmp_path,
    monkeypatch,
):
    document = Document(
        title="Mi Libro",
        source=Path("libro.txt"),
        text="Texto de prueba.",
    )

    temp_dir = tmp_path / "temp"

    config = AudiobookConfig(
        processing=ProcessingConfig(
            temp_dir=temp_dir,
        ),
    )

    reader = FakeReader(document)
    tts = FakeTTS()

    captured = {}

    def fake_merge(
        files,
        destination,
        bitrate="192k",
        title=None,
        chapter_titles=None,
    ):
        captured["files"] = files
        captured["destination"] = destination
        captured["bitrate"] = bitrate
        captured["title"] = title

        destination.write_bytes(b"merged-mp3")

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

    asyncio.run(
        pipeline.run(
            Path("libro.txt"),
            tmp_path / "output",
        )
    )

    assert captured["title"] == "Mi Libro"


def test_pipeline_uses_configured_temp_dir(
    tmp_path,
    monkeypatch,
):
    document = Document(
        title="MiLibro",
        source=Path("libro.txt"),
        text="Texto de prueba.",
    )

    temp_dir = tmp_path / "custom-temp"

    config = AudiobookConfig(
        processing=ProcessingConfig(
            temp_dir=temp_dir,
            keep_chapters=True,
        ),
    )

    reader = FakeReader(document)
    tts = FakeTTS()
    captured = {}

    def fake_merge(
        files,
        destination,
        bitrate="192k",
        title=None,
        chapter_titles=None,
    ):
        captured["files"] = files
        destination.write_bytes(b"merged-mp3")
        return True

    monkeypatch.setattr(
        "audiobook_generator.core.pipeline.merge_mp3",
        fake_merge,
    )

    asyncio.run(
        AudiobookPipeline(
            reader=reader,
            tts=tts,
            config=config,
        ).run(
            Path("libro.txt"),
            tmp_path / "output",
        )
    )

    assert captured["files"]
    assert all(
        file.parent == temp_dir / "MiLibro"
        for file in captured["files"]
    )


def test_pipeline_does_not_invent_chapter_title_in_tts(
    tmp_path,
    monkeypatch,
):
    """El título estructural nunca se añade artificialmente al texto narrado."""
    document = Document(
        title="MiLibro",
        source=Path("libro.epub"),
        chapters=[
            # El lector conoce el título como metadata, pero el texto real
            # empieza directamente con el contenido.
            Chapter(
                number=1,
                title="Capítulo 1",
                text="Resumen real del capítulo.",
            ),
        ],
    )

    config = AudiobookConfig(
        processing=ProcessingConfig(
            temp_dir=tmp_path / "temp",
            keep_chapters=True,
        ),
    )

    reader = FakeReader(document)
    captured = []

    class CapturingTTS(FakeTTS):
        async def synthesize(self, text, destination):
            captured.append(text)
            await super().synthesize(text, destination)

    def fake_merge(
        files,
        destination,
        bitrate="192k",
        title=None,
        chapter_titles=None,
    ):
        destination.write_bytes(b"merged-mp3")
        return True

    monkeypatch.setattr(
        "audiobook_generator.core.pipeline.merge_mp3",
        fake_merge,
    )

    asyncio.run(
        AudiobookPipeline(
            reader=reader,
            tts=CapturingTTS(),
            config=config,
        ).run(
            Path("libro.epub"),
            tmp_path / "output",
        )
    )

    assert captured == ["Resumen real del capítulo."]
