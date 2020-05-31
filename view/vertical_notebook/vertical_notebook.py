import tkinter as tk
from tkinter import ttk

from view.vertical_notebook.associacions_tab import AssociacionsTab
from view.vertical_notebook.hierarchy_tab import HierarchyTab
from view.vertical_notebook.constraints_tab import ConstraintsTab
from view.vertical_notebook.ports_tab import PortsTab
from view.vertical_notebook.resources_tab import ResourcesTab

class VerticalNotebook(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self, parent)
        self.parent = parent

        # style = ttk.Style()

        # style.configure('Vertical.TNotebook', tabposition='wn', width=100, height=100)
        # style.configure('Vertical.TNotebook.Tab', padding=[20,20], width='100')


        # config_item = self._notebook.configure()
        # s = ttk.Style()

        # s.layout('TButton')
        self._notebook = ttk.Notebook(self.parent._frame, style='Vertical.TNotebook')


        self.hierarchy_tab = HierarchyTab(self)
        self.associacions_tab = AssociacionsTab(self)
        self.ports_tab = PortsTab(self)
        self.resources_tab = ResourcesTab(self)
        self.constraints_tab = ConstraintsTab(self)

        

        self._notebook.grid(row=0, column=0, sticky='nw')
