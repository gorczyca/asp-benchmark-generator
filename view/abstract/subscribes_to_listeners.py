from abc import ABC, abstractmethod


class SubscribesToListeners(ABC):
    @abstractmethod
    def __init__(self):
        self._subscribe_to_listeners()

    @abstractmethod
    def _subscribe_to_listeners(self) -> None: pass
