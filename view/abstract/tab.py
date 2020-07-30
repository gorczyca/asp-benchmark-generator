import tkinter as tk
from abc import ABC, abstractmethod
from tkinter import ttk


class Tab(ABC):
    @abstractmethod
    def __init__(self, parent_notebook, tab_name):
        self._frame = ttk.Frame(parent_notebook)
        self._frame.grid(row=0, column=0, sticky=tk.NSEW)
        parent_notebook.add(self._frame, text=tab_name)



