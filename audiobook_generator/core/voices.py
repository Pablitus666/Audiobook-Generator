from __future__ import annotations

from dataclasses import dataclass
from typing import Final


@dataclass(frozen=True, slots=True)
class VoiceProfile:
    """Perfil de una voz disponible para el usuario final."""

    id: str
    name: str
    gender: str
    language: str
    engine: str
    voice: str


VOICE_PROFILES: Final[tuple[VoiceProfile, ...]] = (
    VoiceProfile(
        id="Sofía",
        name="Sofía",
        gender="female",
        language="es-BO",
        engine="edge",
        voice="es-BO-SofiaNeural",
    ),
    VoiceProfile(
        id="Elvira",
        name="Elvira",
        gender="female",
        language="es-ES",
        engine="edge",
        voice="es-ES-ElviraNeural",
    ),
    VoiceProfile(
        id="Marcelo",
        name="Marcelo",
        gender="male",
        language="es-BO",
        engine="edge",
        voice="es-BO-MarceloNeural",
    ),
    VoiceProfile(
        id="Álvaro",
        name="Álvaro",
        gender="male",
        language="es-ES",
        engine="edge",
        voice="es-ES-AlvaroNeural",
    ),
)

DEFAULT_VOICE_ID: Final[str] = "Sofía"

# Alias de compatibilidad con configuraciones de versiones anteriores.
_LEGACY_VOICE_IDS: Final[dict[str, str]] = {
    "female_1": "Sofía",
    "female_2": "Elvira",
    "male_1": "Marcelo",
    "male_2": "Álvaro",
}


def _normalize(value: str) -> str:
    return value.strip().casefold()


def list_voice_profiles() -> tuple[VoiceProfile, ...]:
    """Devuelve las voces disponibles en orden estable."""
    return VOICE_PROFILES


def get_voice_profile(voice_id: str) -> VoiceProfile:
    """Obtiene un perfil por su nombre público, ignorando mayúsculas."""
    normalized = _normalize(voice_id)
    normalized = _normalize(_LEGACY_VOICE_IDS.get(normalized, voice_id))

    for profile in VOICE_PROFILES:
        if _normalize(profile.id) == normalized:
            return profile

    valid = ", ".join(profile.name for profile in VOICE_PROFILES)
    raise ValueError(
        f"voz no válida: {voice_id!r}. Voces disponibles: {valid}"
    )


def resolve_voice(voice_value: str) -> VoiceProfile:
    """
    Resuelve una voz por nombre público o por nombre técnico de Edge TTS.

    También acepta los identificadores antiguos como alias de compatibilidad.
    """
    normalized = _normalize(voice_value)

    for profile in VOICE_PROFILES:
        if (
            _normalize(profile.id) == normalized
            or _normalize(profile.name) == normalized
            or _normalize(profile.voice) == normalized
        ):
            return profile

    legacy_id = _LEGACY_VOICE_IDS.get(normalized)
    if legacy_id is not None:
        return get_voice_profile(legacy_id)

    return get_voice_profile(voice_value)
