
from __future__ import annotations

from pathlib import Path

import pytest

from audiobook_generator.cli import build_parser, main
from audiobook_generator.core.errors import AudiobookError




def test_cli_lists_voices_without_input(capsys):
    parser = build_parser()
    args = parser.parse_args(["--list-voices"])

    assert args.list_voices is True
    assert args.input is None


def test_cli_list_voices_output(monkeypatch, capsys):
    monkeypatch.setattr(
        "sys.argv",
        ["audiobook-generator", "--list-voices"],
    )

    main()
    output = capsys.readouterr().out

    assert "Voces disponibles:" in output
    assert "Sofía" in output
    assert "Elvira" in output
    assert "Marcelo" in output
    assert "Álvaro" in output
    assert "es-BO-SofiaNeural" in output
    assert "es-ES-ElviraNeural" in output
    assert "Español (Bolivia)" in output
    assert "Español (España)" in output

def test_cli_parses_basic_arguments() -> None:
    parser = build_parser()

    args = parser.parse_args(
        [
            "--input",
            "libro.txt",
        ]
    )

    assert args.input == "libro.txt"
    assert args.output == "output"
    assert args.voice == "Sofía"
    assert args.rate == "+0%"
    assert args.volume == "+0%"
    assert args.pitch == "+0Hz"
    assert args.max_characters == 3000
    assert args.bitrate == "192k"
    assert args.keep_chapters is True
    assert args.ocr == "auto"
    assert args.ocr_language == "spa"
    assert args.ocr_dpi == 300
    assert args.ocr_psm == 3
    assert args.debug_ocr is False


def test_cli_parses_custom_arguments() -> None:
    parser = build_parser()

    args = parser.parse_args(
        [
            "--input",
            "libro.txt",
            "--output",
            "salida",
            "--voice",
            "Álvaro",
            "--rate",
            "+10%",
            "--volume",
            "-5%",
            "--pitch",
            "+2Hz",
            "--max-characters",
            "1500",
            "--bitrate",
            "128k",
            "--no-keep-chapters",
            "--ocr",
            "always",
            "--ocr-language",
            "spa+eng",
            "--ocr-dpi",
            "300",
            "--ocr-psm",
            "6",
            "--debug-ocr",
        ]
    )

    assert args.input == "libro.txt"
    assert args.output == "salida"
    assert args.voice == "Álvaro"
    assert args.rate == "+10%"
    assert args.volume == "-5%"
    assert args.pitch == "+2Hz"
    assert args.max_characters == 1500
    assert args.bitrate == "128k"
    assert args.keep_chapters is False
    assert args.ocr == "always"
    assert args.ocr_language == "spa+eng"
    assert args.ocr_dpi == 300
    assert args.ocr_psm == 6
    assert args.debug_ocr is True


def test_cli_accepts_valid_bitrate() -> None:
    parser = build_parser()

    args = parser.parse_args(
        [
            "--input",
            "libro.txt",
            "--bitrate",
            "256k",
        ]
    )

    assert args.bitrate == "256k"


def test_cli_accepts_megabit_bitrate() -> None:
    parser = build_parser()

    args = parser.parse_args(
        [
            "--input",
            "libro.txt",
            "--bitrate",
            "1M",
        ]
    )

    assert args.bitrate == "1M"


def test_cli_rejects_invalid_bitrate() -> None:
    parser = build_parser()

    with pytest.raises(SystemExit):
        parser.parse_args(
            [
                "--input",
                "libro.txt",
                "--bitrate",
                "192",
            ]
        )


def test_cli_rejects_zero_bitrate() -> None:
    parser = build_parser()

    with pytest.raises(SystemExit):
        parser.parse_args(
            [
                "--input",
                "libro.txt",
                "--bitrate",
                "0k",
            ]
        )


def test_cli_accepts_valid_rate() -> None:
    parser = build_parser()

    args = parser.parse_args(
        [
            "--input",
            "libro.txt",
            "--rate",
            "-15%",
        ]
    )

    assert args.rate == "-15%"


def test_cli_accepts_valid_volume() -> None:
    parser = build_parser()

    args = parser.parse_args(
        [
            "--input",
            "libro.txt",
            "--volume",
            "+8%",
        ]
    )

    assert args.volume == "+8%"


def test_cli_accepts_valid_pitch() -> None:
    parser = build_parser()

    args = parser.parse_args(
        [
            "--input",
            "libro.txt",
            "--pitch",
            "-4Hz",
        ]
    )

    assert args.pitch == "-4Hz"


def test_cli_rejects_invalid_rate() -> None:
    parser = build_parser()

    with pytest.raises(SystemExit):
        parser.parse_args(
            [
                "--input",
                "libro.txt",
                "--rate",
                "10%",
            ]
        )


