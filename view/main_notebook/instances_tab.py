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

        self.__selected_component_name = None

        self.__right_frame = tk.Frame(self.frame)
        self.__right_frame.grid(row=0, column=1, sticky='nswe')
        self.__right_frame.rowconfigure(0, weight=1, uniform='fred')
        self.__right_frame.rowconfigure(1, weight=1, uniform='fred')

        self.__set_instances_frame = tk.Frame(self.__right_frame)
        # self.__set_instances_frame.grid(row=0, column=0, sticky='nswe')

        self.__set_global_symmetry_breaking_frame = tk.Frame(self.__right_frame)
        # self.__set_global_symmetry_breaking_frame.grid(row=1, column=0, sticky='nswe')

        self.__global_symmetry_breaking_checkbox_var = tk.BooleanVar(value=True)
        self.__global_symmetry_breaking = ttk.Checkbutton(self.__set_global_symmetry_breaking_frame,
                                                          text='Toggle symmetry breaking for all components?',
                                                          variable=self.__global_symmetry_breaking_checkbox_var)
        self.__global_symmetry_breaking.grid(row=0, column=0, sticky='nswe')
        self.__global_apply_button = ttk.Button(self.__set_global_symmetry_breaking_frame, text='Apply',
                                                command=self.__global_apply)
        self.__global_apply_button.grid(row=1, column=0, sticky='nswe')
        # self.__set_global_symmetry_breaking_frame.grid_forget()

        self.__cmp_label_var = tk.StringVar()
        self.__cmp_label = ttk.Label(self.__set_instances_frame, textvariable=self.__cmp_label_var)
        self.__apply_button = ttk.Button(self.__set_instances_frame, text='Apply', command=self.__apply)
        self.__count_spinbox_var = tk.IntVar()
        self.__count_spinbox = ttk.Spinbox(self.__set_instances_frame, from_=0, to=math.inf,
                                           textvariable=self.__count_spinbox_var)
        self.__symm_breaking_checkbox_var = tk.BooleanVar()
        self.__symm_breaking_checkbox = ttk.Checkbutton(self.__set_instances_frame, text='Symmetry breaking?',
                                                        variable=self.__symm_breaking_checkbox_var)

        self.__cmp_label.grid(row=0, column=0, columnspan=2)
        self.__count_spinbox.grid(row=1, column=0)
        self.__symm_breaking_checkbox.grid(row=1, column=1)
        self.__apply_button.grid(row=2, column=0, columnspan=2)

        # self.__set_instances_frame.grid_forget()

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
            if cmp.count is not None:
                self.__count_spinbox_var.set(cmp.count)
            else:
                self.__count_spinbox_var.set(0)
            self.__cmp_label_var.set(cmp.name)
            if cmp.symmetry_breaking is not None:
                self.__symm_breaking_checkbox_var.set(cmp.symmetry_breaking)

            self.__set_instances_frame.grid(row=0, column=0, sticky='nswe')
            self.__selected_component_name = cmp.name
        else:
            self.__set_instances_frame.grid_forget()

    def __global_apply(self):
        value = self.__global_symmetry_breaking_checkbox_var.get()
        hierarchy = self.controller.model.get_hierarchy()
        updated_cmps = []
        for cmp in hierarchy:
            if cmp.is_leaf:
                cmp.symmetry_breaking = value
                updated_cmps.append(cmp)
        self.hierarchy_tree.update_values(updated_cmps)

    def __apply(self):
        cmp = self.controller.model.get_component_by_name(self.__selected_component_name)
        cmp.count = self.__count_spinbox_var.get()
        cmp.symmetry_breaking = self.__symm_breaking_checkbox_var.get()
        self.hierarchy_tree.update_values([cmp])

    def __build_tree(self):
        hierarchy = self.controller.model.get_hierarchy()
        columns = [
            Column('count', 'Count', stretch=tk.NO, anchor=tk.W),
            Column('symmetry_breaking', 'Symmetry breaking?', stretch=tk.NO, anchor=tk.W)]
        self.hierarchy_tree = HierarchyTree(self.frame, hierarchy, columns=columns, on_select_callback=self.__on_select)
        self.__set_global_symmetry_breaking_frame.grid(row=1, column=0, sticky='nswe')  # show global checkbox

    def __reset(self):  # TODO: czy z tym do jakiejs klasy? (albo jakis wzorzec)
        if self.hierarchy_tree:
            self.hierarchy_tree.destroy()
            self.hierarchy_tree = None
            self.__set_global_symmetry_breaking_frame.grid_forget()
            self.__set_instances_frame.grid_forget()





