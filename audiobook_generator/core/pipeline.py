from __future__ import annotations

import shutil
from pathlib import Path
from collections.abc import Callable

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
from .splitter import _split_long_text, split_text


ProgressCallback = Callable[[float, str], None]


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
        progress_callback: ProgressCallback | None = None,
    ) -> AudiobookResult:
        """Generate the audiobook and optionally report UI progress.

        ``progress_callback`` is deliberately optional so the pipeline keeps
        the same API for the CLI and existing callers. Callback failures are
        ignored: a GUI/status update must never be able to break generation.
        """
        def report(progress: float, status_key: str) -> None:
            if progress_callback is None:
                return
            try:
                progress_callback(max(0.0, min(100.0, progress)), status_key)
            except Exception:
                pass

        report(0.0, "status.loading")
        output_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

        document = self.reader.read(source)
        report(5.0, "status.loading")

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

            # ``chapter.text`` es la única fuente de verdad para el texto
            # que se entrega al TTS. ``chapter.title`` es metadata para
            # nombres de archivo, consola y etiquetas MP3.
            #
            # Es importante NO anteponer ``chapter.title`` aquí: algunos
            # lectores generan un título estructural a partir del nombre
            # interno del recurso (por ejemplo, EPUB) y ese valor puede no
            # existir realmente en el documento. Si lo añadimos, el audio
            # termina pronunciando contenido que el usuario nunca escribió.
            title = chapter.title.strip()

            parts = (
                _split_long_text(
                    text,
                    self.config.processing.max_characters,
                )
                if self.config.processing.max_characters is not None
                else [text]
            )

            for part_index, part in enumerate(parts, start=1):
                if not part.strip():
                    continue

                part_title = title
                if len(parts) > 1:
                    part_title = f"{title} - Parte {part_index}"

                processed_chapters.append(
                    Chapter(
                        number=len(processed_chapters) + 1,
                        title=part_title,
                        text=part,
                    )
                )

        chapters = processed_chapters

        if not chapters:
            raise EmptyDocumentError(
                "el documento no contiene texto utilizable."
            )

        report(10.0, "status.generating")

        temp_root = Path(self.config.processing.temp_dir)
        temp_book_dir = temp_root / document.title

        temp_book_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

        chapter_files: list[Path] = []

        total_chapters = len(chapters)

        for chapter_index, chapter in enumerate(chapters, start=1):
            progress_before = 10.0 + ((chapter_index - 1) / total_chapters) * 80.0
            report(progress_before, "status.generating")
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
            progress_after = 10.0 + (chapter_index / total_chapters) * 80.0
            report(progress_after, "status.generating")

        report(95.0, "status.generating")
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

            report(100.0, "status.finished")
            return AudiobookResult(
                chapter_files=output_chapter_files,
                merged_file=merged,
            )

        shutil.rmtree(
            temp_book_dir,
            ignore_errors=True,
        )

        report(100.0, "status.finished")
        return AudiobookResult(
            chapter_files=chapter_files,
            merged_file=merged,
        )
