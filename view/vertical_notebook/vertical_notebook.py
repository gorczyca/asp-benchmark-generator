import tkinter as tk
from tkinter import ttk

# TODO: lepiej
from view.vertical_notebook.associations_tab import AssociationsTab
from view.vertical_notebook.hierarchy_tab import HierarchyTab
from view.vertical_notebook.constraints_tab import ConstraintsTab
from view.vertical_notebook.ports_tab import PortsTab
from view.vertical_notebook.resources_tab import ResourcesTab
from view.r_frame import RFrame


class VerticalNotebook(RFrame):
    def __init__(self, parent, *args, **kwargs):
        RFrame.__init__(self, parent, *args, **kwargs)

        self.notebook = ttk.Notebook(self.parent.frame, style='Vertical.TNotebook')

        self.hierarchy_tab = HierarchyTab(self)
        self.associations_tab = AssociationsTab(self)
        self.ports_tab = PortsTab(self)
        self.resources_tab = ResourcesTab(self)
        self.constraints_tab = ConstraintsTab(self)

        self.notebook.grid(row=0, column=0, sticky='nw')
