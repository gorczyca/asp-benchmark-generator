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
    def __init__(self, parent, *args, **kwargs):
        VerticalNotebookTab.__init__(self, parent, TAB_NAME, *args, **kwargs)

        self.hierarchy_tree = None

        self.frame.rowconfigure(0, weight=1)
        self.frame.columnconfigure(0, weight=1)

        self.button = ttk.Button(self.frame, text="Edit hierarchy", command=self.__edit_hierarchy)
        self.button.grid(row=1, column=0)

    def __build_tree(self):  # TODO: zamiast tupli obiekty
        columns = [('count', 'Count', 150, 150, tk.NO, tk.W), ('symmetry_breaking', 'Symmetry breaking?', 150, 150, tk.NO, tk.W)]
        self.hierarchy_tree = HierarchyTree(self, columns=columns)
        # TO JEST MEGA ZLE, NAPRAWIC!!
        self.parent.parent.parent.instances_tab.build_tree()

    def callback(self, text):
        print('asdf' + text)

    def __edit_hierarchy(self):
        #pub.sendMessage(actions.BUTTON_CLICK, callback=self.__callback)
        pub.sendMessage(actions.BUTTON_CLICK, callback=self.callback)

        # self._window = EditHierarchyWindow(self, self.__build_tree)







