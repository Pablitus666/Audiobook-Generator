from __future__ import annotations

import shutil
import subprocess
from pathlib import Path


def _concat_line(path: Path) -> str:
    """Create one FFmpeg concat-demuxer file entry."""
    normalized = path.resolve().as_posix()
    escaped = normalized.replace("'", "'\\''")
    return f"file '{escaped}'"


def _escape_ffmetadata(value: str) -> str:
    """Escape a value for FFmpeg's ffmetadata format."""
    return (
        value
        .replace("\\", "\\\\")
        .replace("=", "\\=")
        .replace(";", "\\;")
        .replace("#", "\\#")
        .replace("\n", "\\n")
        .replace("\r", "\\r")
    )


def _probe_duration_ms(
    ffprobe: str,
    path: Path,
) -> int | None:
    """Return an audio file duration in milliseconds when available."""
    try:
        result = subprocess.run(
            [
                ffprobe,
                "-v",
                "error",
                "-show_entries",
                "format=duration",
                "-of",
                "default=noprint_wrappers=1:nokey=1",
                str(path),
            ],
            check=True,
            capture_output=True,
            text=True,
        )
        seconds = float(result.stdout.strip())
    except (
        OSError,
        ValueError,
        subprocess.CalledProcessError,
    ):
        return None

    if seconds <= 0:
        return None

    return max(1, round(seconds * 1000))


def _write_chapter_metadata(
    path: Path,
    title: str | None,
    chapter_titles: list[str],
    durations_ms: list[int],
) -> None:
    """Write an FFmetadata file containing global and chapter metadata."""
    lines = [";FFMETADATA1"]

    if title:
        escaped_title = _escape_ffmetadata(title)
        lines.extend(
            [
                f"title={escaped_title}",
                f"album={escaped_title}",
            ]
        )

    start = 0

    for chapter_title, duration_ms in zip(
        chapter_titles,
        durations_ms,
    ):
        end = start + duration_ms
        lines.extend(
            [
                "",
                "[CHAPTER]",
                "TIMEBASE=1/1000",
                f"START={start}",
                f"END={end}",
                f"title={_escape_ffmetadata(chapter_title)}",
            ]
        )
        start = end

    path.write_text(
        "\n".join(lines) + "\n",
        encoding="utf-8",
    )


def tag_mp3(
    path: Path,
    *,
    title: str,
    album: str,
    track_number: int,
    track_total: int,
) -> bool:
    """Add ID3 metadata to an MP3 without re-encoding its audio."""
    ffmpeg = shutil.which("ffmpeg")

    if not ffmpeg or not path.is_file():
        return False

    temporary = path.with_name(
        f"{path.stem}.metadata.tmp.mp3"
    )

    command = [
        ffmpeg,
        "-hide_banner",
        "-loglevel",
        "error",
        "-i",
        str(path),
        "-map",
        "0:a",
        "-c:a",
        "copy",
        "-id3v2_version",
        "3",
        "-metadata",
        f"title={title}",
        "-metadata",
        f"album={album}",
        "-metadata",
        f"track={track_number}/{track_total}",
        "-y",
        str(temporary),
    ]

    try:
        subprocess.run(
            command,
            check=True,
        )
        temporary.replace(path)
        return True
    except (OSError, subprocess.CalledProcessError):
        return False
    finally:
        temporary.unlink(missing_ok=True)


def merge_mp3(
    files: list[Path],
    destination: Path,
    bitrate: str = "192k",
    title: str | None = None,
    chapter_titles: list[str] | None = None,
) -> bool:
    """Merge MP3 files with FFmpeg and optional chapter metadata.

    Returns True when the final file was created successfully.
    Returns False when FFmpeg is not available or merging fails.

    When ``chapter_titles`` is supplied and ``ffprobe`` can read all source
    durations, the resulting MP3 also contains navigable chapter markers.
    """
    ffmpeg = shutil.which("ffmpeg")

    if not ffmpeg or not files:
        return False

    destination.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    list_file = destination.with_suffix(".concat.txt")
    metadata_file = destination.with_suffix(".ffmeta")

    try:
        lines = [
            _concat_line(path)
            for path in files
        ]

        list_file.write_text(
            "\n".join(lines),
            encoding="utf-8",
        )

        command = [
            ffmpeg,
            "-hide_banner",
            "-loglevel",
            "error",
            "-f",
            "concat",
            "-safe",
            "0",
            "-i",
            str(list_file),
        ]

        use_chapter_metadata = (
            chapter_titles is not None
            and len(chapter_titles) == len(files)
        )

        ffprobe = shutil.which("ffprobe") if use_chapter_metadata else None
        durations_ms: list[int] = []

        if ffprobe:
            for file in files:
                duration_ms = _probe_duration_ms(ffprobe, file)

                if duration_ms is None:
                    durations_ms = []
                    break

                durations_ms.append(duration_ms)

        if use_chapter_metadata and len(durations_ms) == len(files):
            _write_chapter_metadata(
                metadata_file,
                title,
                chapter_titles or [],
                durations_ms,
            )
            command.extend(
                [
                    "-f",
                    "ffmetadata",
                    "-i",
                    str(metadata_file),
                ]
            )

        command.extend(
            [
                "-map",
                "0:a",
                "-c:a",
                "libmp3lame",
                "-b:a",
                bitrate,
            ]
        )

        if use_chapter_metadata and len(durations_ms) == len(files):
            command.extend(
                [
                    "-map_metadata",
                    "1",
                ]
            )
        elif title:
            command.extend(
                [
                    "-metadata",
                    f"title={title}",
                    "-metadata",
                    f"album={title}",
                ]
            )

        command.extend(
            [
                "-y",
                str(destination),
            ]
        )

        subprocess.run(
            command,
            check=True,
        )

        return destination.is_file()

    except (
        OSError,
        subprocess.CalledProcessError,
    ):
        return False

    finally:
        list_file.unlink(
            missing_ok=True
        )
        metadata_file.unlink(
            missing_ok=True
        )
