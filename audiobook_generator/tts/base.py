from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path


class TTSEngine(ABC):
    @abstractmethod
    async def synthesize(self, text: str, destination: Path) -> None:
        raise NotImplementedError
