from view.tab import Tab
from tkinter import ttk
import tkinter as tk
from view.hierarchy_tree import HierarchyTree

TAB_NAME = 'Instances'


class InstancesTab(Tab):
    def __init__(self, parent, *args, **kwargs):
        Tab.__init__(self, parent, TAB_NAME, *args, **kwargs)

        self.hierarchy_tree = None

        self._frame.columnconfigure(0, weight=1)
        self._frame.columnconfigure(1, weight=1)

    def build_tree(self):  # TODO: zamiast tupli obiekty
        columns = [('count', 'Count', 150, 150, tk.NO, tk.W), ('symmetry_breaking', 'Symmetry breaking?', 150, 150, tk.NO, tk.W)]
        self.hierarchy_tree = HierarchyTree(self, columns=columns)




