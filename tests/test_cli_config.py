from audiobook_generator.cli import build_parser


def test_cli_default_configuration_arguments():
    parser = build_parser()

    args = parser.parse_args(
        [
            "--input",
            "libro.txt",
        ]
    )

    assert args.voice == "Sofía"
    assert args.rate == "+0%"
    assert args.volume == "+0%"
    assert args.pitch == "+0Hz"
    assert args.max_characters == 1500
    assert args.bitrate == "192k"
    assert args.keep_chapters is True
    assert args.temp_dir == "temp"
    assert args.ocr == "auto"
    assert args.ocr_language == "spa"
    assert args.ocr_dpi == 300


def test_cli_custom_configuration_arguments():
    parser = build_parser()

    args = parser.parse_args(
        [
            "--input",
            "libro.txt",
            "--output",
            "salida",
            "--temp-dir",
            "mi_temp",
            "--voice",
            "Álvaro",
            "--rate",
            "+10%",
            "--volume",
            "-5%",
            "--pitch",
            "-2Hz",
            "--max-characters",
            "5000",
            "--bitrate",
            "128k",
            "--no-keep-chapters",
            "--ocr",
            "always",
            "--ocr-language",
            "spa+eng",
            "--ocr-dpi",
            "300",
        ]
    )

    assert args.output == "salida"
    assert args.temp_dir == "mi_temp"
    assert args.voice == "Álvaro"
    assert args.rate == "+10%"
    assert args.volume == "-5%"
    assert args.pitch == "-2Hz"
    assert args.max_characters == 5000
    assert args.bitrate == "128k"
    assert args.keep_chapters is False
    assert args.ocr == "always"
    assert args.ocr_language == "spa+eng"
    assert args.ocr_dpi == 300


def test_cli_accepts_all_public_voice_profiles():
    parser = build_parser()

    for voice_id in ("Sofía", "Elvira", "Marcelo", "Álvaro"):
        args = parser.parse_args(["--input", "libro.txt", "--voice", voice_id])
        assert args.voice == voice_id


def test_cli_normalizes_legacy_edge_voice():
    parser = build_parser()

    args = parser.parse_args(
        ["--input", "libro.txt", "--voice", "es-ES-ElviraNeural"]
    )

    assert args.voice == "Elvira"
