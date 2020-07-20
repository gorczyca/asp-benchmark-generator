import math
import tkinter as tk
from tkinter import ttk
from typing import List, Any, Tuple

from pubsub import pub

import actions
import view.tree_view_item as tv_item
from model.component import Component
from view.abstract.has_controller_access import HasControllerAccess
from view.abstract.has_common_setup import HasCommonSetup
from view.abstract.has_hierarchy_tree import HasHierarchyTree
from view.abstract.subscribes_to_listeners import SubscribesToListeners
from view.abstract.tab import Tab
from view.abstract.resetable import Resetable
from view.hierarchy_tree import HierarchyTree
from view.tree_view_column import Column
from view.common import trim_string, change_controls_state

TAB_NAME = 'Instances'
LABEL_LENGTH = 15

CONTROL_PAD_Y = 3
CONTROL_PAD_X = 3

FRAME_PAD_Y = 10
FRAME_PAD_X = 10


# TODO: Add button "Apply to all children"
class InstancesTab(Tab,
                   HasControllerAccess,
                   HasCommonSetup,
                   HasHierarchyTree,
                   SubscribesToListeners,
                   Resetable):
    def __init__(self, parent, parent_notebook, *args, **kwargs):
        Tab.__init__(self, parent_notebook, TAB_NAME, *args, **kwargs)
        HasControllerAccess.__init__(self, parent)

        HasCommonSetup.__init__(self)
        HasHierarchyTree.__init__(self)
        SubscribesToListeners.__init__(self)

    # HasCommonSetup
    def _create_widgets(self):
        self.__left_frame = ttk.Frame(self.frame)

        self.__cmp_label_var = tk.StringVar(value='')
        self.__cmp_label = ttk.Label(self.__left_frame, textvariable=self.__cmp_label_var, style='Big.TLabel',
                                     anchor=tk.CENTER)

        self.__global_symmetry_breaking_checkbox_var = tk.BooleanVar(value=True)
        self.__global_symmetry_breaking_checkbox_var.trace('w', self.__on_global_symmetry_breaking_toggled)
        self.__global_symmetry_breaking_checkbox_label = ttk.Label(self.__left_frame,
                                                                   text='Symmetry breaking\nfor all components:')
        self.__global_symmetry_breaking_checkbox = ttk.Checkbutton(self.__left_frame,
                                                                   variable=self.__global_symmetry_breaking_checkbox_var)
        self.__symm_breaking_checkbox_var = tk.BooleanVar()
        self.__symm_breaking_checkbox_var.trace('w', self.__on_symmetry_breaking_toggled)
        self.__symm_breaking_checkbox_label = ttk.Label(self.__left_frame, text='Symmetry breaking:')
        self.__symm_breaking_checkbox = ttk.Checkbutton(self.__left_frame,
                                                        variable=self.__symm_breaking_checkbox_var)

        self.__count_spinbox_label = ttk.Label(self.__left_frame, text='Count:')
        self.__count_spinbox_var = tk.IntVar()
        self.__count_spinbox_var.trace('w', self.__on_count_changed)
        self.__count_spinbox = ttk.Spinbox(self.__left_frame, from_=0, to=math.inf,
                                           textvariable=self.__count_spinbox_var)

        self.__all_children_count_spinbox_label = ttk.Label(self.__left_frame, text='Count:')
        self.__all_children_count_spinbox_var = tk.IntVar()
        self.__all_children_count_spinbox_var.trace('w', self.__on_count_changed)
        self.__all_children_count_spinbox = ttk.Spinbox(self.__left_frame, from_=0, to=math.inf,
                                                        textvariable=self.__all_children_count_spinbox_var)
        self.__apply_to_all_children_button = ttk.Button(self.__left_frame, text='Apply to all children',
                                                         command=self.__apply_to_all_children)

    def _setup_layout(self):
        # self.__set_instances_frame.grid(row=0, column=0, sticky=tk.NSEW)
        # self.__set_global_symmetry_breaking_frame.grid(row=1, column=0, sticky=tk.NSEW)
        self.__left_frame.grid(row=0, column=0, sticky=tk.NSEW, padx=FRAME_PAD_X, pady=FRAME_PAD_Y)

        self.__cmp_label.grid(row=0, column=0, columnspan=2, sticky=tk.EW, pady=CONTROL_PAD_Y)

        self.__global_symmetry_breaking_checkbox_label.grid(row=1, column=0, sticky=tk.W, pady=CONTROL_PAD_Y, padx=CONTROL_PAD_X)
        self.__global_symmetry_breaking_checkbox.grid(row=1, column=1, sticky=tk.W, padx=CONTROL_PAD_X, pady=CONTROL_PAD_Y)

        self.__symm_breaking_checkbox_label.grid(row=2, column=0, sticky=tk.W, pady=CONTROL_PAD_Y, padx=CONTROL_PAD_X)
        self.__symm_breaking_checkbox.grid(row=2, column=1, sticky=tk.W, padx=CONTROL_PAD_X, pady=CONTROL_PAD_Y)

        self.__count_spinbox_label.grid(row=3, column=0, sticky=tk.W, padx=CONTROL_PAD_X, pady=CONTROL_PAD_Y)
        self.__count_spinbox.grid(row=3, column=1, sticky=tk.NSEW, padx=CONTROL_PAD_X, pady=CONTROL_PAD_Y)

        self.__all_children_count_spinbox_label.grid(row=3, column=0, sticky=tk.W, padx=CONTROL_PAD_X, pady=CONTROL_PAD_Y)
        self.__all_children_count_spinbox.grid(row=3, column=1, sticky=tk.NSEW, padx=CONTROL_PAD_X, pady=CONTROL_PAD_Y)
        self.__apply_to_all_children_button.grid(row=4, column=0, columnspan=2, sticky=tk.NSEW, padx=CONTROL_PAD_X, pady=CONTROL_PAD_Y)

        self.__left_frame.columnconfigure(1, weight=1)
        self.frame.columnconfigure(0, weight=1, uniform='fred')
        self.frame.columnconfigure(1, weight=3, uniform='fred')
        self.frame.rowconfigure(0, weight=1)
        # Hide widgets
        self.__global_symmetry_breaking_checkbox_label.grid_forget()
        self.__global_symmetry_breaking_checkbox.grid_forget()
        self.__symm_breaking_checkbox_label.grid_forget()
        self.__symm_breaking_checkbox.grid_forget()
        self.__count_spinbox_label.grid_forget()
        self.__count_spinbox.grid_forget()
        self.__all_children_count_spinbox_label.grid_forget()
        self.__all_children_count_spinbox.grid_forget()
        self.__apply_to_all_children_button.grid_forget()

    # SubscribesToListeners
    def _subscribe_to_listeners(self):
        pub.subscribe(self.__on_model_loaded, actions.MODEL_LOADED)
        # TODO:
        pub.subscribe(self._build_tree, actions.HIERARCHY_CREATED)
        pub.subscribe(self._build_tree, actions.HIERARCHY_EDITED)
        pub.subscribe(self._reset, actions.RESET)

    # HasHierarchyTree
    @property
    def _columns(self) -> List[Column]:
        return [Column('count', 'Count', stretch=tk.NO, anchor=tk.W),
                Column('symmetry_breaking', 'Symmetry breaking?', stretch=tk.NO, anchor=tk.W)]

    def _extract_values(self, cmp: Component) -> Tuple[Any, ...]:
        return (cmp.count if cmp.count else '',
                tv_item.BOOLEAN_TO_STRING_DICT[cmp.symmetry_breaking])

    def __on_model_loaded(self):
        self._build_tree()
        self.__global_symmetry_breaking_checkbox_label.grid(row=1, column=0, sticky=tk.W, padx=CONTROL_PAD_X, pady=CONTROL_PAD_Y) # Show global checkbox
        self.__global_symmetry_breaking_checkbox.grid(row=1, column=1, sticky=tk.W, padx=CONTROL_PAD_X, pady=CONTROL_PAD_Y)

    def _build_tree(self):
        if self._hierarchy_tree:
            self._destroy_tree()

        self._hierarchy_tree = HierarchyTree(self.frame, self.controller.model.hierarchy, columns=self._columns,
                                             on_select_callback=self._on_select_tree_item,
                                             extract_values=self._extract_values)
        self._hierarchy_tree.grid(row=0, column=1, sticky=tk.NSEW)

    def _destroy_tree(self) -> None:
        self._hierarchy_tree.destroy_()
        self._hierarchy_tree = None

    def _on_select_tree_item(self, cmp_id: int):
        selected_cmp: Component = self.controller.model.get_component_by_id(cmp_id)
        self._selected_component = selected_cmp
        self.__cmp_label_var.set(trim_string(selected_cmp.name, length=LABEL_LENGTH))
        if selected_cmp.is_leaf:
            if selected_cmp.count is not None:
                self.__count_spinbox_var.set(selected_cmp.count)
            else:
                self.__count_spinbox_var.set(0)
            if selected_cmp.symmetry_breaking:
                self.__symm_breaking_checkbox_var.set(selected_cmp.symmetry_breaking)
            # Show instances of single component
            self.__count_spinbox_label.grid(row=3, column=0, sticky=tk.W, padx=CONTROL_PAD_X, pady=CONTROL_PAD_Y)
            self.__count_spinbox.grid(row=3, column=1, sticky=tk.NSEW, padx=CONTROL_PAD_X, pady=CONTROL_PAD_Y)
            # Show symmetry breaking for single component
            self.__symm_breaking_checkbox_label.grid(row=2, column=0, sticky=tk.W, padx=CONTROL_PAD_X, pady=CONTROL_PAD_Y)
            self.__symm_breaking_checkbox.grid(row=2, column=1, sticky=tk.W, padx=CONTROL_PAD_X, pady=CONTROL_PAD_Y)
            # Hide 'for all children'
            self.__all_children_count_spinbox_label.grid_forget()
            self.__all_children_count_spinbox.grid_forget()
            self.__apply_to_all_children_button.grid_forget()
        else:
            # Show apply to all children
            self.__all_children_count_spinbox_label.grid(row=3, column=0, sticky=tk.W, padx=CONTROL_PAD_X, pady=CONTROL_PAD_Y)
            self.__all_children_count_spinbox.grid(row=3, column=1, sticky=tk.NSEW, padx=CONTROL_PAD_X, pady=CONTROL_PAD_Y)
            self.__apply_to_all_children_button.grid(row=4, column=0, columnspan=2, sticky=tk.NSEW, pady=CONTROL_PAD_Y,  padx=CONTROL_PAD_X)
            # Hide for single
            self.__count_spinbox_label.grid_forget()
            self.__count_spinbox.grid_forget()
            self.__symm_breaking_checkbox_label.grid_forget()
            self.__symm_breaking_checkbox.grid_forget()

    # Resetable
    def _reset(self) -> None:
        if self._hierarchy_tree:
            self._destroy_tree()

        self._selected_component = None
        # Hide widgets
        self.__global_symmetry_breaking_checkbox_label.grid_forget()
        self.__global_symmetry_breaking_checkbox.grid_forget()
        self.__symm_breaking_checkbox_label.grid_forget()
        self.__symm_breaking_checkbox.grid_forget()
        self.__count_spinbox_label.grid_forget()
        self.__count_spinbox.grid_forget()
        self.__all_children_count_spinbox_label.grid_forget()
        self.__all_children_count_spinbox.grid_forget()
        self.__apply_to_all_children_button.grid_forget()
        # Set entries to default
        self.__global_symmetry_breaking_checkbox_var.set(True)
        self.__count_spinbox_var.set(0)
        self.__symm_breaking_checkbox_var.set(True)

    # Class-specific
    def __on_global_symmetry_breaking_toggled(self, _1, _2, _3):
        if self._hierarchy_tree:
            value = self.__global_symmetry_breaking_checkbox_var.get()
            edited_cmps = self.controller.model.set_symmetry_breaking_for_all_in_hierarchy(value)
            self._hierarchy_tree.update_values(edited_cmps)

    def __on_symmetry_breaking_toggled(self, _1, _2, _3):
        if self._selected_component and self._hierarchy_tree:
            self._selected_component.symmetry_breaking = self.__symm_breaking_checkbox_var.get()
            self._hierarchy_tree.update_values([self._selected_component])

    def __on_count_changed(self, _1, _2, _3):
        if self._selected_component and self._hierarchy_tree:
            try:
                self._selected_component.count = self.__count_spinbox_var.get()
            except tk.TclError as e:
                print(e)
                self._selected_component.count = None
            finally:
                self._hierarchy_tree.update_values([self._selected_component])

    def __apply_to_all_children(self):
        if self._selected_component:
            value = 0
            try:
                value = self.__all_children_count_spinbox_var.get()
            except tk.TclError as e:
                print(e)
            finally:
                updated_components = self.controller.model.set_instances_count_of_all_components_children(
                    self._selected_component, value)
                self._hierarchy_tree.update_values(updated_components)
