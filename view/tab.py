import tkinter as tk
from abc import ABC


class Tab(ABC):
    def __init__(self, parent_notebook, tab_name, *args, **kwargs):
        self.frame = tk.Frame(parent_notebook, *args, **kwargs)
        parent_notebook.add(self.frame, text=tab_name)
