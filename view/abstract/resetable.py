from abc import ABC, abstractmethod


class Resetable(ABC):
    @abstractmethod
    def _reset(self) -> None: pass
