from pathlib import Path

import pytest

from audiobook_generator.tts import edge


@pytest.mark.asyncio
async def test_edge_tts_passes_voice_rate_volume_and_pitch(
    monkeypatch,
    tmp_path: Path,
):
    captured = {}

    class FakeCommunicate:
        def __init__(
            self,
            text,
            voice,
            rate,
            volume,
            pitch,
        ):
            captured["text"] = text
            captured["voice"] = voice
            captured["rate"] = rate
            captured["volume"] = volume
            captured["pitch"] = pitch

        async def save(self, destination):
            captured["destination"] = destination
            Path(destination).write_bytes(b"fake-mp3")

    monkeypatch.setattr(
        edge.edge_tts,
        "Communicate",
        FakeCommunicate,
    )

    destination = tmp_path / "chapter.mp3"

    engine = edge.EdgeTTSEngine(
        voice="es-MX-DaliaNeural",
        rate="+10%",
        volume="-5%",
        pitch="-2Hz",
    )

    await engine.synthesize(
        "Texto de prueba.",
        destination,
    )

    assert captured["text"] == "Texto de prueba."
    assert captured["voice"] == "es-MX-DaliaNeural"
    assert captured["rate"] == "+10%"
    assert captured["volume"] == "-5%"
    assert captured["pitch"] == "-2Hz"
    assert captured["destination"] == str(destination)
    assert destination.is_file()


@pytest.mark.asyncio
async def test_edge_tts_rejects_empty_text(
    tmp_path: Path,
):
    engine = edge.EdgeTTSEngine(
        voice="es-ES-ElviraNeural",
    )

    with pytest.raises(
        edge.TTSError,
        match="no se puede sintetizar texto vacío",
    ):
        await engine.synthesize(
            "   ",
            tmp_path / "chapter.mp3",
        )


@pytest.mark.asyncio
async def test_edge_tts_wraps_synthesis_error(
    monkeypatch,
    tmp_path: Path,
):
    class FailingCommunicate:
        def __init__(
            self,
            text,
            voice,
            rate,
            volume,
            pitch,
        ):
            pass

        async def save(self, destination):
            raise RuntimeError("fallo de prueba")

    monkeypatch.setattr(
        edge.edge_tts,
        "Communicate",
        FailingCommunicate,
    )

    engine = edge.EdgeTTSEngine(
        voice="es-ES-ElviraNeural",
    )

    with pytest.raises(
        edge.TTSError,
        match="falló la síntesis de voz",
    ):
        await engine.synthesize(
            "Texto de prueba.",
            tmp_path / "chapter.mp3",
        )


@pytest.mark.asyncio
async def test_edge_tts_rejects_missing_output(
    monkeypatch,
    tmp_path: Path,
):
    class FakeCommunicate:
        def __init__(
            self,
            text,
            voice,
            rate,
            volume,
            pitch,
        ):
            pass

        async def save(self, destination):
            pass

    monkeypatch.setattr(
        edge.edge_tts,
        "Communicate",
        FakeCommunicate,
    )

    destination = tmp_path / "chapter.mp3"

    engine = edge.EdgeTTSEngine(
        voice="es-ES-ElviraNeural",
    )

    with pytest.raises(
        edge.TTSError,
        match="no generó el archivo esperado",
    ):
        await engine.synthesize(
            "Texto de prueba.",
            destination,
        )