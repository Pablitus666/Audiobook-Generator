import asyncio
from pathlib import Path

from audiobook_generator.core.config import AudiobookConfig, ProcessingConfig
from audiobook_generator.core.models import Document
from audiobook_generator.core.pipeline import AudiobookPipeline


class FakeReader:
    def __init__(self, document):
        self.document = document

    def read(self, source):
        return self.document


class FakeTTS:
    async def synthesize(self, text, destination):
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(b"fake mp3")


def build_pipeline(
    tmp_path,
    monkeypatch,
    *,
    keep_chapters=True,
    merge_result=True,
):
    document = Document(
        title="MiLibro",
        source=Path("libro.txt"),
        text="Texto de prueba para integración.",
    )

    config = AudiobookConfig(
        processing=ProcessingConfig(
            temp_dir=tmp_path / "temp",
            keep_chapters=keep_chapters,
        ),
    )

    def fake_merge(
        files,
        destination,
        bitrate="192k",
        title=None,
        chapter_titles=None,
    ):
        if not merge_result:
            return False

        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(b"merged mp3")
        return True

    monkeypatch.setattr(
        "audiobook_generator.core.pipeline.merge_mp3",
        fake_merge,
    )

    return AudiobookPipeline(
        reader=FakeReader(document),
        tts=FakeTTS(),
        config=config,
    )


def test_integration_keep_chapters_moves_files_to_output(
    tmp_path,
    monkeypatch,
):
    pipeline = build_pipeline(
        tmp_path,
        monkeypatch,
        keep_chapters=True,
    )

    output_dir = tmp_path / "output"

    result = asyncio.run(
        pipeline.run(
            Path("libro.txt"),
            output_dir,
        )
    )

    temp_dir = tmp_path / "temp" / "MiLibro"
    chapters_dir = output_dir / "chapters"

    assert result.merged_file is not None
    assert result.merged_file.exists()
    assert result.merged_file == output_dir / "libro_Audiobook.mp3"

    assert not temp_dir.exists()
    assert chapters_dir.exists()
    assert result.chapter_files
    assert all(path.exists() for path in result.chapter_files)
    assert all(
        path.parent == chapters_dir
        for path in result.chapter_files
    )


def test_integration_no_keep_chapters_removes_temp_files(
    tmp_path,
    monkeypatch,
):
    pipeline = build_pipeline(
        tmp_path,
        monkeypatch,
        keep_chapters=False,
    )

    output_dir = tmp_path / "output"

    result = asyncio.run(
        pipeline.run(
            Path("libro.txt"),
            output_dir,
        )
    )

    temp_dir = tmp_path / "temp" / "MiLibro"
    chapters_dir = output_dir / "chapters"

    assert result.merged_file is not None
    assert result.merged_file.exists()
    assert not temp_dir.exists()
    assert not chapters_dir.exists()


def test_integration_merge_failure_preserves_temp_files(
    tmp_path,
    monkeypatch,
):
    pipeline = build_pipeline(
        tmp_path,
        monkeypatch,
        keep_chapters=True,
        merge_result=False,
    )

    output_dir = tmp_path / "output"

    result = asyncio.run(
        pipeline.run(
            Path("libro.txt"),
            output_dir,
        )
    )

    temp_dir = tmp_path / "temp" / "MiLibro"

    assert result.merged_file is None
    assert temp_dir.exists()

    temporary_chapters = list(temp_dir.glob("*.mp3"))

    assert temporary_chapters
    assert all(path.exists() for path in temporary_chapters)
    assert not (output_dir / "libro_Audiobook.mp3").exists()
