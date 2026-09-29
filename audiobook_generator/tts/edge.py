from __future__ import annotations

from pathlib import Path

import edge_tts

from audiobook_generator.core.errors import TTSError
from audiobook_generator.tts.base import TTSEngine


class EdgeTTSEngine(TTSEngine):
    """Motor de síntesis basado en Microsoft Edge TTS."""

    def __init__(
        self,
        voice: str,
        rate: str = "+0%",
        volume: str = "+0%",
        pitch: str = "+0Hz",
    ) -> None:
        self.voice = voice
        self.rate = rate
        self.volume = volume
        self.pitch = pitch

    async def synthesize(
        self,
        text: str,
        destination: Path,
    ) -> None:
        if not text.strip():
            raise TTSError("no se puede sintetizar texto vacío.")

        destination.parent.mkdir(parents=True, exist_ok=True)

        try:
            communicate = edge_tts.Communicate(
                text,
                self.voice,
                rate=self.rate,
                volume=self.volume,
                pitch=self.pitch,
            )

            await communicate.save(str(destination))

        except Exception as exc:
            raise TTSError(
                f"falló la síntesis de voz para: {destination.name}"
            ) from exc

        if not destination.is_file():
            raise TTSError(
                f"el motor TTS no generó el archivo esperado: "
                f"{destination}"
            )