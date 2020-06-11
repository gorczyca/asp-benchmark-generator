import tkinter as tk
from tkinter import ttk

from view.c_frame import CFrame


class MainNotebook(CFrame):
    def __init__(self, parent, parent_frame):
        CFrame.__init__(self, parent, parent_frame)

    def _create_widgets(self):
        self.notebook = ttk.Notebook(self.parent_frame, style='Main.TNotebook')

    def _setup_layout(self):
        self.notebook.grid(row=0, column=0, sticky=tk.E)

    def _subscribe_to_listeners(self):
        pass
