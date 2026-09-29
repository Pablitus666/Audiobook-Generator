from audiobook_generator.core.preprocessor import (
    join_wrapped_lines,
    normalize_ocr_text,
    normalize_text,
)


def test_normalize_line_endings():
    text = "Uno\r\nDos\rTres"

    result = normalize_text(text)

    assert result == "Uno\nDos\nTres"


def test_normalize_multiple_spaces():
    text = "Hola     mundo\t\tdesde Python."

    result = normalize_text(text)

    assert result == "Hola mundo desde Python."


def test_normalize_non_breaking_spaces():
    text = "Hola\u00a0\u00a0mundo desde\u00a0Python."

    result = normalize_text(text)

    assert result == "Hola mundo desde Python."


def test_normalize_blank_lines():
    text = "Primer párrafo.\n\n\n\nSegundo párrafo."

    result = normalize_text(text)

    assert result == "Primer párrafo.\n\nSegundo párrafo."


def test_normalize_form_feed():
    text = "Página uno.\fPágina dos."

    result = normalize_text(text)

    assert result == "Página uno.\nPágina dos."


def test_normalize_hyphenated_line_break():
    text = "La infor-\nmación continúa."

    result = normalize_text(text)

    assert result == "La información continúa."


def test_normalize_preserves_paragraphs():
    text = (
        "Primer párrafo.\n\n"
        "Segundo párrafo.\n\n"
        "Tercer párrafo."
    )

    result = normalize_text(text)

    assert result == text


def test_normalize_strips_outer_whitespace():
    text = "   \n\n  Hola mundo.  \n\n"

    result = normalize_text(text)

    assert result == "Hola mundo."


def test_normalize_empty_text():
    assert normalize_text("") == ""
    assert normalize_text("   ") == ""


def test_normalize_removes_bom():
    text = "\ufeffHola mundo."

    result = normalize_text(text)

    assert result == "Hola mundo."


def test_join_wrapped_lines():
    text = (
        "Este es un párrafo\n"
        "que continúa aquí.\n\n"
        "Este es otro párrafo."
    )

    result = join_wrapped_lines(text)

    assert result == (
        "Este es un párrafo que continúa aquí.\n\n"
        "Este es otro párrafo."
    )


def test_join_wrapped_lines_preserves_paragraphs():
    text = (
        "Primer párrafo\n"
        "que continúa.\n\n"
        "Segundo párrafo\n"
        "que también continúa."
    )

    result = join_wrapped_lines(text)

    assert result == (
        "Primer párrafo que continúa.\n\n"
        "Segundo párrafo que también continúa."
    )


def test_join_wrapped_lines_single_line():
    text = "Este texto ya está en una sola línea."

    result = join_wrapped_lines(text)

    assert result == text


def test_join_wrapped_lines_empty():
    assert join_wrapped_lines("") == ""
    assert join_wrapped_lines("   ") == ""


def test_normalize_removes_spaces_before_punctuation():
    text = "Hola , mundo ! Esto está bien ."

    result = normalize_text(text)

    assert result == "Hola, mundo! Esto está bien."

def test_normalize_ocr_text_fixes_known_ocr_errors():
    text = "SENOR FISCAL. LIBERACIÓON definitiva. certif'cado dispuestó."

    result = normalize_ocr_text(text)

    assert result == "SEÑOR FISCAL. LIBERACIÓN definitiva. certificado dispuesto."


def test_normalize_ocr_text_removes_ocr_garbage():
    text = "Texto � de prueba | con □ artefactos."

    result = normalize_ocr_text(text)

    assert result == "Texto de prueba con artefactos."


def test_normalize_ocr_text_does_not_apply_to_normalizer():
    text = "SENOR LIBERACIÓON"

    assert normalize_text(text) == text


def test_normalize_ocr_text_preserves_valid_accented_words():
    text = "RÍO, PAÍS y RAÚL."

    assert normalize_ocr_text(text) == text


def test_normalize_ocr_text_removes_symbol_heavy_garbage_lines():
    text = """Texto válido.

- 1 -
E =
_El
N'i

Propietario: WILMAR OSVALDO RUIZ UZQUIANO
Número Motor: HR16794900N
Placa: 4502BDF
"""

    result = normalize_ocr_text(text)

    assert "Texto válido." in result
    assert "Propietario: WILMAR OSVALDO RUIZ UZQUIANO" in result
    assert "Número Motor: HR16794900N" in result
    assert "Placa: 4502BDF" in result
    assert "E =" not in result
    assert "_El" not in result
    assert "N'i" not in result


def test_normalize_ocr_text_preserves_realistic_technical_lines():
    text = (
        "Número Chasis: 3N8CP5HDXZL455441\n"
        "Cilindrada: 1598 cc.\n"
        "4 X2 (SIMPLE)\n"
        "Peso: 1080 Kg."
    )

    assert normalize_ocr_text(text) == text


