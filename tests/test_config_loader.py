from pathlib import Path

import pytest

from audiobook_generator.core.config_loader import load_config


def test_load_config_reads_all_sections(tmp_path: Path):
    config_file = tmp_path / "audiobook.toml"

    config_file.write_text(
        '''
[tts]
voice = "Álvaro"
rate = "+10%"
volume = "-5%"
pitch = "-2Hz"

[output]
format = "mp3"
bitrate = "128k"

[processing]
max_characters = 5000
temp_dir = "mi_temp"
keep_chapters = false
debug_ocr = true

[ocr]
mode = "always"
language = "spa+eng"
dpi = 300
psm = 6
''',
        encoding="utf-8",
    )

    config = load_config(config_file)

    assert config.tts.voice == "Álvaro"
    assert config.tts.rate == "+10%"
    assert config.tts.volume == "-5%"
    assert config.tts.pitch == "-2Hz"
    assert config.output.format == "mp3"
    assert config.output.bitrate == "128k"
    assert config.processing.max_characters == 5000
    assert config.processing.temp_dir == Path("mi_temp")
    assert config.processing.keep_chapters is False
    assert config.processing.debug_ocr is True
    assert config.ocr.mode == "always"
    assert config.ocr.language == "spa+eng"
    assert config.ocr.dpi == 300
    assert config.ocr.psm == 6


def test_load_config_uses_defaults_for_missing_values(tmp_path: Path):
    config_file = tmp_path / "audiobook.toml"

    config_file.write_text(
        '''
[tts]
voice = "Álvaro"
''',
        encoding="utf-8",
    )

    config = load_config(config_file)

    assert config.tts.voice == "Álvaro"
    assert config.tts.rate == "+0%"
    assert config.tts.volume == "+0%"
    assert config.tts.pitch == "+0Hz"
    assert config.output.format == "mp3"
    assert config.output.bitrate == "192k"
    assert config.processing.max_characters == 3000
    assert config.processing.temp_dir == Path("temp")
    assert config.processing.keep_chapters is True
    assert config.ocr.mode == "auto"
    assert config.ocr.language == "spa"
    assert config.ocr.dpi == 300
    assert config.ocr.psm == 3


def test_load_config_rejects_invalid_toml(tmp_path: Path):
    config_file = tmp_path / "audiobook.toml"

    config_file.write_text(
        '''
[tts
voice = "Elvira"
''',
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="configuración TOML inválida"):
        load_config(config_file)


def test_load_config_rejects_missing_file(tmp_path: Path):
    config_file = tmp_path / "missing.toml"

    with pytest.raises(
        FileNotFoundError,
        match="no existe el archivo de configuración",
    ):
        load_config(config_file)


def test_load_config_rejects_invalid_ocr_mode(tmp_path: Path):
    config_file = tmp_path / "audiobook.toml"

    config_file.write_text(
        """
[ocr]
mode = "manual"
""",
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="ocr.mode"):
        load_config(config_file)


def test_load_config_rejects_invalid_ocr_dpi(tmp_path: Path):
    config_file = tmp_path / "audiobook.toml"

    config_file.write_text(
        """
[ocr]
dpi = 0
""",
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="ocr.dpi"):
        load_config(config_file)


def test_config_loader_rejects_non_boolean_debug_ocr(tmp_path):
    from audiobook_generator.core.config_loader import load_config

    path = tmp_path / "config.toml"
    path.write_text(
        "[processing]\ndebug_ocr = \"yes\"\n",
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="debug_ocr: debe ser booleano"):
        load_config(path)


def test_load_config_rejects_invalid_ocr_psm(tmp_path: Path):
    config_file = tmp_path / "audiobook.toml"
    config_file.write_text("[ocr]\npsm = 14\n", encoding="utf-8")

    with pytest.raises(ValueError, match="ocr.psm"):
        load_config(config_file)
