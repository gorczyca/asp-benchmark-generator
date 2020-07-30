import tkinter as tk
from tkinter import ttk

from view.abstract.has_common_setup import HasCommonSetup


class MainNotebook(HasCommonSetup):
    def __init__(self, parent_frame):
        self.__parent_frame = parent_frame
        HasCommonSetup.__init__(self)

    def _create_widgets(self):
        self.__notebook = ttk.Notebook(self.__parent_frame, style='Main.TNotebook')

    def _setup_layout(self):
        self.__notebook.grid(row=0, column=0, sticky=tk.NSEW)

    @property
    def notebook(self):
        return self.__notebook

