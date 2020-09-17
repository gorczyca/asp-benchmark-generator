import math
import tkinter as tk
from tkinter import ttk
from typing import Tuple, Any, Optional

from pubsub import pub

import actions
from model import Component, Association
from state import State
from view.tree_view_column import Column
from view.scrollbars_listbox import ScrollbarListbox
from view.abstract import Tab, HasCommonSetup, SubscribesToEvents, Resetable, Resetable
from view.common import change_controls_state, trim_string
from view.style import FONT

TAB_NAME = 'Associations'
TREEVIEW_HEADING = 'Component'

CONTROL_PAD_Y = 3
CONTROL_PAD_X = 20

FRAME_PAD_Y = 10
FRAME_PAD_X = 10


class AssociationsTab(Tab,
                      HasCommonSetup,
                      SubscribesToEvents,
                      Resetable):
    """Used to set the number of information about the associations between the root component and other components.

    Attributes:
        __selected_component: Currently selected component in the components taxonomy view.
    """
    def __init__(self, parent_notebook):
        self.__state = State()
        self.__selected_component: Optional[Component] = None

        Tab.__init__(self, parent_notebook, TAB_NAME)
        HasCommonSetup.__init__(self)
        SubscribesToEvents.__init__(self)

    # HasCommonSetup
    def _create_widgets(self):
        self.__taxonomy_tree = ScrollbarListbox(self,
                                                 on_select_callback=self.__on_select_tree_item,
                                                 heading=TREEVIEW_HEADING,
                                                 extract_id=lambda x: x.id_,
                                                 extract_text=lambda x: x.name,
                                                 extract_ancestor=lambda x: '' if x.parent_id is None else x.parent_id,
                                                 extract_values=self.__extract_values,
                                                 values=self.__state.model.taxonomy,
                                                 columns=[Column('Has association?'),
                                                          Column('Min'),
                                                          Column('Max')])

        self.__left_frame = ttk.Frame(self)
        # Cmp label
        self.__cmp_label_var = tk.StringVar(value='')
        self.__cmp_label = ttk.Label(self.__left_frame, textvariable=self.__cmp_label_var,
                                     anchor=tk.CENTER, style='Big.TLabel')
        # Has association checkbox
        self.__has_association_checkbox_var = tk.BooleanVar(value=False)
        self.__has_association_checkbox_var.trace('w', self.__on_has_association_changed)
        self.__has_association_checkbox_label = ttk.Label(self.__left_frame, text='Has association?')
        self.__has_association_checkbox = ttk.Checkbutton(self.__left_frame, state=tk.DISABLED,
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
        self.__taxonomy_tree.grid(row=0, column=1, sticky=tk.NSEW)
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

        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1, uniform='fred')
        self.columnconfigure(1, weight=3, uniform='fred')

    # SubscribesToListeners
    def _subscribe_to_events(self):
        pub.subscribe(self.__on_taxonomy_edited, actions.TAXONOMY_EDITED)
        pub.subscribe(self.__on_taxonomy_edited, actions.MODEL_LOADED)
        pub.subscribe(self._reset, actions.RESET)

    # Taxonomy Treeview
    def __on_select_tree_item(self, cmp_id: int) -> None:
        """Executed whenever a tree item is selected (by mouse click).

        :param cmp_id: Id of the selected component.
        """
        selected_cmp = self.__state.model.get_component(id_=cmp_id)
        if selected_cmp:
            change_controls_state(tk.NORMAL, self.__has_association_checkbox)
            self.__selected_component = selected_cmp
            if selected_cmp.association:
                self.__has_association_checkbox_var.set(True)
                change_controls_state(tk.NORMAL,
                                      self.__has_min_checkbox,
                                      self.__has_max_checkbox)
                if selected_cmp.association.min_:
                    self.__has_min_checkbox_var.set(True)
                    self.__min_spinbox_var.set(selected_cmp.association.min_)
                    change_controls_state(tk.NORMAL, self.__min_spinbox)
                else:
                    self.__has_min_checkbox_var.set(False)
                    change_controls_state(tk.DISABLED, self.__min_spinbox)
                    self.__min_spinbox_var.set('')
                if selected_cmp.association.max_:
                    self.__has_max_checkbox_var.set(True)
                    self.__max_spinbox_var.set(selected_cmp.association.max_)
                    change_controls_state(tk.NORMAL, self.__max_spinbox)
                else:
                    self.__has_max_checkbox_var.set(False)
                    change_controls_state(tk.DISABLED, self.__max_spinbox)
                    self.__max_spinbox_var.set('')
            else:
                self.__has_association_checkbox_var.set(False)
                self.__has_min_checkbox_var.set(False)  # Reset and block controls
                self.__has_max_checkbox_var.set(False)
                self.__min_spinbox_var.set('')
                self.__max_spinbox_var.set('')
                change_controls_state(tk.DISABLED,
                                      self.__has_max_checkbox,
                                      self.__has_min_checkbox,
                                      self.__max_spinbox,
                                      self.__min_spinbox)
            self.__cmp_label_var.set(trim_string(selected_cmp.name, length=20))

    @staticmethod
    def __extract_values(cmp: Component) -> Tuple[Any, ...]:
        """Extracts the data of the component to show in the taxonomy view.

        :param cmp: Component from which to extract the data.
        :return: Tuple containing data about component
            (has association?, min_, max_?).
        """
        has_association = ''
        min_ = ''
        max_ = ''
        if cmp.association:
            has_association = 'Yes'
            min_ = cmp.association.min_ if cmp.association.min_ is not None else ''
            max_ = cmp.association.max_ if cmp.association.max_ is not None else ''
        return has_association, min_, max_

    def __build_tree(self) -> None:
        """Fills the tree view with components from model."""
        self.__taxonomy_tree.set_items(self.__state.model.taxonomy)

    # Resetable
    def _reset(self) -> None:
        self.__taxonomy_tree.set_items([])
        self.__selected_component = None
        # Set entries to default
        self.__has_association_checkbox_var.set(False)
        self.__has_min_checkbox_var.set(False)
        self.__has_max_checkbox_var.set(False)
        self.__min_spinbox_var.set('')
        self.__max_spinbox_var.set('')
        self.__cmp_label_var.set('')
        # Disable items
        change_controls_state(tk.DISABLED,
                              self.__has_association_checkbox,
                              self.__has_min_checkbox,
                              self.__has_max_checkbox,
                              self.__min_spinbox,
                              self.__max_spinbox)

    def __on_taxonomy_edited(self) -> None:
        """Executed whenever the structure of the taxonomy changes."""
        self._reset()
        self.__build_tree()

    def __on_has_association_changed(self, *_):
        """Executed whenever the __has_association_checkbox is toggled"""
        if self.__selected_component:
            has_association = self.__has_association_checkbox_var.get()
            if has_association:
                if not self.__selected_component.association:
                    self.__selected_component.association = Association()
                change_controls_state(tk.NORMAL,
                                      self.__has_min_checkbox,
                                      self.__has_max_checkbox)
            else:
                self.__has_min_checkbox_var.set(False)  # Reset and block controls
                self.__has_max_checkbox_var.set(False)
                self.__min_spinbox_var.set('')
                self.__max_spinbox_var.set('')
                change_controls_state(tk.DISABLED,
                                      self.__has_max_checkbox,
                                      self.__has_min_checkbox,
                                      self.__max_spinbox,
                                      self.__min_spinbox)
                self.__selected_component.association = None
            self.__taxonomy_tree.update_values(self.__selected_component)

    def __on_has_min_changed(self, *_):
        """Executed whenever the __has_min_checkbox is toggled"""
        if self.__selected_component:
            has_min = self.__has_min_checkbox_var.get()
            if has_min:
                change_controls_state(tk.NORMAL, self.__min_spinbox)
                if self.__selected_component.association and self.__selected_component.association.min_ is not None:
                    self.__min_spinbox_var.set(self.__selected_component.association.min_)
                else:
                    self.__min_spinbox_var.set(0)
                    self.__selected_component.association.min_ = 0
            else:
                if self.__selected_component.association:
                    self.__selected_component.association.min_ = None
                change_controls_state(tk.DISABLED, self.__min_spinbox)
                self.__min_spinbox_var.set('')

    def __on_has_max_changed(self, *_):
        """Executed whenever the __has_max_checkbox_var is toggled"""
        if self.__selected_component:
            has_max = self.__has_max_checkbox_var.get()
            if has_max:
                change_controls_state(tk.NORMAL, self.__max_spinbox)
                if self.__selected_component.association:
                    if self.__selected_component.association.max_ is not None:
                        self.__max_spinbox_var.set(self.__selected_component.association.max_)
                    else:
                        if self.__selected_component.association.min_ is not None:
                            # If component has a minimum association, set the value of Spinbox to it
                            self.__max_spinbox_var.set(self.__selected_component.association.min_)
                        else:
                            # Otherwise set it to 0
                            self.__max_spinbox_var.set(0)
                            self.__selected_component.association.max_ = 0
            else:
                if self.__selected_component.association:
                    self.__selected_component.association.max_ = None
                change_controls_state(tk.DISABLED, self.__max_spinbox)
                self.__max_spinbox_var.set('')

    def __on_min_changed(self, *_):
        """Executed whenever the __min_spinbox_var value changes."""
        if self.__selected_component and self.__selected_component.association:
            # This gets triggered at unpredicted moments (e.g. enabling and disabling widgets
            # so it's necessary to check this condition.
            try:
                min_ = self.__min_spinbox_var.get()
                self.__selected_component.association.min_ = min_
                if self.__selected_component.association.max_ is not None \
                   and self.__selected_component.association.max_ < min_:  # If max < min; set max to min
                    self.__selected_component.association.max_ = min_
                    self.__max_spinbox_var.set(min_)
            except tk.TclError:
                self.__selected_component.association.min_ = None
            finally:
                self.__taxonomy_tree.update_values(self.__selected_component)

    def __on_max_changed(self, *_):
        """Executed whenever the __max_spinbox_var value changes."""
        if self.__selected_component and self.__selected_component.association:
            try:
                max_ = self.__max_spinbox_var.get()
                self.__selected_component.association.max_ = max_
                if self.__selected_component.association.min_ is not None \
                   and self.__selected_component.association.min_ > max_:  # If min > max; set min to max
                    self.__selected_component.association.min_ = max_
                    self.__min_spinbox_var.set(max_)
            except tk.TclError:
                self.__selected_component.association.max_ = None
            finally:
                self.__taxonomy_tree.update_values(self.__selected_component)
