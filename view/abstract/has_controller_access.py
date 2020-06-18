from abc import ABC, abstractmethod


class HasControllerAccess(ABC):
    @abstractmethod
    def __init__(self, parent):
        self.controller = parent.controller # TODO: make protected
