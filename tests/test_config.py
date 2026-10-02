from pathlib import Path

from audiobook_generator.core.config import (
    AudiobookConfig,
    ProcessingConfig,
    TTSConfig,
    OcrConfig,
)


def test_default_tts_config():
    config = TTSConfig()

    assert config.voice == "Sofía"
    assert config.rate == "+0%"
    assert config.volume == "+0%"
    assert config.pitch == "+0Hz"


def test_default_processing_config():
    config = ProcessingConfig()

    assert config.max_characters == 1500
    assert config.temp_dir == Path("temp")
    assert config.keep_chapters is True
    assert config.debug_ocr is False


def test_audiobook_config_contains_defaults():
    config = AudiobookConfig()

    assert config.tts.voice == "Sofía"
    assert config.output.format == "mp3"
    assert config.output.bitrate == "192k"


def test_default_ocr_config():
    config = OcrConfig()

    assert config.mode == "auto"
    assert config.language == "spa"
    assert config.dpi == 300
    assert config.psm == 3


def test_audiobook_config_contains_default_ocr_config():
    config = AudiobookConfig()

    assert config.ocr.mode == "auto"
    assert config.ocr.language == "spa"
    assert config.ocr.dpi == 300
    assert config.ocr.psm == 3
