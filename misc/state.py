"""Singleton, gathering in one place all project's data."""

from typing import Optional, TextIO

from model import Model


class State:
    """A singleton class."""
    class __State:
        """Internal, private class.

        Attributes:
            model: Project's model.
            file: File, that the project has been saved to / opened from.
        """
        def __init__(self):
            self.model: Optional[Model] = None
            self.file: Optional[TextIO] = None

    instance: Optional[__State] = None

    def __new__(cls):
        if not State.instance:
            State.instance = State.__State()
        return State.instance

    def __getattr__(self, name):
        return getattr(self.instance, name)

    def __setattr__(self, name, value):
        return setattr(self.instance, name, value)
