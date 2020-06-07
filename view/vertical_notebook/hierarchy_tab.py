from tkinter import ttk
from view.vertical_notebook.create_hierarchy_window import CreateHierarchyWindow
from view.hierarchy_tree import HierarchyTree
from view.vertical_notebook.vertical_notebook_tab import VerticalNotebookTab
from pubsub import pub
from controller import actions
from tkinter import messagebox

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

        self.button = ttk.Button(self.frame, text="Create hierarchy", command=self.__create_hierarchy)
        self.button.grid(row=1, column=0)

        pub.subscribe(self.__reset, actions.RESET)
        pub.subscribe(self.__hierarchy_created, actions.HIERARCHY_EDITED)

    def __reset(self):
        if self.hierarchy_tree:
            self.hierarchy_tree.destroy()
            self.hierarchy_tree = None

    def __hierarchy_created(self):
        hierarchy = self.controller.model.get_hierarchy()
        self.hierarchy_tree = HierarchyTree(self.frame, hierarchy)

    def __create_hierarchy(self):
        hierarchy = self.controller.model.get_hierarchy()
        if hierarchy:
            answer = messagebox.askyesno('Create hierarchy', 'Warning: hierarchy has already been created. \n '
                                                        'If you use this option again, previous hierarchy will be '
                                                        'overwritten, and you may lose all data regarding ports, '
                                                        'instances etc.\n If you plan to make simple changes, '
                                                        'use options such as "Create sibling", "Create child", etc.')
            if not answer:
                return

        self.__window = CreateHierarchyWindow(self, self.frame, self.__hierarchy_created)