def test_cli_rejects_invalid_volume() -> None:
    parser = build_parser()

    with pytest.raises(SystemExit):
        parser.parse_args(
            [
                "--input",
                "libro.txt",
                "--volume",
                "fast",
            ]
        )


def test_cli_rejects_invalid_pitch() -> None:
    parser = build_parser()

    with pytest.raises(SystemExit):
        parser.parse_args(
            [
                "--input",
                "libro.txt",
                "--pitch",
                "2",
            ]
        )


def test_cli_rejects_missing_input_file(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        "sys.argv",
        [
            "audiobook-generator",
            "--input",
            "archivo-inexistente.txt",
        ],
    )

    with pytest.raises(SystemExit, match="no existe el archivo de entrada"):
        main()


def test_cli_rejects_invalid_max_characters(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    input_file = tmp_path / "libro.txt"
    input_file.write_text(
        "Texto de prueba.",
        encoding="utf-8",
    )

    monkeypatch.setattr(
        "sys.argv",
        [
            "audiobook-generator",
            "--input",
            str(input_file),
            "--max-characters",
            "0",
        ],
    )

    with pytest.raises(
        SystemExit,
        match="--max-characters debe ser mayor que cero",
    ):
        main()


def test_cli_rejects_unsupported_format(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    input_file = tmp_path / "libro.xyz"
    input_file.write_text(
        "Contenido de prueba.",
        encoding="utf-8",
    )

    monkeypatch.setattr(
        "sys.argv",
        [
            "audiobook-generator",
            "--input",
            str(input_file),
        ],
    )

    with pytest.raises(
        SystemExit,
        match="Formato no soportado",
    ):
        main()


def test_cli_handles_controlled_audiobook_error(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    input_file = tmp_path / "libro.txt"
    input_file.write_text(
        "Contenido de prueba.",
        encoding="utf-8",
    )

    def fail_pipeline(*args, **kwargs):
        raise AudiobookError("fallo controlado")

    monkeypatch.setattr(
        "audiobook_generator.cli.AudiobookPipeline.run",
        fail_pipeline,
    )

    monkeypatch.setattr(
        "sys.argv",
        [
            "audiobook-generator",
            "--input",
            str(input_file),
        ],
    )

    with pytest.raises(
        SystemExit,
        match="ERROR: fallo controlado",
    ):
        main()


def test_cli_handles_unexpected_error(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    input_file = tmp_path / "libro.txt"
    input_file.write_text(
        "Contenido de prueba.",
        encoding="utf-8",
    )

    def fail_pipeline(*args, **kwargs):
        raise RuntimeError("fallo inesperado")

    monkeypatch.setattr(
        "audiobook_generator.cli.AudiobookPipeline.run",
        fail_pipeline,
    )

    monkeypatch.setattr(
        "sys.argv",
        [
            "audiobook-generator",
            "--input",
            str(input_file),
        ],
    )

    with pytest.raises(
        SystemExit,
        match="ERROR: ocurrió un error inesperado",
    ):
        main()


def test_cli_handles_keyboard_interrupt(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    input_file = tmp_path / "libro.txt"
    input_file.write_text(
        "Contenido de prueba.",
        encoding="utf-8",
    )

    def cancel_pipeline(*args, **kwargs):
        raise KeyboardInterrupt

    monkeypatch.setattr(
        "audiobook_generator.cli.AudiobookPipeline.run",
        cancel_pipeline,
    )

    monkeypatch.setattr(
        "sys.argv",
        [
            "audiobook-generator",
            "--input",
            str(input_file),
        ],
    )

    with pytest.raises(
        SystemExit,
        match="Operación cancelada por el usuario",
    ):
        main()


def test_cli_handles_empty_document(
    tmp_path,
    monkeypatch,
) -> None:
    input_file = tmp_path / "vacio.txt"
    input_file.write_text(
        "",
        encoding="utf-8",
    )

    async def fail_with_empty_document(*args, **kwargs):
        from audiobook_generator.core.errors import EmptyDocumentError

        raise EmptyDocumentError(
            "el documento no contiene texto utilizable."
        )

    monkeypatch.setattr(
        "audiobook_generator.cli.AudiobookPipeline.run",
        fail_with_empty_document,
    )

    monkeypatch.setattr(
        "sys.argv",
        [
            "audiobook-generator",
            "--input",
            str(input_file),
        ],
    )

    with pytest.raises(
        SystemExit,
        match="ERROR: el documento no contiene texto utilizable",
    ):
        main()


def test_cli_rejects_unknown_voice():
    parser = build_parser()

    with pytest.raises(SystemExit):
        parser.parse_args(
            ["--input", "libro.txt", "--voice", "does-not-exist"]
        )



def test_cli_rejects_invalid_ocr_dpi():
    parser = build_parser()

    args = parser.parse_args(
        [
            "--input",
            "libro.pdf",
            "--ocr-dpi",
            "0",
        ]
    )

    assert args.ocr_dpi == 0
