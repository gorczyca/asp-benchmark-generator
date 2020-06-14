import math
import tkinter as tk
from tkinter import ttk
from typing import Optional

from pubsub import pub

import actions
import view.tree_view_item as tv_item
from model.component import Component
from view.c_frame import CFrame
from view.hierarchy_tree import HierarchyTree
from view.hierarchy_tree_column import Column
from view.tab import Tab

TAB_NAME = 'Instances'
LABEL_PAD_X = 25


class InstancesTab(Tab, CFrame):
    def __init__(self, parent, parent_notebook, *args, **kwargs):
        Tab.__init__(self, parent_notebook, TAB_NAME, *args, **kwargs)
        CFrame.__init__(self, parent, parent_notebook)

        self.__hierarchy_tree: Optional[HierarchyTree] = None
        self.__selected_component: Optional[Component] = None

        # TODO: isn't it pointless?
        if self.controller.model.hierarchy:
            self.__build_tree()

    def _create_widgets(self):
        self.__right_frame = tk.Frame(self.frame)
        self.__set_instances_frame = tk.Frame(self.__right_frame)
        self.__set_global_symmetry_breaking_frame = tk.Frame(self.__right_frame)

        self.__global_symmetry_breaking_checkbox_var = tk.BooleanVar(value=True)
        self.__global_symmetry_breaking_checkbox_var.trace('w', self.__on_global_symmetry_breaking_toggled)
        self.__global_symmetry_breaking_checkbox_label = ttk.Label(self.__set_global_symmetry_breaking_frame,
                                                                   text='Symmetry breaking\nfor all components:')
        self.__global_symmetry_breaking_checkbox = ttk.Checkbutton(self.__set_global_symmetry_breaking_frame,
                                                                   variable=self.__global_symmetry_breaking_checkbox_var)

        self.__cmp_label_var = tk.StringVar()
        self.__cmp_label = ttk.Label(self.__set_instances_frame, textvariable=self.__cmp_label_var, style='Big.TLabel')
        self.__count_spinbox_label = ttk.Label(self.__set_instances_frame, text='Count:')
        self.__count_spinbox_var = tk.IntVar()
        self.__count_spinbox_var.trace('w', self.__on_count_changed)
        self.__count_spinbox = ttk.Spinbox(self.__set_instances_frame, from_=0, to=math.inf,
                                           textvariable=self.__count_spinbox_var)
        self.__symm_breaking_checkbox_var = tk.BooleanVar()
        self.__symm_breaking_checkbox_var.trace('w', self.__on_symmetry_breaking_toggled)
        self.__symm_breaking_checkbox_label = ttk.Label(self.__set_instances_frame, text='Symmetry breaking:', )
        self.__symm_breaking_checkbox = ttk.Checkbutton(self.__set_instances_frame,
                                                        variable=self.__symm_breaking_checkbox_var)

    def _setup_layout(self):
        # self.__set_instances_frame.grid(row=0, column=0, sticky='nswe')
        # self.__set_instances_frame.grid_forget()

        # self.__set_global_symmetry_breaking_frame.grid(row=1, column=0, sticky='nswe')
        # self.__set_global_symmetry_breaking_frame.grid_forget()

        self.__global_symmetry_breaking_checkbox_label.grid(row=0, column=0, sticky='w', padx=LABEL_PAD_X)
        self.__global_symmetry_breaking_checkbox.grid(row=0, column=1, sticky='w')

        self.__right_frame.grid(row=0, column=1, sticky=tk.NSEW)
        self.__right_frame.rowconfigure(0, weight=1, uniform='fred')
        self.__right_frame.rowconfigure(1, weight=2, uniform='fred')

        self.__cmp_label.grid(row=0, column=0, columnspan=2)
        self.__count_spinbox_label.grid(row=1, column=0, sticky=tk.W, padx=LABEL_PAD_X)
        self.__count_spinbox.grid(row=1, column=1, sticky=tk.W)
        self.__symm_breaking_checkbox_label.grid(row=2, column=0, sticky=tk.W, padx=LABEL_PAD_X)
        self.__symm_breaking_checkbox.grid(row=2, column=1, sticky=tk.W)

        self.frame.columnconfigure(0, weight=2, uniform='fred')
        self.frame.columnconfigure(1, weight=1, uniform='fred')
        self.frame.rowconfigure(0, weight=1)

    def _subscribe_to_listeners(self):
        pub.subscribe(self.__build_tree, actions.HIERARCHY_CREATED)
        pub.subscribe(self.__build_tree, actions.HIERARCHY_EDITED)
        pub.subscribe(self.__reset, actions.RESET)

    def __on_select(self, cmp_id):
        selected_cmp: Component = self.controller.model.get_component_by_id(cmp_id)
        self.__selected_component = selected_cmp
        if selected_cmp.is_leaf:
            self.__cmp_label_var.set(selected_cmp.name)
            if selected_cmp.count is not None:
                self.__count_spinbox_var.set(selected_cmp.count)
            else:
                self.__count_spinbox_var.set(0)
            if selected_cmp.symmetry_breaking:
                self.__symm_breaking_checkbox_var.set(selected_cmp.symmetry_breaking)

            self.__set_instances_frame.grid(row=0, column=0, sticky=tk.NSEW)
        else:
            self.__set_instances_frame.grid_forget()

    def __on_global_symmetry_breaking_toggled(self, _1, _2, _3):
        value = self.__global_symmetry_breaking_checkbox_var.get()
        edited_cmps = self.controller.model.set_symmetry_breaking_for_all_in_hierarchy(value)
        self.__hierarchy_tree.update_values(edited_cmps)

    def __on_symmetry_breaking_toggled(self, _1, _2, _3):
        if self.__selected_component:
            self.__selected_component.symmetry_breaking = self.__symm_breaking_checkbox_var.get()
            self.__hierarchy_tree.update_values([self.__selected_component])

    def __on_count_changed(self, _1, _2, _3):
        if self.__selected_component:  # TODO: Necessary?
            try:
                self.__selected_component.count = self.__count_spinbox_var.get()
            except tk.TclError as e:
                print(e)
                self.__selected_component.count = None
            finally:
                self.__hierarchy_tree.update_values([self.__selected_component])

    def __build_tree(self):
        columns = [
            Column('count', 'Count', stretch=tk.NO, anchor=tk.W),
            Column('symmetry_breaking', 'Symmetry breaking?', stretch=tk.NO, anchor=tk.W)]

        if self.__hierarchy_tree:
            self.__hierarchy_tree.destroy_()

        self.__hierarchy_tree = HierarchyTree(self.frame, self.controller.model.hierarchy, columns=columns,
                                              on_select_callback=self.__on_select, extract_values=lambda cmp:
                                              (cmp.count if cmp.count else '',
                                               tv_item.BOOLEAN_TO_STRING_DICT[cmp.symmetry_breaking]))
        self.__set_global_symmetry_breaking_frame.grid(row=1, column=0, sticky=tk.NSEW)  # Show global checkbox
        self.__set_instances_frame.grid_forget()    # Hide other checkbox

    def __reset(self):
        if self.__hierarchy_tree:
            self.__hierarchy_tree.destroy_()
            self.__hierarchy_tree = None
            self.__set_global_symmetry_breaking_frame.grid_forget()
            self.__set_instances_frame.grid_forget()

            # TODO: maybe just forget everything, not every grid specifically






