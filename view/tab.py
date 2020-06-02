import tkinter as tk
from tkinter import ttk

import tkinter as tk
from view.r_frame import RFrame


class Tab(RFrame):
    def __init__(self, parent, tab_name, *args, **kwargs):
        RFrame.__init__(self, parent, *args, **kwargs)

        self.frame = tk.Frame(self.parent.notebook, *args, **kwargs)
        self.parent.notebook.add(self.frame, text=tab_name)

