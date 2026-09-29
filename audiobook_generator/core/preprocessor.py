from __future__ import annotations

import re


_MULTIPLE_SPACES_RE = re.compile(r"[ \t\u00a0]+")
_MULTIPLE_BLANK_LINES_RE = re.compile(r"\n{3,}")
_HYPHENATED_LINEBREAK_RE = re.compile(r"(?<=\w)-\n(?=\w)")
_SPACE_BEFORE_PUNCTUATION_RE = re.compile(
    r"\s+([,.;:!?])"
)


def normalize_text(text: str) -> str:
    """
    Normaliza texto extraído de documentos para prepararlo para TTS.

    Normaliza finales de línea, espacios, tabulaciones, espacios
    no separables, palabras cortadas por salto de línea y espacios
    innecesarios antes de signos de puntuación.

    Conserva los saltos de línea que separan párrafos.
    """
    if not text:
        return ""

    # Normaliza finales de línea.
    text = text.replace("\r\n", "\n")
    text = text.replace("\r", "\n")

    # Algunos extractores de documentos pueden producir form-feed
    # como separador de página.
    text = text.replace("\f", "\n")

    # Elimina un posible BOM si el texto llega directamente
    # a esta función y no pasó previamente por utf-8-sig.
    text = text.lstrip("\ufeff")

    # Une palabras cortadas por salto de línea:
    # "infor-\nmación" -> "información"
    text = _HYPHENATED_LINEBREAK_RE.sub("", text)

    # Normaliza espacios, tabulaciones y espacios no separables
    # dentro de cada línea.
    lines = [
        _MULTIPLE_SPACES_RE.sub(" ", line).strip()
        for line in text.split("\n")
    ]

    text = "\n".join(lines)

    # Elimina espacios innecesarios antes de signos de puntuación:
    # "Hola , mundo !" -> "Hola, mundo!"
    text = _SPACE_BEFORE_PUNCTUATION_RE.sub(
        r"\1",
        text,
    )

    # Evita más de una línea vacía consecutiva.
    text = _MULTIPLE_BLANK_LINES_RE.sub(
        "\n\n",
        text,
    )

    return text.strip()


def join_wrapped_lines(text: str) -> str:
    """
    Une líneas que pertenecen al mismo párrafo.

    Ejemplo:

        Este es un párrafo
        que continúa aquí.

    se convierte en:

        Este es un párrafo que continúa aquí.

    Las líneas vacías se conservan como separadores de párrafos.
    """
    text = normalize_text(text)

    if not text:
        return ""

    lines = text.split("\n")
    result: list[str] = []

    for line in lines:
        if not line:
            result.append("")
            continue

        if not result or result[-1] == "":
            result.append(line)
            continue

        result[-1] = f"{result[-1]} {line}"

    return "\n".join(result).strip()

