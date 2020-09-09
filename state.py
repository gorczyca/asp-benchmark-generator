from typing import Optional, TextIO

from settings import Settings
from model import Model


class State:
    class __State:
        def __init__(self):
            self.model: Optional[Model] = None
            self.file: Optional[TextIO] = None
            self.settings: Optional[Settings] = None

    instance = None

    def __new__(cls):
        if not State.instance:
            State.instance = State.__State()
        return State.instance

    def __getattr__(self, name):
        return getattr(self.instance, name)

    def __setattr__(self, name, value):
        return setattr(self.instance, name, value)
