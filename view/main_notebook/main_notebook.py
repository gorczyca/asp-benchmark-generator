import tkinter as tk
from tkinter import ttk
from view.main_notebook.encoding_tab import EncodingTab
from view.main_notebook.instances_tab import InstancesTab
from view.c_frame import CFrame


class MainNotebook(CFrame):
    def __init__(self, parent, parent_frame, *args, **kwargs):
        CFrame.__init__(self, parent, parent_frame, *args, **kwargs)

        self.notebook = ttk.Notebook(parent_frame, style='Main.TNotebook')

        # TODO: to wrzucić to view
        self.notebook.grid(row=0, column=0, sticky='e')
