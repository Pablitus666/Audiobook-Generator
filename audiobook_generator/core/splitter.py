from __future__ import annotations

import re

from .models import Chapter


_CHAPTER_RE = re.compile(
    r"(?im)^"
    r"(?:"
    r"cap[ií]tulo"
    r"|chapter"
    r"|parte"
    r"|secci[oó]n"
    r")"
    r"\s+"
    r".+?"
    r"\s*$"
)


_SENTENCE_END_RE = re.compile(
    r"[.!?…]+(?:[\"”»’']+)?(?=\s|$)"
)


def _split_long_text(
    text: str,
    max_characters: int,
) -> list[str]:
    if max_characters <= 0 or len(text) <= max_characters:
        return [text]

    chunks: list[str] = []
    remaining = text.strip()

    while remaining:
        if len(remaining) <= max_characters:
            chunks.append(remaining)
            break

        window = remaining[: max_characters + 1]

        # 1. Preferir el final de una oración.
        sentence_cut = 0

        for match in _SENTENCE_END_RE.finditer(window):
            end = match.end()

            if end <= max_characters:
                sentence_cut = end

        if sentence_cut > 0:
            chunks.append(
                remaining[:sentence_cut].strip()
            )
            remaining = remaining[sentence_cut:].strip()
            continue

        # 2. Si no cabe una oración completa,
        #    intentar cortar en un párrafo.
        paragraph_cut = remaining.rfind(
            "\n\n",
            0,
            max_characters + 1,
        )

        if paragraph_cut > 0:
            chunks.append(
                remaining[:paragraph_cut].strip()
            )
            remaining = remaining[paragraph_cut:].strip()
            continue

        # 3. Si tampoco hay un párrafo adecuado,
        #    cortar en el último espacio disponible.
        word_cut = remaining.rfind(
            " ",
            0,
            max_characters + 1,
        )

        if word_cut > 0:
            chunks.append(
                remaining[:word_cut].strip()
            )
            remaining = remaining[word_cut:].strip()
            continue

        # 4. Último recurso: cortar exactamente
        #    en el límite de caracteres.
        chunks.append(
            remaining[:max_characters].strip()
        )
        remaining = remaining[max_characters:].strip()

    return chunks


def split_text(
    text: str,
    default_title: str = "Documento",
    max_characters: int | None = None,
) -> list[Chapter]:
    text = (
        text
        .replace("\r\n", "\n")
        .replace("\r", "\n")
        .strip()
    )

    if not text:
        return []

    if max_characters is not None and max_characters <= 0:
        raise ValueError(
            "max_characters debe ser mayor que cero."
        )

    matches = list(
        _CHAPTER_RE.finditer(text)
    )

    if not matches:
        bodies = (
            _split_long_text(
                text,
                max_characters,
            )
            if max_characters is not None
            else [text]
        )

        return [
            Chapter(
                index,
                default_title,
                body,
            )
            for index, body in enumerate(
                bodies,
                start=1,
            )
        ]

    chapters: list[Chapter] = []

    for index, match in enumerate(matches):
        start = match.end()

        end = (
            matches[index + 1].start()
            if index + 1 < len(matches)
            else len(text)
        )

        body = text[start:end].strip()

        if not body:
            continue

        bodies = (
            _split_long_text(
                body,
                max_characters,
            )
            if max_characters is not None
            else [body]
        )

        title = match.group(0).strip()

        for part_index, part in enumerate(
            bodies,
            start=1,
        ):
            part_title = title

            if len(bodies) > 1:
                part_title = (
                    f"{title} - Parte {part_index}"
                )

            chapters.append(
                Chapter(
                    number=len(chapters) + 1,
                    title=part_title,
                    text=part,
                )
            )

    return chapters