from __future__ import annotations

import io
import shutil
from statistics import mean
from difflib import SequenceMatcher
import re

from audiobook_generator.core.errors import OcrError, OcrNotAvailableError
from audiobook_generator.ocr.base import OcrEngine


# La confianza media de Tesseract puede caer en documentos con sellos,
# bordes y tablas aunque el texto principal esté bien segmentado.
# Por eso no usamos la confianza por sí sola para sustituir una salida
# razonablemente completa: en documentos legales PSM 3 suele conservar
# mejor el orden y el contenido que PSM 6.
_MIN_TEXT_FOR_FALLBACK = 80
_FALLBACK_PSM = 6
# Una salida muy corta y con baja confianza suele ser ruido de sellos,
# firmas, fondos o páginas gráficas. No debe entrar al audiolibro.
_MIN_ACCEPTABLE_LENGTH = 80
_MIN_ACCEPTABLE_CONFIDENCE = 50.0
# Una página con muchísimo texto pero confianza muy baja suele ser un fondo,
# firma o gráfico que Tesseract está interpretando como caracteres.
# Se descarta solo cuando ambas señales coinciden para evitar perder
# documentos escaneados legítimos.
_MIN_PAGE_CONFIDENCE = 40.0
_MIN_HIGH_CONFIDENCE_RATIO = 0.25
# Las páginas con sellos, firmas y fondos generan líneas enteras de OCR con
# confianza muy baja. Es más seguro eliminar esas líneas completas que
# enviarlas al TTS. El umbral es deliberadamente conservador: las líneas
# normales del documento suelen quedar muy por encima de 50.
_MIN_LINE_CONFIDENCE = 50.0


