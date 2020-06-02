import tkinter as tk
from tkinter import ttk

# TODO: lepiej
from view.vertical_notebook.associations_tab import AssociationsTab
from view.vertical_notebook.hierarchy_tab import HierarchyTab
from view.vertical_notebook.constraints_tab import ConstraintsTab
from view.vertical_notebook.ports_tab import PortsTab
from view.vertical_notebook.resources_tab import ResourcesTab
from view.c_frame import CFrame


class VerticalNotebook(CFrame):
    def __init__(self, parent, parent_frame, *args, **kwargs):
        CFrame.__init__(self, parent, parent_frame, *args, **kwargs)

        self.notebook = ttk.Notebook(self.parent_frame, style='Vertical.TNotebook')

        # TODO: move
        self.notebook.grid(row=0, column=0, sticky='nw')
