from __future__ import annotations

import argparse
import asyncio
import re
import sys
from pathlib import Path

from .core.config import AudiobookConfig, OcrConfig, OutputConfig, ProcessingConfig, TTSConfig
from .core.config_loader import load_config
from .core.errors import AudiobookError, InputFileError
from .core.pipeline import AudiobookPipeline
from .core.voices import DEFAULT_VOICE_ID, list_voice_profiles, resolve_voice
from . import __version__
from .readers.factory import ReaderFactory
from .readers.pdf import PdfReader
from .ocr.tesseract import TesseractOcrEngine
from .tts.edge import EdgeTTSEngine

_BITRATE_RE = re.compile(r"^\d+(?:[kKmMgG])$")
_PERCENT_RE = re.compile(r"^[+-]\d+%$")
_PITCH_RE = re.compile(r"^[+-]\d+Hz$")


def _validate_voice(value: str) -> str:
    value = value.strip()
    try:
        return resolve_voice(value).id
    except ValueError as exc:
        raise argparse.ArgumentTypeError(str(exc)) from exc


def _voice_help() -> str:
    profiles = ", ".join(profile.name for profile in list_voice_profiles())
    return f"Voces disponibles: {profiles}. También acepta nombres técnicos de Edge TTS."


def _print_voice_catalog() -> None:
    print("Voces disponibles:")
    print()
    print(f"{'Nombre':<10} {'Idioma':<22} {'Género':<12} {'Voz técnica'}")
    print(f"{'-' * 10} {'-' * 22} {'-' * 12} {'-' * 28}")

    gender_labels = {
        "female": "Femenina",
        "male": "Masculina",
    }

    language_labels = {
        "es-BO": "Español (Bolivia)",
        "es-ES": "Español (España)",
    }

    for profile in list_voice_profiles():
        language = language_labels.get(profile.language, profile.language)
        gender = gender_labels.get(profile.gender, profile.gender)
        print(f"{profile.name:<10} {language:<22} {gender:<12} {profile.voice}")


def _validate_bitrate(value: str) -> str:
    value = value.strip()
    if not _BITRATE_RE.fullmatch(value):
        raise argparse.ArgumentTypeError(
            "el bitrate debe tener formato numérico con sufijo "
            "(por ejemplo: 128k, 192k, 256k o 1M)."
        )
    if int(value[:-1]) <= 0:
        raise argparse.ArgumentTypeError("el bitrate debe ser mayor que cero.")
    return value


def _validate_percent(value: str) -> str:
    value = value.strip()
    if not _PERCENT_RE.fullmatch(value):
        raise argparse.ArgumentTypeError(
            "el valor debe tener formato porcentual con signo "
            "(por ejemplo: +10% o -10%)."
        )
    return value