def test_normalize_ocr_text_fixes_observed_document_errors():
    text = (
        "fotocopia del QWCRPVA. "
        "principio de propcrcionalidad. "
        "Código de Procadimiento Penal. "
        "Adjunto en certif cado original."
    )

    result = normalize_ocr_text(text)

    assert result == (
        "fotocopia del CRPVA. "
        "principio de proporcionalidad. "
        "Código de Procedimiento Penal. "
        "Adjunto en certificado original."
    )


def test_normalize_ocr_text_removes_short_graphical_noise_observed_in_scans():
    text = """a A TJ
9 1s
5 5 90
YA: 50
OR NEL
NA
DIRECCIÓN DEPARTAMENTAL DE TRANSITO
Documento Identificación CI 4927893 LP
Bs. 50.00.-
"""

    result = normalize_ocr_text(text)

    assert "a A TJ" not in result
    assert "9 1s" not in result
    assert "5 5 90" not in result
    assert "YA: 50" not in result
    assert "OR NEL" not in result
    assert "NA" not in result
    assert "DIRECCIÓN DEPARTAMENTAL DE TRÁNSITO" in result
    assert "Documento Identificación CI 4927893 LP" in result
    assert "Bs. 50.00.-" in result


def test_normalize_ocr_text_fixes_crpva_prefix_artifact():
    assert normalize_ocr_text("fotocopia del dCRPVA.") == "fotocopia del CRPVA."


def test_normalize_ocr_text_applies_known_certificate_corrections():
    from audiobook_generator.core.preprocessor import normalize_ocr_text

    text = "Ne 4502-BDF\nNúmero Motor; HR16794900N\ndCRPVA"
    cleaned = normalize_ocr_text(text)

    assert "Nº 4502-BDF" in cleaned
    assert "Número Motor: HR16794900N" in cleaned
    assert "CRPVA" in cleaned


def test_normalize_ocr_text_removes_decorative_scan_symbols_without_breaking_codes():
    text = (
        "— CERTIFICADO DE PROPIEDAD —\n"
        "Placa: 4502-BDF\n"
        "CRPVA ¿ 2005630\n"
        "A = DATOS IDENTIFICACION\n"
        "4502BDFINISSAN, KICKS, ITARIJA ACTIVA\n"
    )

    result = normalize_ocr_text(text)

    assert "CERTIFICADO DE PROPIEDAD" in result
    assert "4502-BDF" in result
    assert "2005630" in result
    assert "¿" not in result
    assert " = " not in result
    assert "—" not in result


def test_normalize_ocr_text_removes_symbol_only_scan_lines():
    text = "Texto válido.\n— — —\n_ = = _\n[ ] { }\nOtro texto válido."

    result = normalize_ocr_text(text)

    assert result == "Texto válido.\n\nOtro texto válido."


def test_normalize_ocr_text_removes_leading_trailing_scan_dashes():
    text = "—Fechainicio Propiedad: 30/06/2017 —\n— VAGONETA —\nTexto 4502-BDF —"
    result = normalize_ocr_text(text)
    assert "—" not in result
    assert "Fechainicio Propiedad: 30/06/2017" in result
    assert "VAGONETA" in result
    assert "Texto 4502-BDF" in result


def test_normalize_ocr_text_removes_residual_single_letter_noise():
    text = (
        "CERTIFICA. Es\n"
        "IDENTIFICACIÓN A\n"
        "DETALLE VEHÍCULOS a\n"
        "BLANCO, 2018 á a\n"
        "1 Fecha Póliza: 29/06/2017\n"
        "e Tipo Motor: INYECCION\n"
    )

    result = normalize_ocr_text(text)

    assert "CERTIFICA. Es" not in result
    assert "IDENTIFICACIÓN A" not in result
    assert "DETALLE VEHÍCULOS a" not in result
    assert "BLANCO, 2018 á a" not in result
    assert "1 Fecha Póliza" not in result
    assert "Fecha Póliza: 29/06/2017" in result
    assert "e Tipo Motor" not in result
    assert "Tipo Motor: INYECCIÓN" in result


def test_normalize_ocr_text_corrects_plurinacional_ocr_variants():
    text = "ESTADO PLUFUNACIÓNAL DE BOLIVIA\nESTADO ELURINACIÓNAL DE BOLIVIA"
    assert normalize_ocr_text(text) == (
        "ESTADO PLURINACIONAL DE BOLIVIA\n"
        "ESTADO PLURINACIONAL DE BOLIVIA"
    )


