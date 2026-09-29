from __future__ import annotations

import shutil
import uuid
from pathlib import Path

from ..audio.ffmpeg import merge_mp3, tag_mp3
from ..core.config import AudiobookConfig
from ..core.errors import EmptyDocumentError
from ..core.models import AudiobookResult, Chapter
from ..readers.base import DocumentReader
from ..tts.base import TTSEngine
from .preprocessor import (
    join_wrapped_lines,
    normalize_ocr_text,
    normalize_text,
)
from .splitter import split_text


class AudiobookPipeline:
    def __init__(
        self,
        reader: DocumentReader,
        tts: TTSEngine,
        config: AudiobookConfig | None = None,
    ) -> None:
        self.reader = reader
        self.tts = tts
        self.config = config or AudiobookConfig()

    async def run(
        self,
        source: Path,
        output_dir: Path,
    ) -> AudiobookResult:
        output_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

        document = self.reader.read(source)

        if document.text:
            original_text = document.text

            if document.ocr_applied:
                text = normalize_ocr_text(original_text)

                if self.config.processing.debug_ocr:
                    debug_dir = output_dir / f"{source.stem}_ocr_debug"
                    debug_dir.mkdir(parents=True, exist_ok=True)
                    (debug_dir / "original_ocr.txt").write_text(
                        original_text,
                        encoding="utf-8",
                    )
                    (debug_dir / "cleaned_ocr.txt").write_text(
                        text,
                        encoding="utf-8",
                    )
            else:
                text = normalize_text(original_text)

            if not text:
                raise EmptyDocumentError(
                    "el documento no contiene texto utilizable."
                )

            chapters = split_text(
                text,
                default_title=document.title,
                max_characters=self.config.processing.max_characters,
            )
        else:
            chapters = list(document.chapters)

        if not chapters:
            raise EmptyDocumentError(
                "el documento no contiene texto utilizable."
            )

        processed_chapters: list[Chapter] = []

        for chapter in chapters:
            text = join_wrapped_lines(chapter.text)

            if not text:
                continue

            parts = split_text(
                text,
                default_title=chapter.title,
                max_characters=self.config.processing.max_characters,
            )

            for part in parts:
                if not part.text.strip():
                    continue

                processed_chapters.append(
                    Chapter(
                        number=len(processed_chapters) + 1,
                        title=(
                            chapter.title
                            if len(parts) == 1
                            else part.title
                        ),
                        text=part.text,
                    )
                )

        chapters = processed_chapters

        if not chapters:
            raise EmptyDocumentError(
                "el documento no contiene texto utilizable."
            )

        temp_root = Path(self.config.processing.temp_dir)
        temp_root.mkdir(parents=True, exist_ok=True)
        # Cada ejecución obtiene su propio directorio temporal para evitar
        # colisiones entre conversiones concurrentes del mismo documento.
        temp_book_dir = temp_root / f"run-{uuid.uuid4().hex}"
        temp_book_dir.mkdir(parents=True, exist_ok=False)

        chapter_files: list[Path] = []

        for chapter in chapters:
            destination = (
                temp_book_dir
                / f"CAPITULO_{chapter.number:03d}.mp3"
            )

            print(
                f"[{chapter.number}/{len(chapters)}] "
                f"Generando: {chapter.title}"
            )

            await self.tts.synthesize(
                chapter.text,
                destination,
            )

            # Los metadatos son una mejora de presentación; si FFmpeg no
            # puede escribirlos, conservamos igualmente el audio generado.
            tag_mp3(
                destination,
                title=chapter.title,
                album=document.title,
                track_number=chapter.number,
                track_total=len(chapters),
            )

            chapter_files.append(destination)

        merged = output_dir / f"{source.stem}_Audiobook.mp3"

        if not merge_mp3(
            chapter_files,
            merged,
            bitrate=self.config.output.bitrate,
            title=document.title,
            chapter_titles=[chapter.title for chapter in chapters],
        ):
            return AudiobookResult(
                chapter_files=chapter_files,
                merged_file=None,
            )

        if self.config.processing.keep_chapters:
            chapters_output_dir = output_dir / "chapters"
            chapters_output_dir.mkdir(
                parents=True,
                exist_ok=True,
            )

            output_chapter_files: list[Path] = []

            for chapter_file in chapter_files:
                destination = (
                    chapters_output_dir
                    / chapter_file.name
                )

                shutil.move(
                    str(chapter_file),
                    str(destination),
                )

                output_chapter_files.append(destination)

            shutil.rmtree(
                temp_book_dir,
                ignore_errors=True,
            )

            return AudiobookResult(
                chapter_files=output_chapter_files,
                merged_file=merged,
            )

        shutil.rmtree(
            temp_book_dir,
            ignore_errors=True,
        )

        return AudiobookResult(
            chapter_files=chapter_files,
            merged_file=merged,
        )
