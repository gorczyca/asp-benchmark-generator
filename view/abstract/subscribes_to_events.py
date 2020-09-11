from abc import ABC, abstractmethod


class SubscribesToEvents(ABC):
    @abstractmethod
    def __init__(self):
        self._subscribe_to_events()

    @abstractmethod
    def _subscribe_to_events(self) -> None:
        """Subscribes to PubSub events."""
        pass
