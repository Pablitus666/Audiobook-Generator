from pathlib import Path
from types import SimpleNamespace
import queue

from audiobook_generator.core.models import AudiobookResult
from audiobook_generator.gui import main_window


class _FakeReader:
    pass


class _FakePipeline:
    captured = None

    def __init__(self, reader, tts, config):
        self.reader = reader
        self.tts = tts
        self.config = config
        _FakePipeline.captured = self

    async def run(self, source, output_dir, progress_callback=None):
        assert source == Path("libro.txt")
        assert output_dir == Path("salida")
        assert progress_callback is not None
        progress_callback(25.0, "status.generating")
        return AudiobookResult(
            chapter_files=[],
            merged_file=output_dir / "libro_Audiobook.mp3",
        )


def test_gui_worker_builds_pipeline_from_gui_configuration(monkeypatch):
    source = Path("libro.txt")
    output = Path("salida")
    source.touch()

    monkeypatch.setattr(main_window.ReaderFactory, "create", lambda path: _FakeReader())
    monkeypatch.setattr(main_window, "AudiobookPipeline", _FakePipeline)

    events = queue.Queue()
    app = SimpleNamespace(_generation_queue=events)

    from audiobook_generator.core.config import AudiobookConfig, OcrConfig, OutputConfig, ProcessingConfig, TTSConfig

    config = AudiobookConfig(
        tts=TTSConfig(voice="es-BO-SofiaNeural", rate="+10%", volume="-10%", pitch="+2Hz"),
        output=OutputConfig(bitrate="192k"),
        processing=ProcessingConfig(max_characters=1200, temp_dir=output / ".temp", keep_chapters=False),
        ocr=OcrConfig(),
    )

    main_window.MainWindow._generation_worker(app, source, output, config)

    first = events.get_nowait()
    second = events.get_nowait()

    assert first[0] == "progress"
    assert first[1:] == (25.0, "status.generating")
    assert second[0] == "success"

    pipeline = _FakePipeline.captured
    assert pipeline is not None
    assert pipeline.config.tts.voice == "es-BO-SofiaNeural"
    assert pipeline.config.tts.rate == "+10%"
    assert pipeline.config.tts.volume == "-10%"
    assert pipeline.config.tts.pitch == "+2Hz"
    assert pipeline.config.processing.max_characters == 1200
    assert pipeline.config.processing.keep_chapters is False
