from __future__ import annotations

from abc import ABC, abstractmethod


class OcrEngine(ABC):
    """Interfaz para motores OCR independientes del formato de documento."""

    @abstractmethod
    def recognize(self, image_bytes: bytes) -> str:
        """Reconoce texto a partir de una imagen codificada."""
        raise NotImplementedError

    @abstractmethod
    def is_available(self) -> bool:
        """Indica si el motor OCR está disponible en el sistema."""
        raise NotImplementedError
