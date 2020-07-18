import tkinter as tk
from abc import ABC, abstractmethod
from tkinter import ttk


class Tab(ABC):
    @abstractmethod
    def __init__(self, parent_notebook, tab_name, *args, **kwargs):
        self.frame = ttk.Frame(parent_notebook, *args, **kwargs)
        # TODO:
        self.frame.grid(row=0, column=0, sticky=tk.NSEW)
        # self.frame.rowconfigure(0, weight=1)
        # self.frame.columnconfigure(0, weight=1)

        parent_notebook.add(self.frame, text=tab_name)