def test_normalize_ocr_text_cleans_mixed_certificate_table_noise():
    text = (
        "ESTADO ELURINACIÓNAL DE BOLIVIA SERIE A - 22 EnCUEN\n"
        "DIRECCIÓN NACIONAL DE FISCALIZACIÓN NOO6O32\n"
        "VAGONETA, E\n"
        "4502BDFINISSAN, KICKS, ITARIJA ACTIVA rines\n"
        "CERTIFICADO DE REGISTRO DE PROPEDAD= VEHÍCULO AUTOMOTOR\n"
        "D.DATOS PROPIETARIO\n"
        "Calle Ay ricio 1\n"
        "Al ¡UTORIDAD ESPUTARIA: MAI\n"
    )
    result = normalize_ocr_text(text)
    assert "ESTADO PLURINACIONAL DE BOLIVIA" in result
    assert "EnCUEN" not in result
    assert "Nº 006032" in result
    assert "VAGONETA" in result
    assert "4502BDF NISSAN KICKS TARIJA ACTIVA" in result
    assert "PROPIEDAD" in result
    assert "Calle Ay ricio 1" not in result
    assert "ESP UTARIA" not in result


def test_tesseract_does_not_remove_low_confidence_short_words_inside_good_lines():
    from audiobook_generator.ocr.tesseract import TesseractOcrEngine

    text = "características técnicas e\nidentificatorias son:\n"
    data = {
        "text": ["características", "técnicas", "e", "identificatorias", "son:"],
        "conf": [95, 94, 20, 94, 93],
        "block_num": [1, 1, 1, 1, 1],
        "par_num": [1, 1, 1, 2, 2],
        "line_num": [1, 1, 1, 1, 1],
    }
    result = TesseractOcrEngine._filter_low_confidence_lines(text, data)
    assert "técnicas e" in result
    assert "identificatorias son:" in result


def test_normalize_ocr_text_preserves_short_words_in_valid_prose():
    text = (
        "A efectos de acreditar mi derecho propietario y legitimación activa.\n"
        "características técnicas e identificatorias son:\n"
    )
    result = normalize_ocr_text(text)
    assert "A efectos de acreditar mi derecho propietario y legitimación activa." in result
    assert "características técnicas e identificatorias son:" in result


def test_normalize_ocr_text_cleans_v026_certificate_residuals_and_restores_safe_context():
    text = (
        "características técnicas identificatorias son:\n"
        "derecho propietario legitimación activa para formular\n"
        "estrictamente provisional restrictiva.\n"
        "Marca: Nissan Numero motor: HR16794900N\n"
        "Tipo de vehiculo: Kicks\n"
        "DIRECCION DEPARTAMENTAL DE TRANSITO\n"
        "CRPVA ds 45028D\n"
        "lea 2T53NLIN\n"
        "INYECCION.. D. DATOS PROPIETARIO\n"
        "A IDENTIFICACIÓN VEHÍCULO: 7\n"
        "er A.\n"
    )
    result = normalize_ocr_text(text)
    assert "características técnicas e identificatorias son:" in result
    assert "derecho propietario y legitimación activa" in result
    assert "estrictamente provisional y restrictiva" in result
    assert "Número motor: HR16794900N" in result
    assert "Tipo de vehículo: Kicks" in result
    assert "DIRECCIÓN DEPARTAMENTAL DE TRÁNSITO" in result
    assert "CRPVA ds 45028D" not in result
    assert "2T53NLIN" not in result
    assert "INYECCIÓN." in result
    assert "D. DATOS PROPIETARIO" in result
    assert "A IDENTIFICACIÓN VEHÍCULO" not in result
    assert "er A." not in result


def test_normalize_ocr_text_cleans_v026_form_residuals():
    text = (
        "VAGONETA ELE\n"
        "GOBIERNO MUNICIPAL. LR,\n"
        "a E Usuario: JQUIROGA.TAR\n"
        "A IDENTIFICACIÓN VEHÍCULO: 7\n"
        "er A. DATOS IDENTIFICACION\n"
        "Tipo Motor: INYECCIÓN.. D. DATOS PROPIETARIO\n"
        "Dirección: CALLE HUMBERTO ARCE % S/N\n"
        "Al ¡UTORIDAD: MAI\n"
    )
    result = normalize_ocr_text(text)
    assert "VAGONETA ELE" not in result
    assert "VAGONETA" in result
    assert "GOBIERNO MUNICIPAL. LR" not in result
    assert "Usuario: JQUIROGA.TAR" in result
    assert "A IDENTIFICACIÓN VEHÍCULO: 7" not in result
    assert "er A. DATOS IDENTIFICACION" not in result
    assert "Tipo Motor: INYECCIÓN\n\nD. DATOS PROPIETARIO" in result
    assert "Dirección: CALLE HUMBERTO ARCE S/N" in result
    assert "¡UTORIDAD" not in result