def _validate_pitch(value: str) -> str:
    value = value.strip()
    if not _PITCH_RE.fullmatch(value):
        raise argparse.ArgumentTypeError(
            "el tono debe tener formato numérico en Hz con signo "
            "(por ejemplo: +2Hz o -4Hz)."
        )
    return value


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="audiobook-generator",
        description="Convierte documentos de texto en audiolibros.",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )
    parser.add_argument(
        "--input",
        required=False,
        help="Archivo de entrada.",
    )
    parser.add_argument(
        "--list-voices",
        action="store_true",
        help="Muestra el catálogo de voces disponibles y termina.",
    )
    parser.add_argument(
        "--config",
        default=None,
        help="Archivo TOML de configuración.",
    )
    parser.add_argument("--output", default="output", help="Directorio de salida.")
    parser.add_argument(
        "--temp-dir",
        default="temp",
        help="Directorio para archivos temporales.",
    )
    parser.add_argument(
        "--voice",
        type=_validate_voice,
        default=DEFAULT_VOICE_ID,
        help=_voice_help(),
    )
    parser.add_argument(
        "--rate",
        type=_validate_percent,
        default="+0%",
        help="Velocidad, por ejemplo +10%% o -10%%.",
    )
    parser.add_argument(
        "--volume",
        type=_validate_percent,
        default="+0%",
        help="Volumen, por ejemplo +10%% o -10%%.",
    )
    parser.add_argument(
        "--pitch",
        type=_validate_pitch,
        default="+0Hz",
        help="Tono Edge TTS, por ejemplo +2Hz o -4Hz.",
    )
    parser.add_argument(
        "--max-characters",
        type=int,
        default=3000,
        help="Máximo de caracteres por fragmento TTS.",
    )
    parser.add_argument(
        "--bitrate",
        type=_validate_bitrate,
        default="192k",
        help="Bitrate MP3, por ejemplo 128k, 192k, 256k o 1M.",
    )
    parser.add_argument(
        "--ocr",
        choices=("auto", "always", "never"),
        default="auto",
        help=(
            "Procesamiento OCR de PDF: auto detecta páginas escaneadas, "
            "always fuerza OCR y never desactiva OCR."
        ),
    )
    parser.add_argument(
        "--ocr-language",
        default="spa",
        help="Idioma de Tesseract para OCR de PDF (por ejemplo: spa, eng, spa+eng).",
    )
    parser.add_argument(
        "--ocr-dpi",
        type=int,
        default=300,
        help="Resolución de renderizado para OCR de PDF.",
    )
    parser.add_argument(
        "--ocr-psm",
        type=int,
        default=3,
        help="Modo de segmentación de página de Tesseract (1-13).",
    )
    parser.add_argument(
        "--keep-chapters",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Conservar los MP3 individuales de cada capítulo.",
    )
    parser.add_argument(
        "--debug-ocr",
        action=argparse.BooleanOptionalAction,
        default=False,
        help=(
            "Guardar el texto OCR original y el texto limpiado antes del TTS "
            "para diagnóstico."
        ),
    )
    return parser


def _option_was_supplied(argv: list[str], *names: str) -> bool:
    return any(
        argument == name or argument.startswith(f"{name}=")
        for argument in argv
        for name in names
    )


def _load_cli_config(
    args: argparse.Namespace,
    argv: list[str],
) -> AudiobookConfig:
    if args.config is not None:
        config = load_config(Path(args.config))
    else:
        config = AudiobookConfig()

    tts = config.tts
    output = config.output
    processing = config.processing

    if _option_was_supplied(argv, "--voice"):
        tts = TTSConfig(args.voice, tts.rate, tts.volume, tts.pitch)
    if _option_was_supplied(argv, "--rate"):
        tts = TTSConfig(tts.voice, args.rate, tts.volume, tts.pitch)
    if _option_was_supplied(argv, "--volume"):
        tts = TTSConfig(tts.voice, tts.rate, args.volume, tts.pitch)
    if _option_was_supplied(argv, "--pitch"):
        tts = TTSConfig(tts.voice, tts.rate, tts.volume, args.pitch)

    if _option_was_supplied(argv, "--bitrate"):
        output = OutputConfig(output.format, args.bitrate)

    if _option_was_supplied(argv, "--max-characters"):
        processing = ProcessingConfig(
            max_characters=args.max_characters,
            temp_dir=processing.temp_dir,
            keep_chapters=processing.keep_chapters,
            debug_ocr=processing.debug_ocr,
        )
    if _option_was_supplied(argv, "--temp-dir"):
        processing = ProcessingConfig(
            max_characters=processing.max_characters,
            temp_dir=Path(args.temp_dir),
            keep_chapters=processing.keep_chapters,
            debug_ocr=processing.debug_ocr,
        )
    if _option_was_supplied(argv, "--keep-chapters"):
        processing = ProcessingConfig(
            max_characters=processing.max_characters,
            temp_dir=processing.temp_dir,
            keep_chapters=True,
            debug_ocr=processing.debug_ocr,
        )
    if _option_was_supplied(argv, "--no-keep-chapters"):
        processing = ProcessingConfig(
            max_characters=processing.max_characters,
            temp_dir=processing.temp_dir,
            keep_chapters=False,
            debug_ocr=processing.debug_ocr,
        )

    if _option_was_supplied(argv, "--debug-ocr"):
        processing = ProcessingConfig(
            max_characters=processing.max_characters,
            temp_dir=processing.temp_dir,
            keep_chapters=processing.keep_chapters,
            debug_ocr=True,
        )
    if _option_was_supplied(argv, "--no-debug-ocr"):
        processing = ProcessingConfig(
            max_characters=processing.max_characters,
            temp_dir=processing.temp_dir,
            keep_chapters=processing.keep_chapters,
            debug_ocr=False,
        )

    ocr = config.ocr

    if _option_was_supplied(argv, "--ocr"):
        ocr = OcrConfig(
            mode=args.ocr,
            language=ocr.language,
            dpi=ocr.dpi,
            psm=ocr.psm,
        )

    if _option_was_supplied(argv, "--ocr-language"):
        ocr = OcrConfig(
            mode=ocr.mode,
            language=args.ocr_language,
            dpi=ocr.dpi,
            psm=ocr.psm,
        )

    if _option_was_supplied(argv, "--ocr-dpi"):
        ocr = OcrConfig(
            mode=ocr.mode,
            language=ocr.language,
            dpi=args.ocr_dpi,
            psm=ocr.psm,
        )

    if _option_was_supplied(argv, "--ocr-psm"):
        ocr = OcrConfig(
            mode=ocr.mode,
            language=ocr.language,
            dpi=ocr.dpi,
            psm=args.ocr_psm,
        )

    return AudiobookConfig(
        tts=tts,
        output=output,
        processing=processing,
        ocr=ocr,
    )


