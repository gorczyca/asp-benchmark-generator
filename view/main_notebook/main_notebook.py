import tkinter as tk
from tkinter import ttk
from view.main_notebook.encoding_tab import EncodingTab
from view.main_notebook.instances_tab import InstancesTab

class MainNotebook(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self, parent)
        self.parent = parent
        self._notebook = ttk.Notebook(self.parent.frame, style='Main.TNotebook')

        self.encoding_frame = EncodingTab(self)
        self.instances_tab = InstancesTab(self)

        self._notebook.grid(row=0, column=0)
