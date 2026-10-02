"""System-language detection helpers for Audiobook Generator.

This module is deliberately independent from Tkinter and the translation
engine so it can be reused by the CLI, tests, or future UI components.
"""

from __future__ import annotations

import locale
import os
from typing import Optional


SUPPORTED_LANGUAGES = frozenset({"de", "en", "es", "fr", "it", "ja", "pt", "ru", "zh"})
DEFAULT_LANGUAGE = "en"


def normalize_language(language: str | None) -> str | None:
    """Normalize a locale/language identifier to a supported two-letter code."""
    if not language:
        return None

    value = str(language).strip().lower().replace("_", "-")
    if not value:
        return None

    code = value.split("-", 1)[0]
    return code if code in SUPPORTED_LANGUAGES else None


def _windows_user_language() -> Optional[str]:
    """Read the Windows user's configured UI locale when available."""
    if os.name != "nt":
        return None

    try:
        import ctypes

        buffer = ctypes.create_unicode_buffer(85)
        length = ctypes.windll.kernel32.GetUserDefaultLocaleName(buffer, len(buffer))
        if length:
            return normalize_language(buffer.value)
    except (AttributeError, OSError, TypeError):
        pass

    return None


def get_system_language() -> str:
    """Return the best supported language for the current computer.

    Windows' user locale is preferred.  Python's locale information and common
    environment variables are used as portable fallbacks.  Unsupported or
    unavailable locales always fall back to English.
    """
    # Explicit override is useful for testing and for future user preferences.
    override = normalize_language(os.environ.get("AUDIOBOOK_GENERATOR_LANGUAGE"))
    if override:
        return override

    windows_language = _windows_user_language()
    if windows_language:
        return windows_language

    for candidate in (
        locale.getlocale()[0],
        os.environ.get("LC_ALL"),
        os.environ.get("LC_MESSAGES"),
        os.environ.get("LANG"),
    ):
        language = normalize_language(candidate)
        if language:
            return language

    return DEFAULT_LANGUAGE
