from typing import Optional, TextIO
import tkinter as tk

from pubsub import pub

import actions
from model import Model
from view import View


class Controller:
    """Controller is the middleman between Model and View in MVC pattern.

    All communication between those two are performed with the use of controller.

    Attributes:
        __model: Holds the "Model" object shared by all application's components.
        __view:
        __file: Current file to save to.
        __saved: True if there are no unsaved changes; False therwise.
    """
    def __init__(self, main_window: tk.Tk):
        self.__model: Model = Model()
        self.__view: View = View(self, main_window)

        self.__file: Optional[TextIO] = None
        self.__saved: bool = True

    @property
    def model(self): return self.__model

    @property
    def file(self): return self.__file

    @file.setter
    def file(self, value): self.__file = value

    @property
    def saved(self): return self.__saved

    @saved.setter
    def saved(self, value): self.__saved = value

    def run(self) -> None:
        self.__view.mainloop()


