import math
import tkinter as tk
from tkinter import ttk
from typing import List, Any, Tuple, Optional

from pubsub import pub

import actions
import view.tree_view_item as tv_item
from model.component import Component
from state import State
from view.abstract.has_common_setup import HasCommonSetup
from view.abstract.subscribes_to_events import SubscribesToEvents
from view.abstract.tab import Tab
from view.abstract.resetable import Resetable
from view.hierarchy_tree import HierarchyTree
from view.scrollbars_listbox import ScrollbarListbox
from view.tree_view_column import Column
from view.common import trim_string, BOOLEAN_TO_STRING_DICT, change_controls_state

TAB_NAME = 'Instances'
LABEL_LENGTH = 15
TREEVIEW_HEADING = 'Component'

CONTROL_PAD_Y = 3
CONTROL_PAD_X = 3

FRAME_PAD_Y = 10
FRAME_PAD_X = 10


# TODO: Add button "Apply to all children"
class InstancesTab(Tab,
                   HasCommonSetup,
                   SubscribesToEvents,
                   Resetable):
    def __init__(self, parent_notebook):
        self.__state = State()
        self.__selected_component: Optional[Component] = None

        Tab.__init__(self, parent_notebook, TAB_NAME)

        HasCommonSetup.__init__(self)
        SubscribesToEvents.__init__(self)

    # HasCommonSetup
    def _create_widgets(self):
        self.__hierarchy_tree = ScrollbarListbox(self._frame,
                                                 on_select_callback=self.__on_select_tree_item,
                                                 heading=TREEVIEW_HEADING,
                                                 extract_id=lambda x: x.id_,
                                                 extract_text=lambda x: x.name,
                                                 extract_ancestor=lambda x: '' if x.parent_id is None else x.parent_id,
                                                 extract_values=self.__extract_values,
                                                 columns=[Column('count', 'Count'),
                                                          Column('symmetry_breaking', 'Symmetry breaking?')]
                                                 )

        self.__left_frame = ttk.Frame(self._frame)

        self.__cmp_label_var = tk.StringVar(value='')
        self.__cmp_label = ttk.Label(self.__left_frame, textvariable=self.__cmp_label_var, style='Big.TLabel',
                                     anchor=tk.CENTER)

        self.__all_children_symmetry_breaking_checkbox_var = tk.BooleanVar(value=False)
        self.__all_children_symmetry_breaking_checkbox_label = ttk.Label(self.__left_frame,
                                                                         text='Symmetry breaking\nfor all components:')
        self.__all_children_symmetry_breaking_checkbox = ttk.Checkbutton(self.__left_frame,
                                                                         variable=self.__all_children_symmetry_breaking_checkbox_var)
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
        self.__hierarchy_tree.grid(row=0, column=1, sticky=tk.NSEW)
        self.__left_frame.grid(row=0, column=0, sticky=tk.NSEW, padx=FRAME_PAD_X, pady=FRAME_PAD_Y)

        self.__cmp_label.grid(row=0, column=0, columnspan=2, sticky=tk.EW, pady=CONTROL_PAD_Y)

        self.__symm_breaking_checkbox_label.grid(row=1, column=0, sticky=tk.W, pady=CONTROL_PAD_Y, padx=CONTROL_PAD_X)
        self.__symm_breaking_checkbox.grid(row=1, column=1, sticky=tk.W, padx=CONTROL_PAD_X, pady=CONTROL_PAD_Y)

        self.__count_spinbox_label.grid(row=2, column=0, sticky=tk.W, padx=CONTROL_PAD_X, pady=CONTROL_PAD_Y)
        self.__count_spinbox.grid(row=2, column=1, sticky=tk.NSEW, padx=CONTROL_PAD_X, pady=CONTROL_PAD_Y)

        self.__all_children_count_spinbox_label.grid(row=3, column=0, sticky=tk.W, padx=CONTROL_PAD_X, pady=CONTROL_PAD_Y)
        self.__all_children_count_spinbox.grid(row=3, column=1, sticky=tk.NSEW, padx=CONTROL_PAD_X, pady=CONTROL_PAD_Y)
        self.__all_children_symmetry_breaking_checkbox_label.grid(row=4, column=0, sticky=tk.W, pady=CONTROL_PAD_Y, padx=CONTROL_PAD_X)
        self.__all_children_symmetry_breaking_checkbox.grid(row=4, column=1, sticky=tk.W, padx=CONTROL_PAD_X, pady=CONTROL_PAD_Y)
        self.__apply_to_all_children_button.grid(row=5, column=0, columnspan=2, sticky=tk.NSEW, padx=CONTROL_PAD_X, pady=CONTROL_PAD_Y)

        self.__left_frame.columnconfigure(1, weight=1)
        self._frame.columnconfigure(0, weight=1, uniform='fred')
        self._frame.columnconfigure(1, weight=3, uniform='fred')
        self._frame.rowconfigure(0, weight=1)
        # Hide widgets
        self.__symm_breaking_checkbox_label.grid_forget()
        self.__symm_breaking_checkbox.grid_forget()
        self.__count_spinbox_label.grid_forget()
        self.__count_spinbox.grid_forget()
        self.__all_children_count_spinbox_label.grid_forget()
        self.__all_children_count_spinbox.grid_forget()
        self.__all_children_symmetry_breaking_checkbox_label.grid_forget()
        self.__all_children_symmetry_breaking_checkbox.grid_forget()
        self.__apply_to_all_children_button.grid_forget()

    # SubscribesToListeners
    def _subscribe_to_events(self):
        pub.subscribe(self.__on_model_loaded, actions.MODEL_LOADED)
        pub.subscribe(self.__build_tree, actions.HIERARCHY_EDITED)
        pub.subscribe(self._reset, actions.RESET)

    @staticmethod
    def __extract_values(cmp: Component) -> Tuple[Any, ...]:
        return (cmp.count if cmp.count else '',
                BOOLEAN_TO_STRING_DICT[cmp.symmetry_breaking])

    def __on_model_loaded(self):
        self.__build_tree()

    def __build_tree(self) -> None:
        self.__hierarchy_tree.set_items(self.__state.model.hierarchy)

    def __on_select_tree_item(self, cmp_id: int):
        selected_cmp: Component = self.__state.model.get_component_by_id(cmp_id)
        self.__selected_component = selected_cmp
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
            self.__all_children_symmetry_breaking_checkbox_label.grid(row=4, column=0, sticky=tk.W, pady=CONTROL_PAD_Y,
                                                                      padx=CONTROL_PAD_X)
            self.__all_children_symmetry_breaking_checkbox.grid(row=4, column=1, sticky=tk.W, padx=CONTROL_PAD_X,
                                                                pady=CONTROL_PAD_Y)
            self.__apply_to_all_children_button.grid(row=5, column=0, columnspan=2, sticky=tk.NSEW, pady=CONTROL_PAD_Y,  padx=CONTROL_PAD_X)
            # Hide for single
            self.__count_spinbox_label.grid_forget()
            self.__count_spinbox.grid_forget()
            self.__symm_breaking_checkbox_label.grid_forget()
            self.__symm_breaking_checkbox.grid_forget()

    # Resetable
    def _reset(self) -> None:
        # TODO
        self.__selected_component = None
        # Hide widgets
        self.__all_children_symmetry_breaking_checkbox_label.grid_forget()
        self.__all_children_symmetry_breaking_checkbox.grid_forget()
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

    def __on_symmetry_breaking_toggled(self, _1, _2, _3):
        if self.__selected_component and self.__hierarchy_tree:
            self.__selected_component.symmetry_breaking = self.__symm_breaking_checkbox_var.get()
            self.__hierarchy_tree.update_values(self.__selected_component)

    def __on_count_changed(self, _1, _2, _3):
        if self.__selected_component and self.__hierarchy_tree:
            try:
                self.__selected_component.count = self.__count_spinbox_var.get()
            except tk.TclError as e:
                print(e)
                self.__selected_component.count = None
            finally:
                self.__hierarchy_tree.update_values(self.__selected_component)

    def __apply_to_all_children(self):
        if self.__selected_component:
            count = 0
            symm_breaking = True
            try:
                count = self.__all_children_count_spinbox_var.get()
                symm_breaking = self.__all_children_symmetry_breaking_checkbox_var.get()
            except tk.TclError as e:
                print(e)
            finally:
                updated_components = self.__state.model.set_instances_of_all_components_children(
                    self.__selected_component, count, symm_breaking)
                self.__hierarchy_tree.update_values(*updated_components)
