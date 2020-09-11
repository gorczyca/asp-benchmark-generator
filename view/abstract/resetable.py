from abc import ABC, abstractmethod


class Resetable(ABC):
    @abstractmethod
    def _reset(self) -> None:
        """Resets widgets to default state."""
        pass
