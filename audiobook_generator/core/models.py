from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path


@dataclass(frozen=True)
class Chapter:
    number: int
    title: str
    text: str


@dataclass(frozen=True)
class Document:
    title: str
    source: Path
    text: str = ""
    chapters: list[Chapter] = field(default_factory=list)
    ocr_applied: bool = False


@dataclass(frozen=True)
class AudiobookResult:
    chapter_files: list[Path]
    merged_file: Path | None
