from typing import Optional, TextIO
import tkinter as tk

from model.model import Model
from view.view import View


class Controller:
    """Controller is the middleman between Model and View in MVC pattern.

    All communication between those two are performed with the use of controller.

    Attributes:
        __model: Holds the "Model" object shared by all application's components.
        __view:
        file: Current file to save to.
        saved: True if there are no unsaved changes; False therwise.
    """
    def __init__(self, main_window: tk.Tk):
        self.__model: Model = Model()
        self.__view: View = View(self, main_window)

        self.file: Optional[TextIO] = None
        self.saved: bool = True

    @property
    def model(self): return self.__model

    def run(self) -> None:
        self.__view.mainloop()


