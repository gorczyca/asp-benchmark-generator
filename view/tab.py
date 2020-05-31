import tkinter as tk
from tkinter import ttk

import tkinter as tk

class Tab(tk.Frame):
    def __init__(self, parent, tab_name, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)
        self.parent = parent
        self._frame = tk.Frame(self.parent._notebook, width=100, height=100, *args, **kwargs)
        self.parent._notebook.add(self._frame, text=tab_name)

