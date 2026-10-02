"""JSON-based localization engine for Audiobook Generator."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .locale_utils import DEFAULT_LANGUAGE, SUPPORTED_LANGUAGES, get_system_language, normalize_language


class Localization:
    """Load and serve translated GUI strings from ``assets/locales``.

    The engine is intentionally UI-agnostic.  Widgets only need the ``t``
    method, while language detection, file loading, fallback handling, and
    formatting stay in this module.
    """

    def __init__(
        self,
        language: str | None = None,
        locales_dir: Path | None = None,
        default_language: str = DEFAULT_LANGUAGE,
    ) -> None:
        self.locales_dir = locales_dir or self._default_locales_dir()
        self.default_language = normalize_language(default_language) or DEFAULT_LANGUAGE
        requested = normalize_language(language)
        self.language = requested or get_system_language()
        self._cache: dict[str, dict[str, str]] = {}
        self._translations = self._load(self.language)
        self._fallback = self._load(self.default_language)

    @staticmethod
    def _default_locales_dir() -> Path:
        """Return the project's shared ``assets/locales`` directory."""
        return Path(__file__).resolve().parents[2] / "assets" / "locales"

    def _load(self, language: str) -> dict[str, str]:
        language = normalize_language(language) or self.default_language
        cached = self._cache.get(language)
        if cached is not None:
            return cached

        path = self.locales_dir / f"{language}.json"
        try:
            with path.open("r", encoding="utf-8") as handle:
                data: Any = json.load(handle)
        except (OSError, json.JSONDecodeError):
            data = {}

        if not isinstance(data, dict):
            data = {}

        translations = {str(key): str(value) for key, value in data.items()}
        self._cache[language] = translations
        return translations

    def set_language(self, language: str) -> str:
        """Switch the active language and return the normalized language code."""
        normalized = normalize_language(language) or self.default_language
        self.language = normalized
        self._translations = self._load(normalized)
        return self.language

    def t(self, key: str, **kwargs: Any) -> str:
        """Return a translated string, falling back to English when needed."""
        value = self._translations.get(key)
        if value is None:
            value = self._fallback.get(key)
        if value is None:
            # Returning the key makes missing translations immediately visible
            # during development without crashing the application.
            return key

        if kwargs:
            try:
                return value.format(**kwargs)
            except (KeyError, IndexError, ValueError):
                # A malformed translation should not break the GUI.
                return value
        return value

    def has(self, key: str) -> bool:
        """Return whether a key exists in the active or fallback locale."""
        return key in self._translations or key in self._fallback


__all__ = [
    "DEFAULT_LANGUAGE",
    "SUPPORTED_LANGUAGES",
    "Localization",
    "get_system_language",
]
