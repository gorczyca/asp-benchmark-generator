from view.c_tab import CTab
import tkinter as tk
from tkinter import ttk
from view.hierarchy_tree import HierarchyTree
from pubsub import pub
from controller import actions
from view.hierarchy_tree_column import Column
import math

TAB_NAME = 'Instances'


class InstancesTab(CTab):
    def __init__(self, parent, parent_notebook, *args, **kwargs):
        CTab.__init__(self, parent, parent_notebook, TAB_NAME, *args, **kwargs)

        self.__set_instances_frame = tk.Frame(self.frame)
        self.__set_instances_frame.grid(row=0, column=1, sticky='nswe')

        self.__cmp_label = ttk.Label(self.__set_instances_frame, text='Jakiś item')
        self.__apply_button = ttk.Button(self.__set_instances_frame, text='Apply')
        self.__count_spinbox_var = tk.IntVar()
        self.__count_spinbox = ttk.Spinbox(self.__set_instances_frame, from_=0, to=math.inf,
                                           textvariable=self.__count_spinbox_var)
        self.__symm_breaking_checkbox = ttk.Checkbutton(self.__set_instances_frame, text='Symmetry breaking?')

        self.__cmp_label.grid(row=0, column=0, columnspan=2)
        self.__count_spinbox.grid(row=1, column=0)
        self.__symm_breaking_checkbox.grid(row=1, column=1)
        self.__apply_button.grid(row=2, column=0, columnspan=2)

        self.__set_instances_frame.grid_forget()

        hierarchy = self.controller.model.get_hierarchy()
        if hierarchy:
            self.__build_tree()

        pub.subscribe(self.__build_tree, actions.HIERARCHY_EDITED)
        pub.subscribe(self.__reset, actions.RESET)

        self.frame.columnconfigure(0, weight=2, uniform='fred')
        self.frame.columnconfigure(1, weight=1, uniform='fred')
        self.frame.rowconfigure(0, weight=1)

    def __on_select(self, item_name):
        cmp = self.controller.model.get_component_by_name(item_name)
        if cmp.is_leaf:
            self.__set_instances_frame.grid(row=0, column=1, sticky='nswe')
        else:
            self.__set_instances_frame.grid_forget()

    def __build_tree(self):  # TODO: zamiast tupli obiekty
        hierarchy = self.controller.model.get_hierarchy()
        columns = [
            Column('count', 'Count', stretch=tk.NO, anchor=tk.W),
            Column('symmetry_breaking', 'Symmetry breaking?', stretch=tk.NO, anchor=tk.W)]
        self.hierarchy_tree = HierarchyTree(self.frame, hierarchy, columns=columns, on_select_callback=self.__on_select)

    def __reset(self):  # TODO: czy z tym do jakiejs klasy? (albo jakis wzorzec)
        if self.hierarchy_tree:
            self.hierarchy_tree.destroy()
            self.hierarchy_tree = None





