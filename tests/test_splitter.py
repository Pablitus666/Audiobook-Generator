from audiobook_generator.core.splitter import split_text


def test_split_without_chapters():
    chapters = split_text("Hola mundo.")

    assert len(chapters) == 1
    assert chapters[0].text == "Hola mundo."


def test_split_detects_chapters():
    text = "Capítulo 1\nPrimero.\n\nCapítulo 2\nSegundo."

    chapters = split_text(text)

    assert len(chapters) == 2
    assert chapters[0].title == "Capítulo 1"
    assert chapters[1].text == "Segundo."


def test_split_detects_chapter_with_subtitle():
    text = (
        "CAPÍTULO 1: La llegada\n"
        "Primero.\n\n"
        "CAPÍTULO 2 - El viaje\n"
        "Segundo."
    )

    chapters = split_text(text)

    assert len(chapters) == 2
    assert chapters[0].title == "CAPÍTULO 1: La llegada"
    assert chapters[1].title == "CAPÍTULO 2 - El viaje"


def test_split_detects_roman_numerals():
    text = (
        "CAPÍTULO I\n"
        "Primero.\n\n"
        "CAPÍTULO II\n"
        "Segundo."
    )

    chapters = split_text(text)

    assert len(chapters) == 2
    assert chapters[0].title == "CAPÍTULO I"
    assert chapters[1].title == "CAPÍTULO II"


def test_split_detects_chapter_in_english():
    text = (
        "CHAPTER 1\n"
        "First.\n\n"
        "CHAPTER 2: The journey\n"
        "Second."
    )

    chapters = split_text(text)

    assert len(chapters) == 2
    assert chapters[0].title == "CHAPTER 1"
    assert chapters[1].title == "CHAPTER 2: The journey"


def test_split_detects_parts_and_sections():
    text = (
        "PARTE I\n"
        "Primera parte.\n\n"
        "SECCIÓN II\n"
        "Segunda parte."
    )

    chapters = split_text(text)

    assert len(chapters) == 2
    assert chapters[0].title == "PARTE I"
    assert chapters[1].title == "SECCIÓN II"


def test_split_does_not_detect_inline_chapter():
    text = (
        "Este texto habla de Capítulo 1 pero no es un encabezado.\n\n"
        "El contenido continúa normalmente."
    )

    chapters = split_text(text)

    assert len(chapters) == 1
    assert chapters[0].title == "Documento"


def test_split_respects_max_characters_without_chapters():
    text = "Uno dos tres cuatro cinco seis siete ocho nueve diez."

    chapters = split_text(
        text,
        max_characters=20,
    )

    assert len(chapters) > 1
    assert all(
        len(chapter.text) <= 20
        for chapter in chapters
    )


def test_split_respects_max_characters_inside_chapters():
    text = (
        "Capítulo 1\n"
        "Uno dos tres cuatro cinco seis siete ocho nueve diez."
    )

    chapters = split_text(
        text,
        max_characters=20,
    )

    assert len(chapters) > 1
    assert all(
        len(chapter.text) <= 20
        for chapter in chapters
    )
    assert chapters[0].title == "Capítulo 1 - Parte 1"


def test_split_rejects_invalid_max_characters():
    try:
        split_text(
            "Hola mundo.",
            max_characters=0,
        )
    except ValueError as exc:
        assert "mayor que cero" in str(exc)
    else:
        raise AssertionError(
            "Se esperaba ValueError"
        )


def test_split_prefers_sentence_boundary():
    text = (
        "Esta es la primera oración. "
        "Segunda oración."
    )

    chapters = split_text(
        text,
        max_characters=35,
    )

    assert len(chapters) == 2
    assert chapters[0].text == (
        "Esta es la primera oración."
    )
    assert chapters[1].text == (
        "Segunda oración."
    )


def test_split_prefers_paragraph_boundary():
    text = (
        "Primero tenemos este párrafo sin punto"
        "\n\n"
        "Después tenemos este segundo párrafo "
        "que también es bastante largo."
    )

    chapters = split_text(
        text,
        max_characters=45,
    )

    assert len(chapters) >= 2
    assert chapters[0].text == (
        "Primero tenemos este párrafo sin punto"
    )


def test_split_falls_back_to_word_boundary():
    text = (
        "Uno dos tres cuatro cinco seis siete ocho."
    )

    chapters = split_text(
        text,
        max_characters=20,
    )

    assert len(chapters) > 1
    assert all(
        len(chapter.text) <= 20
        for chapter in chapters
    )


def test_split_falls_back_to_exact_character_limit():
    text = "abcdefghijklmnopqrstuv"

    chapters = split_text(
        text,
        max_characters=10,
    )

    assert [chapter.text for chapter in chapters] == [
        "abcdefghij",
        "klmnopqrst",
        "uv",
    ]