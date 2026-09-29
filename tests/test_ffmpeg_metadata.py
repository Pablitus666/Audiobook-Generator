from pathlib import Path

from audiobook_generator.audio.ffmpeg import merge_mp3


def test_merge_mp3_passes_title_metadata(
    tmp_path,
    monkeypatch,
):
    chapter = tmp_path / "chapter.mp3"
    destination = tmp_path / "audiobook.mp3"

    chapter.write_bytes(b"fake mp3")

    captured = {}

    monkeypatch.setattr(
        "audiobook_generator.audio.ffmpeg.shutil.which",
        lambda name: "ffmpeg.exe",
    )

    def fake_run(command, check):
        captured["command"] = command
        captured["check"] = check

        destination.write_bytes(
            b"fake audiobook"
        )

    monkeypatch.setattr(
        "audiobook_generator.audio.ffmpeg.subprocess.run",
        fake_run,
    )

    result = merge_mp3(
        [chapter],
        destination,
        bitrate="192k",
        title="Mi Audiolibro",
    )

    assert result is True
    assert destination.exists()

    command = captured["command"]

    assert "-metadata" in command
    assert "title=Mi Audiolibro" in command
    assert "album=Mi Audiolibro" in command

def test_merge_mp3_writes_chapter_metadata(
    tmp_path,
    monkeypatch,
):
    chapters = [
        tmp_path / "chapter1.mp3",
        tmp_path / "chapter2.mp3",
    ]
    destination = tmp_path / "audiobook.mp3"

    for chapter in chapters:
        chapter.write_bytes(b"fake mp3")

    monkeypatch.setattr(
        "audiobook_generator.audio.ffmpeg.shutil.which",
        lambda name: "ffmpeg.exe" if name == "ffmpeg" else "ffprobe.exe",
    )
    monkeypatch.setattr(
        "audiobook_generator.audio.ffmpeg._probe_duration_ms",
        lambda ffprobe, path: 1000 if path == chapters[0] else 2000,
    )

    captured = {}

    def fake_run(command, check):
        captured["command"] = command
        destination.write_bytes(b"fake audiobook")

    monkeypatch.setattr(
        "audiobook_generator.audio.ffmpeg.subprocess.run",
        fake_run,
    )

    result = merge_mp3(
        chapters,
        destination,
        title="Mi Audiolibro",
        chapter_titles=["Capítulo 1", "Capítulo 2"],
    )

    assert result is True
    assert destination.exists()

    command = captured["command"]
    assert "-map_metadata" in command
    assert "1" in command
    assert "ffmetadata" in command
    assert "Mi Audiolibro" not in command


def test_tag_mp3_adds_chapter_metadata(
    tmp_path,
    monkeypatch,
):
    source = tmp_path / "chapter.mp3"
    source.write_bytes(b"fake mp3")

    monkeypatch.setattr(
        "audiobook_generator.audio.ffmpeg.shutil.which",
        lambda _: "ffmpeg.exe",
    )

    def fake_run(command, check):
        temporary = Path(command[-1])
        temporary.write_bytes(b"tagged mp3")

    monkeypatch.setattr(
        "audiobook_generator.audio.ffmpeg.subprocess.run",
        fake_run,
    )

    from audiobook_generator.audio.ffmpeg import tag_mp3

    result = tag_mp3(
        source,
        title="Capítulo 1: La llegada",
        album="Mi Audiolibro",
        track_number=1,
        track_total=3,
    )

    assert result is True
    assert source.read_bytes() == b"tagged mp3"
