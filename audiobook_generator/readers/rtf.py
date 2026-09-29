from __future__ import annotations

import re
from pathlib import Path

from audiobook_generator.core.errors import (
    DocumentReadError,
    InputFileError,
)
from audiobook_generator.core.models import Document
from audiobook_generator.readers.base import DocumentReader


_CONTROL_WORD_RE = re.compile(rb"\\([a-zA-Z]+)(-?\d+)? ?")
_HEX_RE = re.compile(rb"\\'([0-9a-fA-F]{2})")


class RtfReader(DocumentReader):
    """Lector de documentos RTF sin dependencias externas."""

    _SKIP_DESTINATIONS = {
        "fonttbl",
        "colortbl",
        "stylesheet",
        "info",
        "pict",
        "object",
        "header",
        "headerl",
        "headerr",
        "footer",
        "footerl",
        "footerr",
        "filetbl",
        "listtable",
        "listoverridetable",
        "generator",
    }

    def read(self, source: Path) -> Document:
        if not source.is_file():
            raise InputFileError(
                f"no existe el archivo de entrada: {source}"
            )

        try:
            raw = source.read_bytes()
        except OSError as exc:
            raise DocumentReadError(
                f"no se pudo leer el archivo RTF: {source}"
            ) from exc

        if not raw.lstrip().startswith(b"{\\rtf"):
            raise DocumentReadError(
                f"el archivo no contiene un documento RTF válido: {source}"
            )

        try:
            text = self._extract_text(raw)
        except Exception as exc:
            raise DocumentReadError(
                f"no se pudo extraer texto del RTF: {source}"
            ) from exc

        return Document(
            title=source.stem,
            source=source,
            text=text,
        )

    @classmethod
    def _extract_text(cls, data: bytes) -> str:
        output: list[str] = []
        stack: list[bool] = [False]
        uc = 1
        skip_fallback = 0
        i = 0

        def active() -> bool:
            return not any(stack)

        while i < len(data):
            byte = data[i]

            if byte == 0x7B:  # {
                stack.append(stack[-1])
                i += 1
                continue

            if byte == 0x7D:  # }
                if len(stack) > 1:
                    stack.pop()
                i += 1
                continue

            if byte != 0x5C:  # backslash
                if skip_fallback:
                    skip_fallback -= 1
                elif active() and byte not in (0x0D, 0x0A):
                    output.append(chr(byte) if byte < 128 else " ")
                i += 1
                continue

            # Escaped hexadecimal character: \'e1
            match = _HEX_RE.match(data, i)
            if match:
                if active() and not skip_fallback:
                    try:
                        output.append(bytes.fromhex(match.group(1).decode()).decode("cp1252"))
                    except UnicodeDecodeError:
                        output.append(" ")
                i = match.end()
                continue

            # Escaped literal characters: \\, \{, \}
            if i + 1 < len(data) and data[i + 1] in b"\\{}":
                if active() and not skip_fallback:
                    output.append(chr(data[i + 1]))
                i += 2
                continue

            # Control symbol.
            if i + 1 < len(data) and data[i + 1] in b"~_-":
                symbol = chr(data[i + 1])
                if active() and not skip_fallback:
                    if symbol == "~":
                        output.append("\u00a0")
                    elif symbol == "_":
                        output.append("-")
                    else:
                        output.append("\u00ad")
                i += 2
                continue

            match = _CONTROL_WORD_RE.match(data, i)
            if not match:
                i += 1
                continue

            word = match.group(1).decode("ascii", errors="ignore").lower()
            argument = match.group(2)
            number = int(argument) if argument else None
            i = match.end()

            if word in cls._SKIP_DESTINATIONS:
                stack[-1] = True
                continue

            if word == "uc" and number is not None:
                uc = max(0, number)
                continue

            if word == "u" and number is not None:
                if number < 0:
                    number += 65536
                try:
                    output.append(chr(number))
                except ValueError:
                    output.append("\ufffd")
                skip_fallback = uc
                continue

            if skip_fallback and word not in {"u"}:
                # A control word terminates the fallback sequence.
                skip_fallback = 0

            if not active():
                continue

            if word in {"par", "line"}:
                output.append("\n\n" if word == "par" else "\n")
            elif word == "tab":
                output.append("\t")
            elif word == "emdash":
                output.append("\u2014")
            elif word == "endash":
                output.append("\u2013")
            elif word == "bullet":
                output.append("\u2022")
            elif word == "lquote":
                output.append("\u2018")
            elif word == "rquote":
                output.append("\u2019")
            elif word == "ldblquote":
                output.append("\u201c")
            elif word == "rdblquote":
                output.append("\u201d")

        text = "".join(output)
        lines = [" ".join(line.split()) for line in text.splitlines()]
        return "\n\n".join(line for line in lines if line)


