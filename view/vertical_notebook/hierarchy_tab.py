import tkinter as tk
from tkinter import ttk
from view.vertical_notebook.edit_hierarchy_window import EditHierarchyWindow
from view.hierarchy_tree import HierarchyTree
from view.vertical_notebook.vertical_notebook_tab import VerticalNotebookTab
from pubsub import pub
from controller import actions

TAB_NAME = 'Hierarchy'

COL_ID_SYMMETRY_BREAKING = 'symmetry_breaking'
COL_ID_COUNT = 'count'
COL_NAME_SYMMETRY_BREAKING = 'Symmetry breaking?'
COL_NAME_COUNT = 'Count'


class HierarchyTab(VerticalNotebookTab):
    def __init__(self, parent, parent_notebook, *args, **kwargs):
        VerticalNotebookTab.__init__(self, parent, parent_notebook, TAB_NAME, *args, **kwargs)

        self.hierarchy_tree = None

        self.frame.rowconfigure(0, weight=1)
        self.frame.columnconfigure(0, weight=1)

        self.button = ttk.Button(self.frame, text="Edit hierarchy", command=self.__edit_hierarchy)
        self.button.grid(row=1, column=0)

    def __hierarchy_edited(self, hierarchy):
        self.controller.model.set_hierarchy(hierarchy)
        self.hierarchy_tree = HierarchyTree(self.frame, hierarchy)
        pub.sendMessage(actions.HIERARCHY_EDITED)

    def __edit_hierarchy(self):
        self.__window = EditHierarchyWindow(self, self.frame, self.__hierarchy_edited)







