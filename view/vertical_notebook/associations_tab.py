import math
import tkinter as tk
from tkinter import ttk
from typing import Tuple, Any, List

from pubsub import pub

import actions
from model.component import Component
from model.association import Association
from state import State
from view.abstract.tab import Tab
from view.tree_view_column import Column
from view.hierarchy_tree import HierarchyTree
from view.abstract.has_common_setup import HasCommonSetup
from view.abstract.subscribes_to_listeners import SubscribesToListeners
from view.abstract.has_hierarchy_tree import HasHierarchyTree
from view.abstract.resetable import Resetable
from view.style import FONT

TAB_NAME = 'Associations'

CONTROL_PAD_Y = 3
CONTROL_PAD_X = 20

FRAME_PAD_Y = 10
FRAME_PAD_X = 10


class AssociationsTab(Tab,
                      HasCommonSetup,
                      SubscribesToListeners,
                      HasHierarchyTree,
                      Resetable):
    def __init__(self, parent, parent_notebook, *args, **kwargs):
        Tab.__init__(self, parent_notebook, TAB_NAME, *args, **kwargs)

        HasCommonSetup.__init__(self)
        SubscribesToListeners.__init__(self)
        HasHierarchyTree.__init__(self)

        self.__state = State()

    # HasCommonSetup
    def _create_widgets(self):
        self.__left_frame = ttk.Frame(self.frame)
        # Cmp label
        self.__cmp_label_var = tk.StringVar(value='COMPONENT')
        self.__cmp_label = ttk.Label(self.__left_frame, textvariable=self.__cmp_label_var,
                                     anchor=tk.CENTER, style='Big.TLabel')
        # Has association checkbox
        self.__has_association_checkbox_var = tk.BooleanVar(value=False)
        self.__has_association_checkbox_var.trace('w', self.__on_has_association_changed)
        self.__has_association_checkbox_label = ttk.Label(self.__left_frame, text='Has association?')
        self.__has_association_checkbox = ttk.Checkbutton(self.__left_frame,
                                                          variable=self.__has_association_checkbox_var)
        # Has min checkbox
        self.__has_min_checkbox_var = tk.BooleanVar(value=False)
        self.__has_min_checkbox_var.trace('w', self.__on_has_min_changed)
        self.__has_min_checkbox_label = ttk.Label(self.__left_frame, text='Has min?')
        self.__has_min_checkbox = ttk.Checkbutton(self.__left_frame, state=tk.DISABLED,
                                                  variable=self.__has_min_checkbox_var)
        # Min spinbox
        self.__min_spinbox_var = tk.IntVar(value='')
        self.__min_spinbox_var.trace('w', self.__on_min_changed)
        self.__min_spinbox = ttk.Spinbox(self.__left_frame, from_=0, to=math.inf, state=tk.DISABLED,
                                         textvariable=self.__min_spinbox_var, font=FONT)
        # Has max checkbox
        self.__has_max_checkbox_var = tk.BooleanVar(value=False)
        self.__has_max_checkbox_var.trace('w', self.__on_has_max_changed)
        self.__has_max_checkbox_label = ttk.Label(self.__left_frame, text='Has max?')
        self.__has_max_checkbox = ttk.Checkbutton(self.__left_frame, state=tk.DISABLED,
                                                  variable=self.__has_max_checkbox_var)
        # Max spinbox
        self.__max_spinbox_var = tk.IntVar(value='')
        self.__max_spinbox_var.trace('w', self.__on_max_changed)
        self.__max_spinbox = ttk.Spinbox(self.__left_frame, from_=0, to=math.inf, state=tk.DISABLED,
                                         textvariable=self.__max_spinbox_var, font=FONT)

    def _setup_layout(self):
        self.__left_frame.grid(row=0, column=0, sticky=tk.NSEW, pady=FRAME_PAD_Y, padx=FRAME_PAD_X)
        self.__cmp_label.grid(row=0, column=0, columnspan=4, sticky=tk.EW, pady=CONTROL_PAD_Y)
        self.__has_association_checkbox_label.grid(row=1, column=0, columnspan=2, sticky=tk.W, pady=CONTROL_PAD_Y)
        self.__has_association_checkbox.grid(row=1, column=2, columnspan=2, sticky=tk.E, pady=CONTROL_PAD_Y)
        self.__has_min_checkbox_label.grid(row=2, column=0, sticky=tk.W, pady=CONTROL_PAD_Y)
        self.__has_min_checkbox.grid(row=2, column=1, sticky=tk.E, pady=CONTROL_PAD_Y)
        self.__has_max_checkbox_label.grid(row=2, column=2, sticky=tk.W, pady=CONTROL_PAD_Y)
        self.__has_max_checkbox.grid(row=2, column=3, sticky=tk.E, pady=CONTROL_PAD_Y)
        self.__min_spinbox.grid(row=3, column=0, columnspan=2, sticky=tk.NSEW, pady=CONTROL_PAD_Y)
        self.__max_spinbox.grid(row=3, column=2, columnspan=2, sticky=tk.NSEW, pady=CONTROL_PAD_Y)

        self.__left_frame.columnconfigure(0, weight=1)
        self.__left_frame.columnconfigure(1, weight=1)
        self.__left_frame.columnconfigure(2, weight=1)
        self.__left_frame.columnconfigure(3, weight=1)

        self.frame.rowconfigure(0, weight=1)
        self.frame.columnconfigure(0, weight=1, uniform='fred')
        self.frame.columnconfigure(1, weight=3, uniform='fred')

        # Hide widgets
        self.__left_frame.grid_forget()

    # SubscribesToListeners
    def _subscribe_to_listeners(self):
        pub.subscribe(self.__on_model_loaded, actions.MODEL_LOADED)
        # TODO:
        pub.subscribe(self._build_tree, actions.HIERARCHY_CREATED)
        pub.subscribe(self._build_tree, actions.HIERARCHY_EDITED)
        pub.subscribe(self._reset, actions.RESET)

    # HasHierarchyTree
    def _on_select_tree_item(self, cmp_id: int) -> None:
        selected_cmp: Component = self.__state.model.get_component_by_id(cmp_id)
        self._selected_component = selected_cmp

        if selected_cmp.association:
            self.__has_association_checkbox_var.set(True)
            if selected_cmp.association.min_:
                self.__has_min_checkbox_var.set(True)
                self.__min_spinbox_var.set(selected_cmp.association.min_)
            if selected_cmp.association.max_:
                self.__has_max_checkbox_var.set(True)
                self.__max_spinbox_var.set(selected_cmp.association.max_)
        else:
            self.__disable_widgets()
            self.__has_association_checkbox_var.set(False)
        self.__cmp_label_var.set(selected_cmp.name)
        self.__left_frame.grid(row=0, column=0, sticky=tk.NSEW, pady=FRAME_PAD_Y, padx=FRAME_PAD_X) # show

    @property
    def _columns(self) -> List[Column]:
        return [ Column('has_association', 'Has association?'),
                 Column('min', 'Min'),
                 Column('max', 'Max') ]

    def _extract_values(self, cmp: Component) -> Tuple[Any, ...]:
        has_association = ''
        min_ = ''
        max_ = ''
        if cmp.association:
            has_association = 'Yes'
            min_ = cmp.association.min_ if cmp.association.min_ is not None else ''
            max_ = cmp.association.max_ if cmp.association.max_ is not None else ''
        return has_association, min_, max_

    def __on_model_loaded(self):
        self._build_tree()

    def _build_tree(self) -> None:
        if self._hierarchy_tree:
            self._destroy_tree()

        self._hierarchy_tree = HierarchyTree(self.frame, self.__state.model.hierarchy, columns=self._columns,
                                             on_select_callback=self._on_select_tree_item,
                                             extract_values=self._extract_values)
        self._hierarchy_tree.grid(row=0, column=1, sticky=tk.NSEW)

    def _destroy_tree(self) -> None:
        self._hierarchy_tree.destroy_()
        self._hierarchy_tree = None

    # Resetable
    def _reset(self) -> None:
        if self._hierarchy_tree:
            self._destroy_tree()

        self._selected_component = None
        # Hide widgets
        self.__left_frame.grid_forget()
        # Set entries to default
        self.__has_association_checkbox_var.set(False)
        self.__has_min_checkbox_var.set(False)
        self.__has_min_checkbox.config(state=tk.DISABLED)
        self.__min_spinbox_var.set('')  # TODO: dangerous
        self.__min_spinbox.config(state=tk.DISABLED)
        self.__has_max_checkbox_var.set(False)
        self.__has_max_checkbox.config(state=tk.DISABLED)
        self.__max_spinbox_var.set('')  # TODO: dangerous
        self.__max_spinbox.config(state=tk.DISABLED)

    # Class-specific
    def __disable_widgets(self):
        self.__has_min_checkbox_var.set(False)
        self.__has_max_checkbox_var.set(False)
        self.__has_max_checkbox.config(state=tk.DISABLED)
        self.__has_min_checkbox.config(state=tk.DISABLED)
        self.__max_spinbox.config(state=tk.DISABLED)
        self.__min_spinbox.config(state=tk.DISABLED)
        self.__min_spinbox_var.set('')
        self.__max_spinbox_var.set('')

    def __on_has_association_changed(self, _1, _2, _3):
        if self._hierarchy_tree and self._selected_component:
            has_association = self.__has_association_checkbox_var.get()
            if has_association:
                if not self._selected_component.association:
                    self._selected_component.association = Association()
                self.__has_min_checkbox.config(state=tk.NORMAL)
                self.__has_max_checkbox.config(state=tk.NORMAL)
            else:
                self.__disable_widgets()
                self._selected_component.association = None
            self._hierarchy_tree.update_values([self._selected_component])

    def __on_has_min_changed(self, _1, _2, _3):
        if self._selected_component:
            has_min = self.__has_min_checkbox_var.get()
            if has_min:
                self.__min_spinbox.config(state=tk.ACTIVE)
                if self._selected_component.association and self._selected_component.association.min_:
                    self.__min_spinbox_var.set(self._selected_component.association.min_)
                else:
                    self.__min_spinbox_var.set(0)
            else:
                self.__min_spinbox_var.set('')
                self.__min_spinbox.config(state=tk.DISABLED)

    def __on_has_max_changed(self, _1, _2, _3):
        if self._selected_component:
            has_max = self.__has_max_checkbox_var.get()
            if has_max:
                self.__max_spinbox.config(state=tk.ACTIVE)
                if self._selected_component.association.max_:
                    self.__max_spinbox_var.set(self._selected_component.association.max_)
                else:
                    if self._selected_component.association.min_:
                        # If component has a minimum association, set the value of Spinbox to it
                        self.__max_spinbox_var.set(self._selected_component.association.min_)
                    else:
                        # Otherwise set it to 0
                        self.__max_spinbox_var.set(0)
            else:
                self.__max_spinbox_var.set('')
                self.__max_spinbox.config(state=tk.DISABLED)

    def __on_min_changed(self, _1, _2, _3):
        if self._selected_component and self._hierarchy_tree:
            if self._selected_component.association:
                # This gets triggered at unpredicted moments (e.g. enabling and disabling widgets
                # so it's necessary to check this condition.
                try:
                    min_ = self.__min_spinbox_var.get()
                    self._selected_component.association.min_ = min_
                    if self._selected_component.association.max_ \
                       and self._selected_component.association.max_ < min_:  # If max < min; set max to min
                        self._selected_component.association.max_ = min_
                        self.__max_spinbox_var.set(min_)
                except tk.TclError as e:
                    print(e)
                    self._selected_component.association.min_ = None
                    # self._selected_component.association.min_ = ''  # TODO: URGENT! co to jest??
                finally:
                    self._hierarchy_tree.update_values([self._selected_component])

    def __on_max_changed(self, _1, _2, _3):
        if self._selected_component and self._hierarchy_tree:
            if self._selected_component.association:
                try:
                    max_ = self.__max_spinbox_var.get()
                    self._selected_component.association.max_ = max_
                    if self._selected_component.association.min_ \
                       and self._selected_component.association.min_ > max_:  # If min > max; set min to max
                        self._selected_component.association.min_ = max_
                        self.__min_spinbox_var.set(max_)
                except tk.TclError as e:
                    print(e)
                    self._selected_component.association.max_ = None
                    # self._selected_component.association.max_ = ''  # TODO: URGENT! co to jest??
                finally:
                    self._hierarchy_tree.update_values([self._selected_component])
