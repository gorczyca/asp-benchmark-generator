from view.c_tab import CTab
import tkinter as tk
from view.hierarchy_tree import HierarchyTree
from pubsub import pub
from controller import actions
from view.hierarchy_tree_column import Column

TAB_NAME = 'Instances'


class InstancesTab(CTab):
    def __init__(self, parent, parent_notebook, *args, **kwargs):
        CTab.__init__(self, parent, parent_notebook, TAB_NAME, *args, **kwargs)

        hierarchy = self.controller.model.get_hierarchy()

        if hierarchy:
            self.__build_tree()

        pub.subscribe(self.__build_tree, actions.HIERARCHY_EDITED)

        self.frame.columnconfigure(0, weight=1)
        self.frame.columnconfigure(1, weight=1)
        self.frame.rowconfigure(0, weight=1)

    def __build_tree(self):  # TODO: zamiast tupli obiekty
        hierarchy = self.controller.model.get_hierarchy()
        columns = [
            Column('count', 'Count', stretch=tk.NO, anchor=tk.W),
            Column('symmetry_breaking', 'Symmetry breaking?', stretch=tk.NO, anchor=tk.W)]
        self.hierarchy_tree = HierarchyTree(self.frame, hierarchy, columns=columns)






