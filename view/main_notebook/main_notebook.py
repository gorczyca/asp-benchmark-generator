import tkinter as tk
from tkinter import ttk
from view.main_notebook.encoding_tab import EncodingTab
from view.main_notebook.instances_tab import InstancesTab
from view.r_frame import RFrame


class MainNotebook(RFrame):
    def __init__(self, parent, *args, **kwargs):
        RFrame.__init__(self, parent, *args, **kwargs)

        self._notebook = ttk.Notebook(parent.frame, style='Main.TNotebook')

        # TODO: czyli wszystkie muszą być takie same chyba?
        self.encoding_frame = EncodingTab(self)
        self.instances_tab = InstancesTab(self)

        self._notebook.grid(row=0, column=0, sticky='e')
