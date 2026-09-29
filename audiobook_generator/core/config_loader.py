from __future__ import annotations

from pathlib import Path
import re
import tomllib

from .config import AudiobookConfig, OcrConfig, OutputConfig, ProcessingConfig, TTSConfig
from .voices import resolve_voice


_RATE_RE = re.compile(r"^[+-]\d+%$")
_PITCH_RE = re.compile(r"^[+-]\d+Hz$")
_BITRATE_RE = re.compile(r"^(\d+)([kKmMgG])$")
_OCR_MODES = {"auto", "always", "never"}


def _require_string(
    value: object,
    field_name: str,
) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(
            f"valor inválido para {field_name}: debe ser un texto no vacío."
        )

    return value


def _validate_rate(
    value: object,
    field_name: str,
) -> str:
    value = _require_string(value, field_name)

    if not _RATE_RE.fullmatch(value):
        raise ValueError(
            f"valor inválido para {field_name}: formato esperado +/-N%."
        )

    return value


def _validate_pitch(
    value: object,
    field_name: str,
) -> str:
    value = _require_string(value, field_name)

    if not _PITCH_RE.fullmatch(value):
        raise ValueError(
            f"valor inválido para {field_name}: formato esperado +/-NHz."
        )

    return value


def _validate_bitrate(value: object) -> str:
    value = _require_string(value, "bitrate")
    match = _BITRATE_RE.fullmatch(value)

    if match is None or int(match.group(1)) <= 0:
        raise ValueError(
            "valor inválido para bitrate: debe ser un número positivo "
            "seguido de k, M o G."
        )

    return value


def _validate_positive_integer(
    value: object,
    field_name: str,
) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
        raise ValueError(
            f"valor inválido para {field_name}: debe ser un entero mayor que 0."
        )

    return value


def _validate_section(
    data: object,
    section_name: str,
) -> dict[str, object]:
    if not isinstance(data, dict):
        raise ValueError(
            f"sección inválida [{section_name}]: debe ser una tabla TOML."
        )

    return data


def load_config(path: Path) -> AudiobookConfig:
    if not path.is_file():
        raise FileNotFoundError(
            f"no existe el archivo de configuración: {path}"
        )

    try:
        with path.open("rb") as file:
            data = tomllib.load(file)
    except tomllib.TOMLDecodeError as exc:
        raise ValueError(
            f"configuración TOML inválida: {exc}"
        ) from exc

    tts_data = _validate_section(
        data.get("tts", {}),
        "tts",
    )
    output_data = _validate_section(
        data.get("output", {}),
        "output",
    )
    processing_data = _validate_section(
        data.get("processing", {}),
        "processing",
    )
    ocr_data = _validate_section(
        data.get("ocr", {}),
        "ocr",
    )

    defaults_tts = TTSConfig()
    defaults_output = OutputConfig()
    defaults_processing = ProcessingConfig()

    voice = tts_data.get("voice", defaults_tts.voice)
    voice = _require_string(voice, "voice")
    try:
        voice = resolve_voice(voice).id
    except ValueError as exc:
        raise ValueError(str(exc)) from exc

    rate = _validate_rate(
        tts_data.get("rate", defaults_tts.rate),
        "rate",
    )

    volume = _validate_rate(
        tts_data.get("volume", defaults_tts.volume),
        "volume",
    )

    pitch = _validate_pitch(
        tts_data.get("pitch", defaults_tts.pitch),
        "pitch",
    )

    output_format = output_data.get(
        "format",
        defaults_output.format,
    )
    output_format = _require_string(
        output_format,
        "format",
    ).lower()

    if output_format != "mp3":
        raise ValueError(
            f"valor inválido para format: formato no soportado: "
            f"{output_format}"
        )

    bitrate = _validate_bitrate(
        output_data.get(
            "bitrate",
            defaults_output.bitrate,
        )
    )

    max_characters = _validate_positive_integer(
        processing_data.get(
            "max_characters",
            defaults_processing.max_characters,
        ),
        "max_characters",
    )

    temp_dir_value = processing_data.get(
        "temp_dir",
        str(defaults_processing.temp_dir),
    )
    temp_dir_value = _require_string(
        temp_dir_value,
        "temp_dir",
    )

    keep_chapters = processing_data.get(
        "keep_chapters",
        defaults_processing.keep_chapters,
    )
    if not isinstance(keep_chapters, bool):
        raise ValueError(
            "valor inválido para keep_chapters: debe ser booleano."
        )

    debug_ocr = processing_data.get(
        "debug_ocr",
        defaults_processing.debug_ocr,
    )
    if not isinstance(debug_ocr, bool):
        raise ValueError(
            "valor inválido para debug_ocr: debe ser booleano."
        )

    defaults_ocr = OcrConfig()

    ocr_mode = _require_string(
        ocr_data.get("mode", defaults_ocr.mode),
        "ocr.mode",
    ).lower()
    if ocr_mode not in _OCR_MODES:
        raise ValueError(
            "valor inválido para ocr.mode: debe ser auto, always o never."
        )

    ocr_language = _require_string(
        ocr_data.get("language", defaults_ocr.language),
        "ocr.language",
    )

    ocr_dpi = _validate_positive_integer(
        ocr_data.get("dpi", defaults_ocr.dpi),
        "ocr.dpi",
    )

    ocr_psm = _validate_positive_integer(
        ocr_data.get("psm", defaults_ocr.psm),
        "ocr.psm",
    )
    if ocr_psm > 13:
        raise ValueError("valor inválido para ocr.psm: debe estar entre 1 y 13.")

    return AudiobookConfig(
        tts=TTSConfig(
            voice=voice,
            rate=rate,
            volume=volume,
            pitch=pitch,
        ),
        output=OutputConfig(
            format=output_format,
            bitrate=bitrate,
        ),
        processing=ProcessingConfig(
            max_characters=max_characters,
            temp_dir=Path(temp_dir_value),
            keep_chapters=keep_chapters,
            debug_ocr=debug_ocr,
        ),
        ocr=OcrConfig(
            mode=ocr_mode,
            language=ocr_language,
            dpi=ocr_dpi,
            psm=ocr_psm,
        ),
    )