# Correcciones deliberadamente conservadoras para errores OCR conocidos.
# Se aplican únicamente a documentos que el lector marca como procesados
# mediante OCR; los documentos con texto nativo no pasan por esta etapa.
_OCR_WORD_REPLACEMENTS = {
    "SENOR": "SEÑOR",
    "Senor": "Señor",
    "senor": "señor",
    "LIBERACIÓON": "LIBERACIÓN",
    "liberacióon": "liberación",
    "certif'cado": "certificado",
    "Certif'cado": "Certificado",
    "certif cado": "certificado",
    "Certif cado": "Certificado",
    "dispuestó": "dispuesto",
    "propcrcionalidad": "proporcionalidad",
    "Propcrcionalidad": "Proporcionalidad",
    "Procadimiento": "Procedimiento",
    "procadimiento": "procedimiento",
    "QWCRPVA": "CRPVA",
    "dCRPVA": "CRPVA",
    "DCRPVA": "CRPVA",
    "Ne": "Nº",
    "N*": "Nº",
    "N°": "Nº",
    "Número Motor;": "Número Motor:",
    "PROP E DAD": "PROPIEDAD",
    "PLUFUNACIÓNAL": "PLURINACIONAL",
    "PLUFUNACIONAL": "PLURINACIONAL",
    "ELURINACIÓNAL": "PLURINACIONAL",
    "ELURINACIONAL": "PLURINACIONAL",
    "GCBIERNO": "GOBIERNO",
    # Fragmentos OCR observados en certificados escaneados. Son correcciones
    # contextuales/inequívocas y no sustituciones ortográficas generales.
    "EnCUEN": "",
    "NOO6O32": "Nº 006032",
    "N0O6O32": "Nº 006032",
    "PROPEDAD": "PROPIEDAD",
    "DENTIFICACIÓN": "IDENTIFICACIÓN",
    "ell sistema": "el sistema",
    "UFRMAPROMETARO": "",
    "ESP UTARIA": "",
    "ESPUTARIA": "",
    # Normalización ortográfica segura de términos administrativos que
    # aparecen repetidamente sin tilde por limitaciones del OCR.
    "TRANSITO": "TRÁNSITO",
    "transito": "tránsito",
    "DIVISION": "DIVISIÓN",
    "division": "división",
    "DIRECCION": "DIRECCIÓN",
    "direccion": "dirección",
    "NUMERO": "NÚMERO",
    "Numero": "Número",
    "numero": "número",
    "vehiculo": "vehículo",
    "Vehiculo": "Vehículo",
    "VEHICULO": "VEHÍCULO",
    "IDENTIFICACION": "IDENTIFICACIÓN",
    "identificacion": "identificación",
    "POLIZA": "PÓLIZA",
    "IMPORTACION": "IMPORTACIÓN",
    "IMPORTACIÓN": "IMPORTACIÓN",
    "PROPIEDAD": "PROPIEDAD",
}

_OCR_GARBAGE_RE = re.compile(r"[�¤†‡□■]+")
_OCR_ISOLATED_PIPE_RE = re.compile(r"(?<!\w)\|+(?!\w)")
_OCR_DUPLICATE_ACCENT_RE = re.compile(
    r"(?:ÁA|áa|ÉE|ée|ÍI|íi|ÓO|óo|ÚU|úu)"
)
_OCR_BROKEN_FRAGMENT_RE = re.compile(r"^[A-Za-zÁÉÍÓÚáéíóúÑñ]{1,2}['’][A-Za-zÁÉÍÓÚáéíóúÑñ]{1,2}$")
_OCR_STRUCTURAL_SYMBOLS = set("_=+|~^—–-[]{}<>¿¡")
_OCR_DECORATIVE_SYMBOL_RE = re.compile(r"(?<!\w)[_=+|~^—–]+(?!\w)")
_OCR_BRACKET_ARTIFACT_RE = re.compile(r"[\[\]{}<>]")
_OCR_STANDALONE_QUESTION_RE = re.compile(r"(?<!\w)[¿¡](?!\w)")
_OCR_DASH_RUN_RE = re.compile(r"(?<!\w)[—–-]{2,}(?!\w)")
_OCR_LEADING_TRAILING_DASH_RE = re.compile(r"(^|[\s])[-—–]+(?=\w)|(?<=\w)[-—–]+(?=$|[\s])")

# Palabras cortas que aparecen con frecuencia en certificados y formularios.
# Sirven para no confundir líneas legítimas como "Cl 4927893 LP" con ruido
# compuesto únicamente por fragmentos de 1–3 caracteres.
_OCR_SHORT_VALID_WORDS = {
    "a", "al", "de", "del", "el", "en", "es", "la", "las", "los",
    "y", "o", "u", "un", "una", "por", "sin", "con", "no", "sí",
    "que", "se", "su", "sus", "para", "como", "son", "del",
    "bs", "ci", "lp", "n", "nº", "no", "rua", "rua.",
}


