import math
import tkinter as tk
from tkinter import ttk
from typing import Any, Tuple, Optional

from pubsub import pub

import actions
from model.component import Component
from state import State
from view.abstract.has_common_setup import HasCommonSetup
from view.abstract.subscribes_to_events import SubscribesToEvents
from view.abstract.tab import Tab
from view.abstract.resetable import Resetable
from view.scrollbars_listbox import ScrollbarListbox
from view.tree_view_column import Column
from view.common import trim_string, BOOLEAN_TO_STRING_DICT, change_controls_state, set_spinbox_var_value

TAB_NAME = 'Instances'
LABEL_LENGTH = 15
TREEVIEW_HEADING = 'Component'
EXACT_COUNT_LABEL_TEXT = 'Count:'
MIN_COUNT_LABEL_TEXT = 'Min:'

CONTROL_PAD_Y = 3
CONTROL_PAD_X = 3

FRAME_PAD_Y = 10
FRAME_PAD_X = 10


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
                                                 columns=[Column('Count'),
                                                          Column('Min'),
                                                          Column('Max'),
                                                          Column('Symmetry breaking?')],
                                                 values=self.__state.model.hierarchy)

        self.__left_frame = ttk.Frame(self._frame)

        self.__global_symmetry_breaking_frame = ttk.Frame(self.__left_frame)
        self.__global_symmetry_breaking_checkbox_label = ttk.Label(self.__global_symmetry_breaking_frame,
                                                                   text='Symmetry breaking\n'
                                                                        'for all components:')
        self.__global_symmetry_breaking_checkbox_var = tk.BooleanVar(value=False)
        self.__global_symmetry_breaking_checkbox = ttk.Checkbutton(self.__global_symmetry_breaking_frame,
                                                                   variable=self.__global_symmetry_breaking_checkbox_var)
        self.__apply_global_symmetry_breaking_button = ttk.Button(self.__global_symmetry_breaking_frame, text='Apply',
                                                                  command=self.__apply_symmetry_breaking_for_all_components)

        self.__component_separator = ttk.Separator(self.__left_frame, orient=tk.HORIZONTAL)

        self.__cmp_label_var = tk.StringVar(value='')
        self.__cmp_label = ttk.Label(self.__left_frame, textvariable=self.__cmp_label_var, style='Big.TLabel',
                                     anchor=tk.CENTER)

        self.__symm_breaking_checkbox_var = tk.BooleanVar(value=False)
        self.__symm_breaking_checkbox_var.trace('w', self.__on_symmetry_breaking_toggled)
        self.__symm_breaking_checkbox_label = ttk.Label(self.__left_frame, text='Symmetry\nbreaking:')
        self.__symm_breaking_checkbox = ttk.Checkbutton(self.__left_frame, variable=self.__symm_breaking_checkbox_var)

        self.__exact_value_radiobutton_var = tk.BooleanVar(value=True)
        self.__exact_value_radiobutton_var.trace('w', self.__on_exact_value_radiobutton_changed)
        self.__exact_value_radiobutton = ttk.Radiobutton(self.__left_frame, value=True, text='Exact', state=tk.DISABLED,
                                                         variable=self.__exact_value_radiobutton_var)
        self.__range_radiobutton = ttk.Radiobutton(self.__left_frame, text='Range', value=False, state=tk.DISABLED,
                                                   variable=self.__exact_value_radiobutton_var)

        self.__exact_minimum_spinbox_label_var = tk.StringVar(value=EXACT_COUNT_LABEL_TEXT)
        self.__exact_minimum_spinbox_label = ttk.Label(self.__left_frame,
                                                       textvariable=self.__exact_minimum_spinbox_label_var)
        self.__exact_minimum_spinbox_var = tk.IntVar(value='')
        self.__exact_minimum_spinbox_var.trace('w', self.__on_count_changed)
        self.__exact_minimum_spinbox = ttk.Spinbox(self.__left_frame, from_=0, to=math.inf, state=tk.DISABLED,
                                                   textvariable=self.__exact_minimum_spinbox_var)

        self.__max_spinbox_label = ttk.Label(self.__left_frame, text='Max:')
        self.__max_spinbox_var = tk.IntVar()
        self.__max_spinbox_var.trace('w', self.__on_max_changed)
        self.__max_spinbox = ttk.Spinbox(self.__left_frame, from_=1, to=math.inf,
                                         textvariable=self.__max_spinbox_var)

        self.__apply_symmetry_breaking_to_all_children_button = ttk.Button(self.__left_frame,
                                                                           text='Apply to children',
                                                                           command=self.__apply_symmetry_breaking_to_all_children,
                                                                           style='SmallFont.TButton')

        self.__apply_count_to_all_children_button = ttk.Button(self.__left_frame, text='Apply to all children',
                                                               command=self.__apply_count_to_all_children)

    def _setup_layout(self):
        self.__hierarchy_tree.grid(row=0, column=1, sticky=tk.NSEW)
        self.__left_frame.grid(row=0, column=0, sticky=tk.NSEW, padx=FRAME_PAD_X, pady=FRAME_PAD_Y)

        self.__global_symmetry_breaking_frame.grid(row=0, column=0, columnspan=4, sticky=tk.NSEW)
        self.__global_symmetry_breaking_frame.columnconfigure(0, weight=1)
        self.__global_symmetry_breaking_frame.columnconfigure(1, weight=1)
        self.__global_symmetry_breaking_frame.columnconfigure(2, weight=1)

        self.__global_symmetry_breaking_checkbox_label.grid(row=0, column=0, sticky=tk.W, pady=CONTROL_PAD_Y, padx=CONTROL_PAD_X)
        self.__global_symmetry_breaking_checkbox.grid(row=0, column=1, sticky=tk.W, pady=CONTROL_PAD_Y, padx=CONTROL_PAD_X)
        self.__apply_global_symmetry_breaking_button.grid(row=0, column=2, sticky=tk.EW, pady=CONTROL_PAD_Y, padx=CONTROL_PAD_X)

        self.__component_separator.grid(row=1, column=0, columnspan=4, sticky=tk.EW, pady=CONTROL_PAD_Y, padx=CONTROL_PAD_X)

        self.__cmp_label.grid(row=2, column=0, columnspan=4, sticky=tk.EW, pady=CONTROL_PAD_Y)

        self.__symm_breaking_checkbox_label.grid(row=3, column=0, sticky=tk.W, pady=CONTROL_PAD_Y, padx=CONTROL_PAD_X)
        self.__symm_breaking_checkbox.grid(row=3, column=1, sticky=tk.NW, padx=CONTROL_PAD_X, pady=CONTROL_PAD_Y)
        self.__apply_symmetry_breaking_to_all_children_button.grid(row=3, column=2, columnspan=2, padx=CONTROL_PAD_X, pady=CONTROL_PAD_Y)

        self.__exact_value_radiobutton.grid(row=4, column=0, sticky=tk.W, padx=CONTROL_PAD_X, pady=CONTROL_PAD_Y)
        self.__range_radiobutton.grid(row=4, column=1, sticky=tk.W, padx=CONTROL_PAD_X, pady=CONTROL_PAD_Y)

        self.__exact_minimum_spinbox_label.grid(row=5, column=0, sticky=tk.W, padx=CONTROL_PAD_X, pady=CONTROL_PAD_Y)
        self.__exact_minimum_spinbox.grid(row=5, column=1, sticky=tk.EW, padx=CONTROL_PAD_X, pady=CONTROL_PAD_Y)
        self.__max_spinbox_label.grid(row=5, column=2, sticky=tk.W, padx=CONTROL_PAD_X, pady=CONTROL_PAD_Y)
        self.__max_spinbox.grid(row=5, column=3, sticky=tk.EW, padx=CONTROL_PAD_X, pady=CONTROL_PAD_Y)

        self.__apply_count_to_all_children_button.grid(row=6, column=0, columnspan=4, sticky=tk.NSEW, padx=CONTROL_PAD_X, pady=CONTROL_PAD_Y)

        # Hide 'for all children' widgets
        self.__apply_symmetry_breaking_to_all_children_button.grid_forget()
        self.__max_spinbox_label.grid_forget()
        self.__max_spinbox.grid_forget()
        self.__apply_count_to_all_children_button.grid_forget()

        self.__left_frame.columnconfigure(0, weight=1, uniform='fred')
        self.__left_frame.columnconfigure(1, weight=1, uniform='fred')
        self.__left_frame.columnconfigure(2, weight=1, uniform='fred')
        self.__left_frame.columnconfigure(3, weight=1, uniform='fred')

        self._frame.columnconfigure(0, weight=1, uniform='fred')
        self._frame.columnconfigure(1, weight=3, uniform='fred')
        self._frame.rowconfigure(0, weight=1)

    # SubscribesToListeners
    def _subscribe_to_events(self):
        pub.subscribe(self.__on_model_loaded, actions.MODEL_LOADED)
        pub.subscribe(self.__build_tree, actions.HIERARCHY_EDITED)
        pub.subscribe(self._reset, actions.RESET)

    @staticmethod
    def __extract_values(cmp: Component) -> Tuple[Any, ...]:
        return (cmp.count if cmp.count else '',
                cmp.min_count if cmp.min_count is not None else '',
                cmp.max_count if cmp.max_count is not None else '',
                BOOLEAN_TO_STRING_DICT[cmp.symmetry_breaking])

    def __on_model_loaded(self):
        self.__build_tree()

    def __build_tree(self) -> None:
        self.__hierarchy_tree.set_items(self.__state.model.hierarchy)

    def __on_select_tree_item(self, cmp_id: int):
        selected_cmp: Component = self.__state.model.get_component(id_=cmp_id)
        self.__selected_component = selected_cmp
        self.__cmp_label_var.set(trim_string(selected_cmp.name, length=LABEL_LENGTH))
        self.__exact_value_radiobutton_var.set(selected_cmp.exact)
        # Enable symmetry breaking checkbox & spinbox
        change_controls_state(tk.NORMAL,
                              self.__exact_minimum_spinbox,
                              self.__symm_breaking_checkbox,
                              self.__range_radiobutton,
                              self.__exact_value_radiobutton,
                              self.__exact_minimum_spinbox)
        if selected_cmp.is_leaf:
            # Set the spinbox values
            if selected_cmp.exact:
                set_spinbox_var_value(self.__exact_minimum_spinbox_var, selected_cmp.count)
            else:
                set_spinbox_var_value(self.__exact_minimum_spinbox_var, selected_cmp.min_count)
                set_spinbox_var_value(self.__max_spinbox_var, selected_cmp.max_count)

            self.__symm_breaking_checkbox_var.set(selected_cmp.symmetry_breaking)
            self.__apply_symmetry_breaking_to_all_children_button.grid_forget()
            self.__apply_count_to_all_children_button.grid_forget()
        else:
            # Show apply to all children
            self.__apply_symmetry_breaking_to_all_children_button.grid(row=3, column=2, columnspan=2, padx=CONTROL_PAD_X, pady=CONTROL_PAD_Y)
            self.__apply_count_to_all_children_button.grid(row=6, column=0, columnspan=4, sticky=tk.NSEW, padx=CONTROL_PAD_X, pady=CONTROL_PAD_Y)
            # Reset symmetry breaking for all components
            self.__symm_breaking_checkbox_var.set(False)

    # Resetable
    def _reset(self) -> None:
        self.__selected_component = None
        # Disable widgets
        change_controls_state(tk.DISABLED,
                              self.__exact_minimum_spinbox,
                              self.__symm_breaking_checkbox,
                              self.__range_radiobutton,
                              self.__exact_value_radiobutton,
                              self.__exact_minimum_spinbox)

        # Hide 'for all children' widgets
        self.__apply_symmetry_breaking_to_all_children_button.grid_forget()
        self.__max_spinbox_label.grid_forget()
        self.__max_spinbox.grid_forget()
        self.__apply_count_to_all_children_button.grid_forget()

        # Set entries to default
        self.__exact_minimum_spinbox_var.set('')
        self.__max_spinbox_var.set('')
        self.__cmp_label_var.set('')
        self.__symm_breaking_checkbox_var.set(False)
        self.__global_symmetry_breaking_checkbox_var.set(False)
        # Clear the tree
        self.__hierarchy_tree.set_items([])

    def __on_symmetry_breaking_toggled(self, *_):
        # if self.__selected_component and self.__hierarchy_tree:
        if self.__selected_component and self.__selected_component.is_leaf:
            self.__selected_component.symmetry_breaking = self.__symm_breaking_checkbox_var.get()
            self.__hierarchy_tree.update_values(self.__selected_component)

    def __on_count_changed(self, *_):
        if self.__selected_component:
            exact = self.__exact_value_radiobutton_var.get()
            try:
                value = self.__exact_minimum_spinbox_var.get()
                if exact:
                    if self.__selected_component.is_leaf:
                        self.__selected_component.count = value
                        # Reset min/max counter
                        self.__selected_component.min_count = None
                        self.__selected_component.max_count = None
                else:
                    max_value = self.__max_spinbox_var.get()
                    if self.__selected_component.is_leaf:
                        self.__selected_component.min_count = value
                        # Reset count property
                        self.__selected_component.count = None
                    if value >= max_value:
                        new_max_value = value + 1
                        self.__max_spinbox_var.set(new_max_value)
                        if self.__selected_component.is_leaf:
                            self.__selected_component.max_count = new_max_value
            except tk.TclError as e:
                print(e)
                self.__selected_component.count = None  # Reset both
                self.__selected_component.min_count = None
            finally:
                self.__hierarchy_tree.update_values(self.__selected_component)

    def __apply_count_to_all_children(self):
        if self.__selected_component:
            exact = self.__exact_value_radiobutton_var.get()
            if exact:
                count = None
                try:
                    count = self.__exact_minimum_spinbox_var.get()
                except tk.TclError as e:
                    print(e)
                finally:
                    updated_cmps = self.__state.model.set_components_leaf_children_properties(self.__selected_component,
                                                                                              exact=True, count=count,
                                                                                              min_count=None,
                                                                                              max_count=None)
            else:
                min_count = None
                max_count = None
                try:
                    min_count = self.__exact_minimum_spinbox_var.get()
                    max_count = self.__max_spinbox_var.get()
                except tk.TclError as e:
                    print(e)
                finally:
                    updated_cmps = self.__state.model.set_components_leaf_children_properties(self.__selected_component,
                                                                                              exact=False,
                                                                                              count=None,
                                                                                              min_count=min_count,
                                                                                              max_count=max_count)
            self.__hierarchy_tree.update_values(*updated_cmps)

    def __apply_symmetry_breaking_to_all_children(self):
        if self.__selected_component:
            symm_breaking = True
            try:
                symm_breaking = self.__symm_breaking_checkbox_var.get()
            except tk.TclError as e:
                print(e)
            finally:
                updated_cmps = self.__state.model.set_components_leaf_children_properties(self.__selected_component,
                                                                                          symmetry_breaking=symm_breaking)
                self.__hierarchy_tree.update_values(*updated_cmps)

    def __on_exact_value_radiobutton_changed(self, *_):
        if self.__selected_component:
            self.__exact_minimum_spinbox_var.set(0)
            self.__max_spinbox_var.set(0)

            self.__selected_component.count = None
            self.__selected_component.min_count = None
            self.__selected_component.max_count = None

            exact_value = self.__exact_value_radiobutton_var.get()
            if exact_value:
                self.__max_spinbox_label.grid_forget()  # Hide 'Max' label and spinbox
                self.__max_spinbox.grid_forget()
                self.__exact_minimum_spinbox_label_var.set(EXACT_COUNT_LABEL_TEXT)
            else:
                # Restore max widgets
                self.__max_spinbox_label.grid(row=5, column=2, sticky=tk.W, padx=CONTROL_PAD_X, pady=CONTROL_PAD_Y)
                self.__max_spinbox.grid(row=5, column=3, sticky=tk.EW, padx=CONTROL_PAD_X, pady=CONTROL_PAD_Y)
                self.__exact_minimum_spinbox_label_var.set(MIN_COUNT_LABEL_TEXT)

            if self.__selected_component.is_leaf:
                self.__selected_component.exact = exact_value
                self.__hierarchy_tree.update_values(self.__selected_component)

    def __on_max_changed(self, *_):
        if self.__selected_component:
            try:
                max_value = self.__max_spinbox_var.get()
                if self.__selected_component.is_leaf:
                    self.__selected_component.max_count = max_value

                min_value = self.__exact_minimum_spinbox_var.get()
                if max_value <= min_value and max_value >= 1:
                    new_min_value = max_value - 1
                    self.__exact_minimum_spinbox_var.set(new_min_value)
                    if self.__selected_component.is_leaf:
                        self.__selected_component.min_count = new_min_value
            except tk.TclError as e:
                print(e)
            finally:
                self.__hierarchy_tree.update_values(self.__selected_component)

    def __apply_symmetry_breaking_for_all_components(self):
        if self.__hierarchy_tree:
            symm_breaking = self.__global_symmetry_breaking_checkbox_var.get()
            updated_cmps = self.__state.model.set_all_leaf_components_properties(symmetry_breaking=symm_breaking)
            self.__hierarchy_tree.update_values(*updated_cmps)