def main() -> None:
    argv = sys.argv[1:]
    args = build_parser().parse_args(argv)

    if args.list_voices:
        _print_voice_catalog()
        return

    if args.input is None:
        build_parser().error("--input es obligatorio salvo cuando se usa --list-voices")

    try:
        input_path = Path(args.input).expanduser().resolve()
        output_dir = Path(args.output).expanduser().resolve()

        if not input_path.is_file():
            raise InputFileError(f"no existe el archivo de entrada: {input_path}")

        config = _load_cli_config(args, argv)

        if config.processing.max_characters <= 0:
            raise AudiobookError("--max-characters debe ser mayor que cero.")

        if config.ocr.dpi <= 0:
            raise AudiobookError("--ocr-dpi debe ser mayor que cero.")

        if not 1 <= config.ocr.psm <= 13:
            raise AudiobookError("--ocr-psm debe estar entre 1 y 13.")

        pdf_reader = PdfReader(
            ocr_engine=TesseractOcrEngine(
                language=config.ocr.language,
                psm=config.ocr.psm,
            ),
            ocr_config=config.ocr,
        )

        reader = ReaderFactory.create(
            input_path,
            pdf_reader=pdf_reader,
        )
        tts = EdgeTTSEngine(
            voice=resolve_voice(config.tts.voice).voice,
            rate=config.tts.rate,
            volume=config.tts.volume,
            pitch=config.tts.pitch,
        )
        pipeline = AudiobookPipeline(reader=reader, tts=tts, config=config)
        result = asyncio.run(pipeline.run(input_path, output_dir))

    except AudiobookError as exc:
        raise SystemExit(f"ERROR: {exc}") from exc
    except KeyboardInterrupt:
        raise SystemExit("\nOperación cancelada por el usuario.") from None
    except Exception as exc:
        raise SystemExit(
            "ERROR: ocurrió un error inesperado durante "
            f"la generación del audiolibro: {exc}"
        ) from exc

    print()
    print("✓ Audiolibro generado")
    print(f"  Capítulos: {len(result.chapter_files)}")
    for chapter_file in result.chapter_files:
        print(f"  - {chapter_file}")
    if result.merged_file:
        print(f"  Final: {result.merged_file}")
    else:
        print("  Final: no se pudo unir automáticamente (FFmpeg no disponible).")


if __name__ == "__main__":
    main()