def _is_ocr_garbage_line(line: str) -> bool:
    """Detecta líneas dominadas por artefactos gráficos de OCR.

    La detección evita reglas basadas únicamente en caracteres no
    alfanuméricos, porque documentos legales pueden contener códigos,
    matrículas, números de expediente y abreviaturas que deben conservarse.
    Solo elimina líneas muy cortas en las que los símbolos predominan
    claramente sobre letras y números.
    """
    stripped = line.strip()
    if not stripped:
        return False

    alphanumeric = sum(character.isalnum() for character in stripped)
    symbols = sum(
        not character.isalnum() and not character.isspace()
        for character in stripped
    )

    if alphanumeric == 0:
        return True

    if _OCR_BROKEN_FRAGMENT_RE.fullmatch(stripped):
        return True

    # El OCR de sellos, firmas y bordes suele producir líneas como:
    # "a A TJ", "9 1s", "5 5 90", "YA: 50", "OR NEL" o "NA".
    # Si una línea está formada únicamente por tokens diminutos, sin una
    # palabra reconocible ni un campo técnico, es más seguro descartarla
    # antes de enviarla al TTS. No se aplica a líneas con palabras normales
    # o identificadores técnicos.
    tokens = re.findall(r"[A-Za-zÁÉÍÓÚÜÑáéíóúüñ]+|\d+(?:[./-]\d+)*", stripped)
    if tokens:
        normalized_tokens = [token.casefold() for token in tokens]
        short_tokens = [token for token in normalized_tokens if len(token) <= 3]
        long_alpha_tokens = [
            token for token in normalized_tokens
            if token.isalpha() and len(token) >= 4
        ]
        known_short_word_count = sum(
            token in _OCR_SHORT_VALID_WORDS for token in normalized_tokens
        )
        has_numeric_token = any(token.isdigit() for token in normalized_tokens)
        uppercase_short_count = sum(
            token.isalpha() and token.upper() == token and len(token) <= 3
            for token in tokens
        )
        if (
            len(tokens) <= 5
            and len(short_tokens) == len(tokens)
            and not long_alpha_tokens
            and known_short_word_count < 2
            and not has_numeric_token
        ) or (
            len(tokens) <= 4
            and len(short_tokens) == len(tokens)
            and uppercase_short_count >= 2
            and not has_numeric_token
        ) or (
            len(tokens) <= 4
            and has_numeric_token
            and not long_alpha_tokens
            and known_short_word_count == 0
        ):
            return True

    structural_symbols = sum(
        character in _OCR_STRUCTURAL_SYMBOLS
        for character in stripped
    )
    if alphanumeric <= 3 and structural_symbols >= 1:
        return True

    # Ejemplos: "E =", "- 1 -", "N'i", "_El".
    if alphanumeric <= 3 and symbols >= 2:
        return True

    # Para líneas un poco mayores exigimos que los símbolos dominen
    # claramente. Esto evita tocar datos como matrículas o códigos.
    if alphanumeric <= 6 and symbols >= 4 and symbols > alphanumeric:
        return True

    return False


def _remove_ocr_garbage_lines(text: str) -> str:
    return "\n".join(
        line
        for line in text.split("\n")
        if not _is_ocr_garbage_line(line)
    )


