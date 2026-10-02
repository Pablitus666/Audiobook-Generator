from audiobook_generator.core.voices import (
    DEFAULT_VOICE_ID,
    VOICE_PROFILES,
    get_voice_profile,
    resolve_voice,
)


def test_four_voice_profiles_are_registered():
    assert len(VOICE_PROFILES) == 4
    assert [profile.gender for profile in VOICE_PROFILES] == [
        "female",
        "female",
        "male",
        "male",
    ]


def test_default_voice_is_Sofía():
    profile = get_voice_profile(DEFAULT_VOICE_ID)

    assert profile.name == "Sofía"
    assert profile.voice == "es-BO-SofiaNeural"


def test_voice_profiles_have_unique_ids_and_engine_names():
    ids = [profile.id for profile in VOICE_PROFILES]
    voices = [profile.voice for profile in VOICE_PROFILES]

    assert len(ids) == len(set(ids))
    assert len(voices) == len(set(voices))


def test_resolve_voice_accepts_public_name():
    profile = resolve_voice("Álvaro")

    assert profile.name == "Álvaro"
    assert profile.voice == "es-ES-AlvaroNeural"


def test_resolve_voice_accepts_legacy_id():
    profile = resolve_voice("male_2")

    assert profile.id == "Álvaro"


def test_resolve_voice_accepts_edge_name():
    profile = resolve_voice("es-ES-ElviraNeural")

    assert profile.id == "Elvira"


def test_unknown_voice_is_rejected():
    try:
        resolve_voice("does-not-exist")
    except ValueError as exc:
        assert "voz no válida" in str(exc)
    else:
        raise AssertionError("Se esperaba ValueError")


def test_public_voice_names_are_case_insensitive():
    assert get_voice_profile("ELVIRA").id == "Elvira"
    assert get_voice_profile("álvaro").id == "Álvaro"

