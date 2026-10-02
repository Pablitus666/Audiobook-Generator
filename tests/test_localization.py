import json
from pathlib import Path

from audiobook_generator.core.localization import Localization
from audiobook_generator.core.locale_utils import get_system_language, normalize_language


LOCALES = Path(__file__).resolve().parents[1] / "assets" / "locales"


def test_all_locale_files_have_same_keys():
    files = sorted(LOCALES.glob("*.json"))
    assert {p.stem for p in files} == {"de", "en", "es", "fr", "it", "ja", "pt", "ru", "zh"}
    keys = []
    for path in files:
        with path.open(encoding="utf-8") as handle:
            data = json.load(handle)
        keys.append(set(data))
    assert all(item == keys[0] for item in keys[1:])


def test_localization_loads_requested_language():
    i18n = Localization(language="es", locales_dir=LOCALES)
    assert i18n.language == "es"
    assert i18n.t("section.document") == "Documento"
    assert i18n.t("button.browse") == "Examinar"


def test_localization_falls_back_to_english():
    i18n = Localization(language="zh", locales_dir=LOCALES)
    assert i18n.t("button.close")
    assert i18n.t("missing.key") == "missing.key"


def test_language_normalization():
    assert normalize_language("es_ES") == "es"
    assert normalize_language("zh-CN") == "zh"
    assert normalize_language("pt-BR") == "pt"
    assert normalize_language("xx_YY") is None


def test_system_language_is_supported():
    assert get_system_language() in {"de", "en", "es", "fr", "it", "ja", "pt", "ru", "zh"}