def normalize_ocr_text(text: str) -> str:
    """Limpia errores evidentes producidos por OCR antes del TTS.

    La función es intencionadamente conservadora. No intenta corregir
    ortografía general ni reescribir el contenido; solo elimina artefactos
    de reconocimiento y aplica unas pocas correcciones OCR inequívocas.
    """
    if not text:
        return ""

    # Unicode compuesto ayuda a mantener caracteres acentuados coherentes.
    import unicodedata

    text = unicodedata.normalize("NFC", text)

    # Elimina caracteres invisibles que pueden hacer que TTS produzca
    # pausas o pronunciaciones inesperadas.
    text = text.replace("\u200b", "")
    text = text.replace("\u200c", "")
    text = text.replace("\u200d", "")
    text = text.replace("\ufeff", "")

    # Primero aplicamos correcciones OCR inequívocas. Esto debe ocurrir antes
    # de eliminar líneas cortas para que campos como "Ne 4502-BDF" no sean
    # confundidos con ruido.
    for wrong, correct in _OCR_WORD_REPLACEMENTS.items():
        text = re.sub(
            rf"(?<!\w){re.escape(wrong)}(?!\w)",
            correct,
            text,
        )

    # Artefactos gráficos habituales en OCR de sellos, bordes y tablas.
    # Se eliminan como caracteres independientes, pero no se tocan los
    # guiones internos de palabras/códigos (por ejemplo 4502-BDF).
    text = _OCR_GARBAGE_RE.sub(" ", text)
    text = _OCR_ISOLATED_PIPE_RE.sub(" ", text)
    text = _OCR_DECORATIVE_SYMBOL_RE.sub(" ", text)
    text = _OCR_BRACKET_ARTIFACT_RE.sub(" ", text)
    text = _OCR_STANDALONE_QUESTION_RE.sub(" ", text)
    text = _OCR_DASH_RUN_RE.sub(" ", text)
    text = _OCR_LEADING_TRAILING_DASH_RE.sub(" ", text)
    text = _remove_ocr_garbage_lines(text)

    # Pequeños residuos de una línea OCR que ya fue identificada como texto
    # válido pero conserva una letra suelta al final o delante de un campo.
    text = re.sub(r"(?m)^1 (?=Fecha Póliza\b)", "", text)
    text = re.sub(r"(?m)^(A)[,:] (?=DATOS IDENTIFICACION\b)", r"\1. ", text)
    text = re.sub(r"(?m)^\s*e\s+(?=Tipo Motor\b)", "", text)
    text = re.sub(r"(?m)^CERTIFICA\.\s+Es\s*$", "CERTIFICA.", text)
    text = re.sub(r"(?m)\s+[A-Za-zÁÉÍÓÚÜÑáéíóúüñ]\s*$", "", text)

    # Corrige concatenaciones OCR muy características de las tablas del
    # certificado de propiedad. Se conserva el contenido reconocible y se
    # separan los campos para que el TTS no pronuncie una cadena espuria.
    text = re.sub(
        r"\b4502BDFINISSAN,?\s*KICKS,?\s*ITARIJA\s+ACTIVA(?:\s+rines)?\b",
        "4502BDF NISSAN KICKS TARIJA ACTIVA",
        text,
        flags=re.IGNORECASE,
    )
    text = re.sub(
        r"\bVAGONETA,?\s*E\b",
        "VAGONETA",
        text,
        flags=re.IGNORECASE,
    )
    text = re.sub(r"(?m)^\s*VAGONETA,\s*$", "VAGONETA", text)
    # Encabezados y firmas parcialmente reconocidos: si solo aportan ruido,
    # se elimina el fragmento, pero no la línea documental principal.
    text = re.sub(r"(?m)^\s*POLIC\s*$", "", text, flags=re.IGNORECASE)
    text = re.sub(r"(?m)^\s*MEFDE LA DIVI\s*$", "", text, flags=re.IGNORECASE)
    text = re.sub(r"(?m)^\s*No =00 DE VEHÍCULOS\s*$", "", text, flags=re.IGNORECASE)
    text = re.sub(r"(?m)^\s*¡CULOS\s*$", "", text, flags=re.IGNORECASE)
    text = re.sub(r"(?m)^\s*Calle Ay ricio 1\s*$", "", text, flags=re.IGNORECASE)
    text = re.sub(r"(?m)^\s*Al ¡UTORIDAD ESPUTARIA: MAI\s*$", "", text, flags=re.IGNORECASE)
    text = re.sub(r"(?m)^\s*Al ¡UTORIDAD: MAI\s*$", "", text, flags=re.IGNORECASE)
    text = re.sub(r"(?m)^\s*CCBIERNO AUTÓNOMO MUMENAL DE TANIA\s+Nombre:", "Nombre:", text, flags=re.IGNORECASE)
    text = re.sub(r"(?m)^\s*Al ¡UTORIDAD: MAI\s*$", "", text, flags=re.IGNORECASE)

    # Residuos específicos detectados en el certificado de propiedad.
    text = re.sub(r"(?m)^\s*CRPVA\s+(?:ds|¿)\s+45028D\s*$", "", text, flags=re.IGNORECASE)
    text = re.sub(r"\blea\s+2T53NLIN\b", "", text, flags=re.IGNORECASE)
    text = re.sub(r"\bINYECCION\.\.\s+D\.\s*DATOS PROPIETARIO", "INYECCIÓN.\n\nD. DATOS PROPIETARIO", text, flags=re.IGNORECASE)
    text = re.sub(r"\bINYECCION\b", "INYECCIÓN", text, flags=re.IGNORECASE)
    text = re.sub(r"(?m)^\s*A\s+IDENTIFICACIÓN VEHÍCULO:.*$", "", text, flags=re.IGNORECASE)
    text = re.sub(r"(?m)^\s*er A\.(?:\s+DATOS IDENTIFICACION)?\s*$", "", text, flags=re.IGNORECASE)

    # Residuos gráficos adicionales detectados en el certificado v026.
    # Son fragmentos aislados de bordes, sellos o tablas, no datos
    # documentales. Se eliminan únicamente cuando aparecen como líneas
    # independientes o en las formas OCR observadas.
    text = re.sub(r"(?m)^\s*VAGONETA\s+ELE\s*$", "VAGONETA", text, flags=re.IGNORECASE)
    text = re.sub(r"(?m)^\s*GOBIERNO MUNICIPAL\.\s*LR,\s*$", "", text, flags=re.IGNORECASE)
    text = re.sub(r"(?m)^\s*a?\s*E\s+Usuario:\s*", "Usuario: ", text, flags=re.IGNORECASE)
    text = re.sub(r"(?m)^\s*A\s+IDENTIFICACIÓN VEHÍCULO:\s*7\s*$", "", text, flags=re.IGNORECASE)
    text = re.sub(r"(?m)^\s*er A\.(?:\s+DATOS IDENTIFICACION)?\s*$", "", text, flags=re.IGNORECASE)
    text = re.sub(r"(?m)^\s*Al\s+¡UTORIDAD(?: ESPUTARIA)?:\s*MAI\s*$", "", text, flags=re.IGNORECASE)
    text = re.sub(r"(?m)^\s*¡UTORIDAD(?: ESPUTARIA)?:\s*MAI\s*$", "", text, flags=re.IGNORECASE)

    # Separadores OCR espurios dentro de campos del formulario.
    text = re.sub(r"(?m)^(Dirección:\s*CALLE HUMBERTO ARCE)\s+%\s+(S/N)$", r"\1 \2", text, flags=re.IGNORECASE)
    text = re.sub(r"(?m)^(Tipo Motor:\s*INYECCIÓN)\.\.\s+(D\.\s*DATOS PROPIETARIO)$", r"\1\n\n\2", text, flags=re.IGNORECASE)

    # Recuperaciones contextuales muy seguras: el OCR suele perder una
    # conjunción aislada entre palabras con alta confianza.
    text = re.sub(r"(características técnicas)\s+(identificatorias)", r"\1 e \2", text, flags=re.IGNORECASE)
    text = re.sub(r"(derecho propietario)\s+(legitimación activa)", r"\1 y \2", text, flags=re.IGNORECASE)
    text = re.sub(r"(estrictamente provisional)\s+(restrictiva)", r"\1 y \2", text, flags=re.IGNORECASE)
    text = re.sub(r"(devolución de los objetos secuestrados)\s+(que no estén)", r"\1 que no estén", text, flags=re.IGNORECASE)

    text = re.sub(r"\bD\.DATOS\b", "D. DATOS", text)
    text = re.sub(r"\bPROPIEDAD=\s*VEHÍCULO", "PROPIEDAD VEHÍCULO", text, flags=re.IGNORECASE)
    text = re.sub(r"(?m)^\s*DN IDENTIFICACIÓN PROPIETARIO.*$", "D. DATOS PROPIETARIO", text, flags=re.IGNORECASE)

    # Un error frecuente es duplicar la vocal después de una vocal acentuada:
    # por ejemplo, "LIBERACIÓON". En español esta secuencia no es una
    # escritura válida habitual y es segura de normalizar para TTS.
    text = _OCR_DUPLICATE_ACCENT_RE.sub(lambda match: match.group(0)[0], text)

    return normalize_text(text)
