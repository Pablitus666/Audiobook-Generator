from pathlib import Path

from audiobook_generator.audio import ffmpeg


def test_merge_returns_false_without_ffmpeg(monkeypatch, tmp_path: Path):
    monkeypatch.setattr(ffmpeg.shutil, "which", lambda _: None)

    result = ffmpeg.merge_mp3(
        [tmp_path / "chapter.mp3"],
        tmp_path / "book.mp3",
    )

    assert result is False


def test_merge_returns_false_without_files(monkeypatch, tmp_path: Path):
    monkeypatch.setattr(
        ffmpeg.shutil,
        "which",
        lambda _: "ffmpeg.exe",
    )

    result = ffmpeg.merge_mp3(
        [],
        tmp_path / "book.mp3",
    )

    assert result is False


def test_concat_line_uses_absolute_forward_slashes(tmp_path: Path):
    source = tmp_path / "chapter one.mp3"
    line = ffmpeg._concat_line(source)

    assert line.startswith("file '")
    assert line.endswith("'")
    assert source.resolve().as_posix() in line


def test_merge_passes_bitrate_to_ffmpeg(monkeypatch, tmp_path: Path):
    calls = []

    monkeypatch.setattr(
        ffmpeg.shutil,
        "which",
        lambda _: "ffmpeg.exe",
    )

    def fake_run(command, check):
        calls.append(command)

    monkeypatch.setattr(
        ffmpeg.subprocess,
        "run",
        fake_run,
    )

    chapter = tmp_path / "chapter.mp3"
    chapter.write_bytes(b"fake")

    destination = tmp_path / "book.mp3"

    monkeypatch.setattr(
        Path,
        "is_file",
        lambda self: self == destination,
    )

    result = ffmpeg.merge_mp3(
        [chapter],
        destination,
        bitrate="128k",
    )

    assert result is True
    assert len(calls) == 1
    assert "-b:a" in calls[0]
    assert "128k" in calls[0]


def test_merge_returns_false_when_ffmpeg_fails(
    monkeypatch,
    tmp_path: Path,
):
    monkeypatch.setattr(
        ffmpeg.shutil,
        "which",
        lambda _: "ffmpeg.exe",
    )

    def failing_run(command, check):
        raise ffmpeg.subprocess.CalledProcessError(
            returncode=1,
            cmd=command,
        )

    monkeypatch.setattr(
        ffmpeg.subprocess,
        "run",
        failing_run,
    )

    chapter = tmp_path / "chapter.mp3"
    chapter.write_bytes(b"fake mp3")

    destination = tmp_path / "book.mp3"

    result = ffmpeg.merge_mp3(
        [chapter],
        destination,
    )

    assert result is False
    assert not destination.exists()


def test_merge_removes_concat_file_after_success(
    monkeypatch,
    tmp_path: Path,
):
    monkeypatch.setattr(
        ffmpeg.shutil,
        "which",
        lambda _: "ffmpeg.exe",
    )

    chapter = tmp_path / "chapter.mp3"
    chapter.write_bytes(b"fake mp3")

    destination = tmp_path / "book.mp3"

    def fake_run(command, check):
        destination.write_bytes(b"fake audiobook")

    monkeypatch.setattr(
        ffmpeg.subprocess,
        "run",
        fake_run,
    )

    result = ffmpeg.merge_mp3(
        [chapter],
        destination,
    )

    concat_file = destination.with_suffix(".concat.txt")

    assert result is True
    assert destination.exists()
    assert not concat_file.exists()


def test_merge_removes_concat_file_after_failure(
    monkeypatch,
    tmp_path: Path,
):
    monkeypatch.setattr(
        ffmpeg.shutil,
        "which",
        lambda _: "ffmpeg.exe",
    )

    chapter = tmp_path / "chapter.mp3"
    chapter.write_bytes(b"fake mp3")

    destination = tmp_path / "book.mp3"

    def failing_run(command, check):
        raise OSError("fallo de prueba")

    monkeypatch.setattr(
        ffmpeg.subprocess,
        "run",
        failing_run,
    )

    result = ffmpeg.merge_mp3(
        [chapter],
        destination,
    )

    concat_file = destination.with_suffix(".concat.txt")

    assert result is False
    assert not concat_file.exists()