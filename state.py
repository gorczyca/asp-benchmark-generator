from typing import Optional, TextIO

from model.model import Model


class Borg:
    _shared_state = {}

    def __init__(self):
        self.__dict__ = self._shared_state


class State(Borg):
    def __init__(self):
        Borg.__init__(self)
        # self.val = arg
        self.model: Model = Model()
        self.file: Optional[TextIO] = None
        self.is_saved: bool = True

    # def __str__(self): return self.val



