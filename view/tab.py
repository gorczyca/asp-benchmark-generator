import tkinter as tk
from tkinter import ttk

import tkinter as tk
from view.r_frame import RFrame


class Tab(RFrame):
    def __init__(self, parent, tab_name, *args, **kwargs):
        RFrame.__init__(self, parent, *args, **kwargs)

        self._frame = tk.Frame(self.parent._notebook, *args, **kwargs)
        self.parent._notebook.add(self._frame, text=tab_name)

