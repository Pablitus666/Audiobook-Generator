from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path

from audiobook_generator.core.models import Document


class DocumentReader(ABC):
    """Interfaz base para lectores de documentos."""

    @abstractmethod
    def read(self, source: Path) -> Document:
        """Lee un documento y devuelve su representación interna."""
        raise NotImplementedError