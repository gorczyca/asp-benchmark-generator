from abc import ABC, abstractmethod


class HasCommonSetup(ABC):
    @abstractmethod
    def __init__(self):
        self._create_widgets()
        self._setup_layout()

    @abstractmethod
    def _create_widgets(self) -> None: pass

    @abstractmethod
    def _setup_layout(self) -> None: pass



