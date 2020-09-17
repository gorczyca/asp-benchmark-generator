import copy
import math
from typing import Optional, Callable
import tkinter as tk
from tkinter import ttk, messagebox

from exceptions import BGError
from model import Component, SimpleConstraint
from state import State
from view.scrollbars_listbox import ScrollbarListbox
from view.tree_view_column import Column
from view.abstract import HasCommonSetup, Window
from view.style import FRAME_PAD_X, FRAME_PAD_Y, CONTROL_PAD_Y, FONT


WINDOW_TITLE = 'Simple constraint'
TREEVIEW_HEADING = 'Component'


class SimpleConstraintWindow(HasCommonSetup,
                             Window):
    """Used create/edit SimpleConstraints.

    Attributes:
        __callback: Callback function to be executed after pressing the OK button on this Window.
        __constraint: SimpleConstraint to add / create.
        __components_ids: List of component ids concerned by this constraint.
        __selected_taxonomy_tree_item: Currently selected component in the components taxonomy view.
        __selected_listbox_item: Currently selected component in the selected components listview.
    """
    def __init__(self, parent_frame,
                 callback: Optional[Callable],
                 constraint: Optional[SimpleConstraint] = None):
        self.__state = State()
        self.__callback = callback
        self.__constraint: SimpleConstraint = copy.deepcopy(constraint) if constraint is not None \
            else SimpleConstraint()
        self.__components_ids = [] if constraint is None else [*constraint.components_ids]  # Deep copy of component ids
        self.__selected_taxonomy_tree_item: Optional[Component] = None
        self.__selected_listbox_item: Optional[Component] = None

        Window.__init__(self, parent_frame, WINDOW_TITLE)
        HasCommonSetup.__init__(self)

    # HasCommonSetup
    def _create_widgets(self) -> None:
        self.__taxonomy_tree = ScrollbarListbox(self,
                                                 on_select_callback=self.__on_select_tree_item,
                                                 heading=TREEVIEW_HEADING,
                                                 extract_id=lambda x: x.id_,
                                                 extract_text=lambda x: x.name,
                                                 extract_ancestor=lambda x: '' if x.parent_id is None else x.parent_id,
                                                 values=self.__state.model.taxonomy)

        self.__mid_frame = ttk.Frame(self)
        self.__add_component_button = ttk.Button(self.__mid_frame, text='>>', command=self.__add_to_selected)
        self.__add_components_recursively_button = ttk.Button(self.__mid_frame, text='>> (recursively)',
                                                              command=self.__add_to_selected_recursively)
        self.__remove_component_button = ttk.Button(self.__mid_frame, text='<<', command=self.__remove_from_selected)

        self.__right_frame = ttk.Frame(self)

        self.__components_listbox = ScrollbarListbox(self.__right_frame,
                                                     values=self.__state.model.get_components_by_ids(
                                                         self.__constraint.components_ids),
                                                     extract_id=lambda cmp: cmp.id_,
                                                     extract_text=lambda cmp: cmp.name,
                                                     on_select_callback=self.__on_select_listbox_component,
                                                     columns=[Column('Selected components', main=True, stretch=tk.YES)])

        # Name
        self.__name_entry_var = tk.StringVar(value=self.__constraint.name)
        self.__name_entry_label = ttk.Label(self.__right_frame, text='Name:')
        self.__name_entry = ttk.Entry(self.__right_frame, textvariable=self.__name_entry_var, font=FONT)
        # Description
        self.__description_text_label = ttk.Label(self.__right_frame, text='Description:')
        self.__description_text = tk.Text(self.__right_frame, height=2, font=FONT)
        if self.__constraint.description:
            self.__description_text.insert(tk.INSERT, self.__constraint.description)
        # Distinct checkbox
        self.__distinct_checkbox_var = tk.BooleanVar(value=self.__constraint.distinct)
        self.__distinct_checkbox_label = ttk.Label(self.__right_frame, text='Distinct?')
        self.__distinct_checkbox = ttk.Checkbutton(self.__right_frame, variable=self.__distinct_checkbox_var)
        # Has min checkbox
        self.__has_min_checkbox_var = tk.BooleanVar(value=self.__constraint.min_ is not None)
        self.__has_min_checkbox_var.trace('w', self.__on_has_min_changed)
        self.__has_min_checkbox_label = ttk.Label(self.__right_frame, text='Has min?')
        self.__has_min_checkbox = ttk.Checkbutton(self.__right_frame, variable=self.__has_min_checkbox_var)
        # Min spinbox
        min_var_value = self.__constraint.min_ if self.__constraint.min_ is not None else ''
        self.__min_spinbox_var = tk.IntVar(value=min_var_value)
        self.__min_spinbox_var.trace('w', self.__on_min_changed)
        self.__min_spinbox = ttk.Spinbox(self.__right_frame, from_=0, to=math.inf, textvariable=self.__min_spinbox_var,
                                         state=tk.NORMAL if self.__constraint.min_ is not None else tk.DISABLED)
        # Has max checkbox
        self.__has_max_checkbox_var = tk.BooleanVar(value=self.__constraint.max_ is not None)
        self.__has_max_checkbox_var.trace('w', self.__on_has_max_changed)
        self.__has_max_checkbox_label = ttk.Label(self.__right_frame, text='Has max?')
        self.__has_max_checkbox = ttk.Checkbutton(self.__right_frame, variable=self.__has_max_checkbox_var)
        # Max spinbox
        max_var_value = self.__constraint.max_ if self.__constraint.max_ is not None else ''
        self.__max_spinbox_var = tk.IntVar(value=max_var_value)
        self.__max_spinbox_var.trace('w', self.__on_max_changed)
        self.__max_spinbox = ttk.Spinbox(self.__right_frame, from_=0, to=math.inf, textvariable=self.__max_spinbox_var,
                                         state=tk.NORMAL if self.__constraint.max_ is not None else tk.DISABLED)
        # Buttons frame
        self.__ok_button = ttk.Button(self.__right_frame, text='Ok', command=self.__ok)
        self.__cancel_button = ttk.Button(self.__right_frame, text='Cancel', command=self.destroy)

    def _setup_layout(self) -> None:
        self.__taxonomy_tree.grid(row=0, column=0, sticky=tk.NSEW, pady=FRAME_PAD_Y, padx=FRAME_PAD_X)
        self.__mid_frame.grid(row=0, column=1)
        self.__remove_component_button.grid(row=1, column=0, sticky=tk.NSEW, pady=CONTROL_PAD_Y)
        self.__add_component_button.grid(row=2, column=0, sticky=tk.NSEW, pady=CONTROL_PAD_Y)
        self.__add_components_recursively_button.grid(row=3, column=0, sticky=tk.NSEW, pady=CONTROL_PAD_Y)

        self.__right_frame.grid(row=0, column=2, sticky=tk.NSEW, pady=FRAME_PAD_Y, padx=FRAME_PAD_X)
        self.__name_entry_label.grid(row=0, column=0, sticky=tk.W, pady=CONTROL_PAD_Y)
        self.__name_entry.grid(row=0, column=1, columnspan=3, sticky=tk.NSEW, pady=CONTROL_PAD_Y)
        self.__description_text_label.grid(row=1, column=0, sticky=tk.NW, pady=CONTROL_PAD_Y)
        self.__description_text.grid(row=1, column=1, columnspan=3, sticky=tk.NSEW, pady=CONTROL_PAD_Y)
        self.__distinct_checkbox_label.grid(row=2, column=0, sticky=tk.W, pady=CONTROL_PAD_Y)
        self.__distinct_checkbox.grid(row=2, column=1, columnspan=3, sticky=tk.E, pady=CONTROL_PAD_Y)

        self.__has_min_checkbox_label.grid(row=3, column=0, sticky=tk.W, pady=CONTROL_PAD_Y)
        self.__has_min_checkbox.grid(row=3, column=1, sticky=tk.E, pady=CONTROL_PAD_Y)
        self.__has_max_checkbox_label.grid(row=3, column=2, sticky=tk.W, pady=CONTROL_PAD_Y)
        self.__has_max_checkbox.grid(row=3, column=3, sticky=tk.E, pady=CONTROL_PAD_Y)
        self.__min_spinbox.grid(row=4, column=0, columnspan=2, sticky=tk.NSEW, pady=CONTROL_PAD_Y)
        self.__max_spinbox.grid(row=4, column=2, columnspan=2, sticky=tk.NSEW, pady=CONTROL_PAD_Y)

        self.__components_listbox.grid(row=5, column=0, columnspan=4, sticky=tk.NSEW, pady=CONTROL_PAD_Y)

        self.__ok_button.grid(row=6, column=0, columnspan=2, sticky=tk.EW, pady=CONTROL_PAD_Y)
        self.__cancel_button.grid(row=6, column=2, columnspan=2, sticky=tk.EW, pady=CONTROL_PAD_Y)

        self.__right_frame.rowconfigure(1, weight=1)
        self.__right_frame.rowconfigure(5, weight=2)

        self.__right_frame.columnconfigure(1, weight=1)
        self.__right_frame.columnconfigure(3, weight=1)

        self.columnconfigure(0, weight=1, uniform='fred')
        self.columnconfigure(2, weight=1, uniform='fred')
        self.rowconfigure(0, weight=1)

        self._set_geometry()

    # Taxonomy Treeview
    def __on_select_tree_item(self, cmp_id: int) -> None:
        """Executed whenever a tree item is selected (by mouse click).

        :param cmp_id: Id of the selected component.
        """
        self.__selected_taxonomy_tree_item = self.__state.model.get_component(id_=cmp_id)

    def __on_select_listbox_component(self, cmp_id: int) -> None:
        """Executed whenever a listview item is selected (by mouse click).

        :param cmp_id: Id of the selected component.
        """
        self.__selected_listbox_item = self.__state.model.get_component(id_=cmp_id)

    def __add_to_selected(self):
        """Adds the __selected_taxonomy_tree_item to the list of selected component ids."""
        if self.__selected_taxonomy_tree_item:
            if self.__selected_taxonomy_tree_item.id_ not in self.__components_ids:
                self.__components_ids.append(self.__selected_taxonomy_tree_item.id_)
                self.__components_listbox.add_item(self.__selected_taxonomy_tree_item)
                self.__selected_listbox_item = self.__selected_taxonomy_tree_item
                self.__selected_taxonomy_tree_item = None

    def __add_to_selected_recursively(self):
        """Adds the __selected_taxonomy_tree_item and all its children to the list of selected component ids."""
        if self.__selected_taxonomy_tree_item:
            for c in self.__state.model.get_components_children(self.__selected_taxonomy_tree_item):
                if c.id_ not in self.__components_ids:
                    self.__components_ids.append(c.id_)
                    self.__components_listbox.add_item(c, select_item=False)    # Append children
            self.__components_ids.append(self.__selected_taxonomy_tree_item.id_)
            self.__components_listbox.add_item(self.__selected_taxonomy_tree_item)
            self.__selected_listbox_item = self.__selected_taxonomy_tree_item
            self.__selected_taxonomy_tree_item = None

    def __remove_from_selected(self):
        """Adds the __selected_taxonomy_tree_item to the list of selected component ids."""
        if self.__selected_listbox_item:
            self.__components_ids.remove(self.__selected_listbox_item.id_)
            self.__components_listbox.remove_item_recursively(self.__selected_listbox_item)
            self.__selected_taxonomy_tree_item = self.__selected_listbox_item
            self.__taxonomy_tree.select_item(self.__selected_listbox_item)
            self.__selected_listbox_item = None

    def __on_has_min_changed(self, *_):
        """Executed whenever the __has_min_checkbox is toggled"""
        has_min = self.__has_min_checkbox_var.get()
        if has_min:
            self.__min_spinbox.config(state=tk.ACTIVE)
            self.__min_spinbox_var.set(0)
        else:
            self.__min_spinbox_var.set('')
            self.__min_spinbox.config(state=tk.DISABLED)

    def __on_has_max_changed(self, *_):
        """Executed whenever the __has_max_checkbox is toggled"""
        has_max = self.__has_max_checkbox_var.get()
        if has_max:
            self.__max_spinbox.config(state=tk.ACTIVE)
            has_min = self.__has_min_checkbox_var.get()
            if has_min:
                min_ = self.__min_spinbox_var.get()
                self.__max_spinbox_var.set(min_)
            else:
                self.__max_spinbox_var.set(0)
                self.__constraint.max_ = 0
        else:
            self.__max_spinbox_var.set('')
            self.__max_spinbox.config(state=tk.DISABLED)

    def __on_min_changed(self, *_):
        """Executed whenever the __min_spinbox value changes."""
        try:
            min_ = self.__min_spinbox_var.get()
            has_max = self.__has_max_checkbox_var.get()
            if has_max:
                max_ = self.__max_spinbox_var.get()
                if min_ > max_:
                    self.__max_spinbox_var.set(min_)
        except tk.TclError:
            pass

    def __on_max_changed(self, *_):
        """Executed whenever the __max_spinbox value changes."""
        try:
            max_ = self.__max_spinbox_var.get()
            has_min = self.__has_min_checkbox_var.get()
            if has_min:
                min_ = self.__min_spinbox_var.get()
                if min_ > max_:
                    self.__min_spinbox_var.set(max_)
        except tk.TclError:
            pass

    def __ok(self):
        """Executed whenever the __ok_button is pressed."""
        min_ = None
        max_ = None
        if self.__has_min_checkbox_var.get():   # If component has min
            try:
                min_ = self.__min_spinbox_var.get()
            except tk.TclError:
                min_ = None
        if self.__has_max_checkbox_var.get():   # If component has max
            try:
                max_ = self.__max_spinbox_var.get()
            except tk.TclError:
                max_ = None
        try:
            name = self.__name_entry_var.get()
            # Rewrite values if they are correct
            self.__constraint.name = name
            self.__constraint.description = self.__description_text.get(1.0, tk.END)
            self.__constraint.components_ids = self.__components_ids
            self.__constraint.distinct = self.__distinct_checkbox_var.get()
            self.__constraint.min_ = min_
            self.__constraint.max_ = max_

            #   If this SimpleConstraint is not an independent constraint, but a part of a ComplexConstraint,
            #   name is checked against the names of other SimpleConstraints in the antecedent/consequent
            #   of the ComplexConstraint,
            #   Otherwise, it is checked against all the SimpleConstraint names in model.
            self.__callback(self.__constraint)
            self.grab_release()
            self.destroy()
        except BGError as e:
            messagebox.showerror('Error', e.message, parent=self)

