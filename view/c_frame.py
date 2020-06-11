import tkinter as tk
from abc import ABC, abstractmethod


class CFrame(tk.Frame, ABC):
    @abstractmethod
    def __init__(self, parent, parent_frame):
        tk.Frame.__init__(self, parent_frame)

        self.controller = parent.controller
        self.parent_frame = parent_frame

        self._create_widgets()
        self._setup_layout()
        self._subscribe_to_listeners()

    @abstractmethod
    def _create_widgets(self): pass

    @abstractmethod
    def _setup_layout(self): pass

    @abstractmethod
    def _subscribe_to_listeners(self): pass



