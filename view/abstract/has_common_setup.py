from abc import ABC, abstractmethod


class HasCommonSetup(ABC):
    @abstractmethod
    def __init__(self):
        self._create_widgets()
        self._setup_layout()

    @abstractmethod
    def _create_widgets(self) -> None:
        """All the tk widgets should be created here."""
        pass

    @abstractmethod
    def _setup_layout(self) -> None:
        """This is where the tk widgets are being positioned."""
        pass



