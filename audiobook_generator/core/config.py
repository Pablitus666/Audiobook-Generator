from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class TTSConfig:
    voice: str = "Sofía"
    rate: str = "+0%"
    volume: str = "+0%"
    pitch: str = "+0Hz"


@dataclass(frozen=True)
class OutputConfig:
    format: str = "mp3"
    bitrate: str = "192k"


@dataclass(frozen=True)
class ProcessingConfig:
    max_characters: int = 1500
    temp_dir: Path = Path("temp")
    keep_chapters: bool = True
    debug_ocr: bool = False


@dataclass(frozen=True)
class OcrConfig:
    mode: str = "auto"
    language: str = "spa"
    dpi: int = 300
    psm: int = 3


@dataclass(frozen=True)
class AudiobookConfig:
    tts: TTSConfig = TTSConfig()
    output: OutputConfig = OutputConfig()
    processing: ProcessingConfig = ProcessingConfig()
    ocr: OcrConfig = OcrConfig()
