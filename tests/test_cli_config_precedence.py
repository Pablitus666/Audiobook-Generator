from pathlib import Path

from audiobook_generator import cli


def test_config_file_values_are_used_when_cli_options_are_omitted(
    tmp_path: Path,
):
    config_file = tmp_path / "audiobook.toml"

    config_file.write_text(
        """
[tts]
voice = "Álvaro"
rate = "+15%"
volume = "-5%"
pitch = "-2Hz"

[output]
bitrate = "128k"

[processing]
max_characters = 5000
temp_dir = "toml_temp"
keep_chapters = false

[ocr]
mode = "always"
language = "spa+eng"
dpi = 300
""",
        encoding="utf-8",
    )

    argv = [
        "--input",
        "libro.txt",
        "--config",
        str(config_file),
    ]

    args = cli.build_parser().parse_args(argv)
    config = cli._load_cli_config(args, argv)

    assert config.tts.voice == "Álvaro"
    assert config.tts.rate == "+15%"
    assert config.tts.volume == "-5%"
    assert config.tts.pitch == "-2Hz"
    assert config.output.bitrate == "128k"
    assert config.processing.max_characters == 5000
    assert config.processing.temp_dir == Path("toml_temp")
    assert config.processing.keep_chapters is False
    assert config.ocr.mode == "always"
    assert config.ocr.language == "spa+eng"
    assert config.ocr.dpi == 300


def test_explicit_cli_options_override_config_file(
    tmp_path: Path,
):
    config_file = tmp_path / "audiobook.toml"

    config_file.write_text(
        """
[tts]
voice = "Álvaro"
rate = "+15%"
volume = "-5%"
pitch = "-2Hz"

[output]
bitrate = "128k"

[processing]
max_characters = 5000
temp_dir = "toml_temp"
keep_chapters = false
""",
        encoding="utf-8",
    )

    argv = [
        "--input",
        "libro.txt",
        "--config",
        str(config_file),
        "--voice",
        "Elvira",
        "--rate",
        "-10%",
        "--volume",
        "+10%",
        "--pitch",
        "+3Hz",
        "--bitrate",
        "192k",
        "--max-characters",
        "3000",
        "--temp-dir",
        "cli_temp",
        "--keep-chapters",
        "--ocr",
        "never",
        "--ocr-language",
        "eng",
        "--ocr-dpi",
        "150",
    ]

    args = cli.build_parser().parse_args(argv)
    config = cli._load_cli_config(args, argv)

    assert config.tts.voice == "Elvira"
    assert config.tts.rate == "-10%"
    assert config.tts.volume == "+10%"
    assert config.tts.pitch == "+3Hz"
    assert config.output.bitrate == "192k"
    assert config.processing.max_characters == 3000
    assert config.processing.temp_dir == Path("cli_temp")
    assert config.processing.keep_chapters is True
    assert config.ocr.mode == "never"
    assert config.ocr.language == "eng"
    assert config.ocr.dpi == 150


def test_no_config_preserves_existing_cli_defaults():
    argv = [
        "--input",
        "libro.txt",
    ]

    args = cli.build_parser().parse_args(argv)
    config = cli._load_cli_config(args, argv)

    assert config.tts.voice == "Sofía"
    assert config.tts.rate == "+0%"
    assert config.tts.volume == "+0%"
    assert config.tts.pitch == "+0Hz"
    assert config.output.bitrate == "192k"
    assert config.processing.max_characters == 3000
    assert config.processing.temp_dir == Path("temp")
    assert config.processing.keep_chapters is True


def test_no_keep_chapters_overrides_config_file(
    tmp_path: Path,
):
    config_file = tmp_path / "audiobook.toml"

    config_file.write_text(
        """
[processing]
keep_chapters = true
""",
        encoding="utf-8",
    )

    argv = [
        "--input",
        "libro.txt",
        "--config",
        str(config_file),
        "--no-keep-chapters",
    ]

    args = cli.build_parser().parse_args(argv)
    config = cli._load_cli_config(args, argv)

    assert config.processing.keep_chapters is False


def test_debug_ocr_cli_overrides_config_file(tmp_path: Path):
    config_file = tmp_path / "audiobook.toml"
    config_file.write_text(
        """
[processing]

debug_ocr = true
""",
        encoding="utf-8",
    )

    argv = [
        "--input",
        "libro.txt",
        "--config",
        str(config_file),
        "--no-debug-ocr",
    ]

    args = cli.build_parser().parse_args(argv)
    config = cli._load_cli_config(args, argv)

    assert config.processing.debug_ocr is False


def test_debug_ocr_cli_enables_configured_false(tmp_path: Path):
    config_file = tmp_path / "audiobook.toml"
    config_file.write_text(
        """
[processing]

debug_ocr = false
""",
        encoding="utf-8",
    )

    argv = [
        "--input",
        "libro.txt",
        "--config",
        str(config_file),
        "--debug-ocr",
    ]

    args = cli.build_parser().parse_args(argv)
    config = cli._load_cli_config(args, argv)

    assert config.processing.debug_ocr is True