class TesseractOcrEngine(OcrEngine):
    """Motor OCR basado en Tesseract a través de pytesseract.

    Usa el PSM configurado como primera pasada. Para páginas escaneadas
    con segmentación difícil, realiza una segunda pasada conservadora con
    PSM 6 cuando la confianza de Tesseract es baja o el resultado es
    anormalmente corto. Se conserva el resultado con mejor combinación de
    confianza y cantidad de texto útil.
    """

    def __init__(
        self,
        language: str = "spa",
        tesseract_cmd: str | None = None,
        psm: int = 3,
    ) -> None:
        self.language = language
        self.tesseract_cmd = tesseract_cmd
        if not 1 <= psm <= 13:
            raise ValueError("psm debe estar entre 1 y 13.")
        self.psm = psm

    def is_available(self) -> bool:
        if self.tesseract_cmd:
            return shutil.which(self.tesseract_cmd) is not None

        return shutil.which("tesseract") is not None

    @staticmethod
    def _confidence(data: dict[str, list[object]]) -> float:
        values: list[float] = []
        for value in data.get("conf", []):
            try:
                confidence = float(value)
            except (TypeError, ValueError):
                continue
            if confidence >= 0:
                values.append(confidence)
        return mean(values) if values else 0.0

    @staticmethod
    def _useful_length(text: str) -> int:
        return sum(character.isalnum() for character in text)

    @staticmethod
    def _line_signature(text: str) -> str:
        return re.sub(r"[^\wáéíóúüñÁÉÍÓÚÜÑ]+", "", text.casefold())

    @classmethod
    def _filter_low_confidence_lines(
        cls,
        text: str,
        data: dict[str, list[object]],
    ) -> str:
        """Elimina líneas que Tesseract identifica como ruido gráfico.

        No filtra palabras individuales: eso puede destruir códigos, placas o
        números legítimos. Solo elimina una línea completa cuando la confianza
        media de esa línea es muy baja. La comparación tolera pequeñas
        diferencias entre ``image_to_string`` e ``image_to_data``.
        """
        groups: dict[tuple[int, int, int], list[float]] = {}
        texts: dict[tuple[int, int, int], list[str]] = {}
        for i, raw in enumerate(data.get("text", [])):
            token = str(raw).strip()
            if not token:
                continue
            try:
                confidence = float(data.get("conf", [])[i])
            except (IndexError, TypeError, ValueError):
                continue
            key = (
                int(data.get("block_num", [0])[i]),
                int(data.get("par_num", [0])[i]),
                int(data.get("line_num", [0])[i]),
            )
            groups.setdefault(key, []).append(confidence)
            texts.setdefault(key, []).append(token)

        bad_signatures = {
            cls._line_signature(" ".join(texts[key]))
            for key, values in groups.items()
            if values and mean(values) < _MIN_LINE_CONFIDENCE
        }
        if not bad_signatures:
            return text

        kept: list[str] = []
        for line in text.splitlines():
            signature = cls._line_signature(line)
            if not signature:
                kept.append(line)
                continue
            if signature in bad_signatures:
                continue
            # image_to_string puede unir/separar algún espacio respecto a
            # image_to_data. Solo aplicamos una coincidencia difusa a líneas
            # cortas, donde eliminar un falso positivo tiene poco coste.
            if len(signature) >= 8 and any(
                SequenceMatcher(None, signature, bad).ratio() >= 0.90
                for bad in bad_signatures
                if abs(len(signature) - len(bad)) <= 4
            ):
                continue

            # No eliminamos tokens individuales dentro de una línea que ya
            # tiene confianza global suficiente. En documentos legales, una
            # palabra corta como "a", "e", "de" o "y" puede tener menor
            # confianza que el resto de la línea y seguir siendo contenido
            # perfectamente válido. La limpieza de fragmentos internos se
            # hace después, en normalize_ocr_text(), mediante reglas
            # contextuales.
            kept.append(line)

        return "\n".join(kept)

    def recognize(self, image_bytes: bytes) -> str:
        if not self.is_available():
            raise OcrNotAvailableError(
                "Tesseract OCR no está disponible. "
                "Instala los componentes de OCR y asegúrate de que "
                "el ejecutable 'tesseract' esté disponible en PATH."
            )

        try:
            from PIL import Image
            import pytesseract
        except ImportError as exc:
            raise OcrNotAvailableError(
                "Las dependencias Python de OCR no están instaladas. "
                "Instala: pip install -r requirements-ocr.txt"
            ) from exc

        if self.tesseract_cmd:
            pytesseract.pytesseract.tesseract_cmd = self.tesseract_cmd

        try:
            with Image.open(io.BytesIO(image_bytes)) as image:
                primary_config = f"--oem 1 --psm {self.psm}"
                primary_text = pytesseract.image_to_string(
                    image,
                    lang=self.language,
                    config=primary_config,
                ).strip()

                # La segunda pasada solo se ejecuta cuando hay una señal
                # objetiva de que la segmentación inicial puede ser mala.
                # Esto evita duplicar el coste OCR en páginas normales.
                try:
                    primary_data = pytesseract.image_to_data(
                        image,
                        lang=self.language,
                        config=primary_config,
                        output_type=pytesseract.Output.DICT,
                    )
                    primary_confidence = self._confidence(primary_data)
                except Exception:
                    primary_confidence = 100.0

                # Elimina líneas completas con confianza muy baja (sellos,
                # firmas, bordes y fondos). Esto ataca directamente el ruido
                # que no puede detectarse por caracteres después del OCR.
                primary_text = self._filter_low_confidence_lines(
                    primary_text,
                    primary_data,
                ).strip()

                primary_length = self._useful_length(primary_text)

                # Descarta páginas cuyo OCR solo encontró unos pocos
                # caracteres con confianza muy baja. Esto evita incorporar
                # al audiolibro páginas de sellos/fondos/firmas que Tesseract
                # interpreta como texto.
                if (
                    primary_length < _MIN_ACCEPTABLE_LENGTH
                    and primary_confidence < _MIN_ACCEPTABLE_CONFIDENCE
                ):
                    return ""

                # Caso distinto: algunas páginas gráficas generan cientos de
                # caracteres, pero casi todos tienen confianza baja. En ese
                # escenario la longitud deja de ser una señal útil.
                # Volvemos a usar image_to_data y exigimos que al menos una
                # fracción mínima de las palabras tenga confianza >= 50.
                try:
                    confidences = []
                    for value in primary_data.get("conf", []):
                        try:
                            confidence = float(value)
                        except (TypeError, ValueError):
                            continue
                        if confidence >= 0:
                            confidences.append(confidence)
                    high_confidence_ratio = (
                        sum(c >= _MIN_ACCEPTABLE_CONFIDENCE for c in confidences)
                        / len(confidences)
                        if confidences
                        else 0.0
                    )
                except Exception:
                    high_confidence_ratio = 1.0

                if (
                    primary_length >= _MIN_ACCEPTABLE_LENGTH
                    and primary_confidence < _MIN_PAGE_CONFIDENCE
                    and high_confidence_ratio < _MIN_HIGH_CONFIDENCE_RATIO
                ):
                    return ""

                needs_fallback = (
                    self.psm != _FALLBACK_PSM
                    and primary_length < _MIN_TEXT_FOR_FALLBACK
                )

                if not needs_fallback:
                    return primary_text

                fallback_config = f"--oem 1 --psm {_FALLBACK_PSM}"
                fallback_text = pytesseract.image_to_string(
                    image,
                    lang=self.language,
                    config=fallback_config,
                ).strip()

                try:
                    fallback_data = pytesseract.image_to_data(
                        image,
                        lang=self.language,
                        config=fallback_config,
                        output_type=pytesseract.Output.DICT,
                    )
                    fallback_confidence = self._confidence(fallback_data)
                except Exception:
                    fallback_confidence = 0.0

                # Solo aceptamos el fallback si recupera claramente más texto
                # útil. La confianza media no decide por sí sola porque los
                # certificados escaneados contienen sellos, líneas y tablas que
                # penalizan artificialmente esa métrica.
                primary_length = self._useful_length(primary_text)
                fallback_length = self._useful_length(fallback_text)

                if fallback_length >= max(primary_length + 80, int(primary_length * 1.35)):
                    return fallback_text

                return primary_text

        except Exception as exc:
            raise OcrError(
                f"no se pudo ejecutar OCR con Tesseract: {exc}"
            ) from exc
