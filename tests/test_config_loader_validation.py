from pathlib import Path

import pytest

from audiobook_generator.core.config_loader import load_config


def write_config(tmp_path: Path, content: str) -> Path:
    config_file = tmp_path / "audiobook.toml"
    config_file.write_text(content, encoding="utf-8")
    return config_file


@pytest.mark.parametrize(
    ("section", "field", "value", "message"),
    [
        ("tts", "rate", '"10%"', "rate"),
        ("tts", "volume", '"loud"', "volume"),
        ("tts", "pitch", '"+2"', "pitch"),
        ("output", "bitrate", '"0k"', "bitrate"),
        ("output", "bitrate", '"192"', "bitrate"),
    ],
)
def test_load_config_rejects_invalid_tts_and_output_values(
    tmp_path: Path,
    section: str,
    field: str,
    value: str,
    message: str,
):
    config_file = write_config(
        tmp_path,
        f"""
[{section}]
{field} = {value}
""",
    )

    with pytest.raises(ValueError, match=message):
        load_config(config_file)


@pytest.mark.parametrize("value", ["0", "-1"])
def test_load_config_rejects_invalid_max_characters(
    tmp_path: Path,
    value: str,
):
    config_file = write_config(
        tmp_path,
        f"""
[processing]
max_characters = {value}
""",
    )

    with pytest.raises(ValueError, match="max_characters"):
        load_config(config_file)


def test_load_config_rejects_non_boolean_keep_chapters(tmp_path: Path):
    config_file = write_config(
        tmp_path,
        """
[processing]
keep_chapters = "false"
""",
    )

    with pytest.raises(ValueError, match="keep_chapters"):
        load_config(config_file)


def test_load_config_rejects_unsupported_output_format(tmp_path: Path):
    config_file = write_config(
        tmp_path,
        """
[output]
format = "wav"
""",
    )

    with pytest.raises(ValueError, match="format"):
        load_config(config_file)


def test_load_config_rejects_empty_voice(tmp_path: Path):
    config_file = write_config(
        tmp_path,
        """
[tts]
voice = ""
""",
    )

    with pytest.raises(ValueError, match="voice"):
        load_config(config_file)


def test_load_config_rejects_unknown_voice(tmp_path: Path):
    config_file = write_config(
        tmp_path,
        """
[tts]
voice = "does-not-exist"
""",
    )

    with pytest.raises(ValueError, match="voz no válida"):
        load_config(config_file)


def test_load_config_accepts_public_voice_name(tmp_path: Path):
    config_file = write_config(
        tmp_path,
        """
[tts]
voice = "Elvira"
""",
    )

    config = load_config(config_file)

    assert config.tts.voice == "Elvira"


def test_load_config_normalizes_legacy_edge_voice(tmp_path: Path):
    config_file = write_config(
        tmp_path,
        """
[tts]
voice = "es-ES-ElviraNeural"
""",
    )

    config = load_config(config_file)

    assert config.tts.voice == "Elvira"


def test_load_config_accepts_boolean_debug_ocr(tmp_path: Path):
    config_file = write_config(
        tmp_path,
        """
[processing]
debug_ocr = true
""",
    )

    config = load_config(config_file)

    assert config.processing.debug_ocr is True


def test_load_config_rejects_non_boolean_debug_ocr(tmp_path: Path):
    config_file = write_config(
        tmp_path,
        """
[processing]
debug_ocr = "true"
""",
    )

    with pytest.raises(ValueError, match="debug_ocr"):
        load_config(config_file)
