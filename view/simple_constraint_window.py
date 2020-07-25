import math
from typing import Tuple, Any, List, Optional
import tkinter as tk
from tkinter import ttk, messagebox

from model.component import Component
from model.simple_constraint import SimpleConstraint
from state import State
from view.abstract.has_common_setup import HasCommonSetup
from view.abstract.has_hierarchy_tree import HasHierarchyTree
from view.abstract.window import Window
from view.hierarchy_tree import HierarchyTree
from view.scrollbars_listbox import ScrollbarListbox
from view.tree_view_column import Column
from view.style import FRAME_PAD_X, FRAME_PAD_Y, CONTROL_PAD_Y, FONT


WINDOW_TITLE = 'Simple constraint'


class SimpleConstraintWindow(HasCommonSetup,
                             HasHierarchyTree,  # TODO: remove this interface
                             Window):
    def __init__(self, parent_frame, callback, constraint: Optional[SimpleConstraint] = None,
                 check_name_with: List[str] = None):
        self.__constraint: SimpleConstraint = constraint if constraint is not None \
            else SimpleConstraint()
        self.__components_ids = [] if constraint is None else [*constraint.components_ids]  # Deep copy of component ids
        self.__selected_hierarchy_tree_item: Optional[Component] = None
        self.__selected_listbox_item: Optional[Component] = None
        self.__check_name_with: List[str] = check_name_with if check_name_with is not None else []

        self.__state = State()
        self.__callback = callback

        Window.__init__(self, parent_frame, WINDOW_TITLE)
        HasCommonSetup.__init__(self)

    # HasCommonSetup
    def _create_widgets(self) -> None:
        self._build_tree()

        self.__mid_frame = ttk.Frame(self._window)
        self.__add_component_button = ttk.Button(self.__mid_frame, text='>>', command=self.__add_to_selected)
        self.__add_components_recursively_button = ttk.Button(self.__mid_frame, text='>> (recursively)',
                                                              command=self.__add_to_selected_recursively)
        self.__remove_component_button = ttk.Button(self.__mid_frame, text='<<', command=self.__remove_from_selected)

        self.__right_frame = ttk.Frame(self._window)
        # self.__constraints_data_frame = ttk.Frame(self.__right_frame)
        # TODO: move grid_row to a separate function and invoke it in setup_layout
        self.__components_listbox = ScrollbarListbox(self.__right_frame,
                                                     values=self.__state.model.get_components_by_ids(
                                                         self.__constraint.components_ids),
                                                     extract_id=lambda cmp: cmp.id_,
                                                     extract_text=lambda cmp: cmp.name,
                                                     on_select_callback=self.__on_select_listbox_component,
                                                     columns=[Column('#0', 'Selected components', stretch=tk.YES)])

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
        self.__min_spinbox = ttk.Spinbox(self.__right_frame, from_=0, to=math.inf, state=tk.DISABLED,
                                         textvariable=self.__min_spinbox_var)
        # Has max checkbox
        self.__has_max_checkbox_var = tk.BooleanVar(value=self.__constraint.max_ is not None)
        self.__has_max_checkbox_var.trace('w', self.__on_has_max_changed)
        self.__has_max_checkbox_label = ttk.Label(self.__right_frame, text='Has max?')
        self.__has_max_checkbox = ttk.Checkbutton(self.__right_frame, variable=self.__has_max_checkbox_var)
        # Max spinbox
        max_var_value = self.__constraint.max_ if self.__constraint.max_ is not None else ''
        self.__max_spinbox_var = tk.IntVar(value=max_var_value)
        self.__max_spinbox_var.trace('w', self.__on_max_changed)
        self.__max_spinbox = ttk.Spinbox(self.__right_frame, from_=0, to=math.inf, state=tk.DISABLED,
                                         textvariable=self.__max_spinbox_var)
        # Buttons frame
        self.__ok_button = ttk.Button(self.__right_frame, text='Ok', command=self.__ok)
        self.__cancel_button = ttk.Button(self.__right_frame, text='Cancel', command=self._window.destroy)

    def _setup_layout(self) -> None:
        self._hierarchy_tree.grid(row=0, column=0, sticky=tk.NSEW, pady=FRAME_PAD_Y, padx=FRAME_PAD_X)
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

        self._window.columnconfigure(0, weight=1, uniform='fred')
        self._window.columnconfigure(2, weight=1, uniform='fred')
        self._window.rowconfigure(0, weight=1)

        self._set_geometry()

    def _on_select_tree_item(self, cmp_id: int) -> None:
        self.__selected_hierarchy_tree_item = self.__state.model.get_component_by_id(cmp_id)

    @property
    def _columns(self) -> List[Column]:
        return []

    def _extract_values(self, cmp: Component) -> Tuple[Any, ...]:
        pass

    def _build_tree(self) -> None:
        self._hierarchy_tree = HierarchyTree(self._window, self.__state.model.hierarchy,
                                             on_select_callback=self._on_select_tree_item)

    def _destroy_tree(self) -> None:
        pass

    def __on_select_listbox_component(self, id_: int) -> None:
        self.__selected_listbox_item = self.__state.model.get_component_by_id(id_)

    def __add_to_selected(self):
        if self.__selected_hierarchy_tree_item:
            if self.__selected_hierarchy_tree_item.id_ not in self.__components_ids:
                self.__components_ids.append(self.__selected_hierarchy_tree_item.id_)
                self.__components_listbox.add_item(self.__selected_hierarchy_tree_item)

    def __add_to_selected_recursively(self):
        if self.__selected_hierarchy_tree_item:
            component_and_children = self.__state.model.get_component_and_its_children(
                self.__selected_hierarchy_tree_item)
            for c in component_and_children:
                if c.id_ not in self.__components_ids:
                    self.__components_ids.append(c.id_)
                    self.__components_listbox.add_item(c)

    def __remove_from_selected(self):
        if self.__selected_listbox_item:
            self.__components_ids.remove(self.__selected_listbox_item.id_)
            self.__components_listbox.remove_item(self.__selected_listbox_item)
            self.__selected_listbox_item = None

    def __on_has_min_changed(self, _1, _2, _3):
        has_min = self.__has_min_checkbox_var.get()
        if has_min:
            self.__min_spinbox.config(state=tk.ACTIVE)
            self.__min_spinbox_var.set(0)
            # self.__constraint.min_ = 0
        else:
            self.__min_spinbox_var.set('')
            self.__min_spinbox.config(state=tk.DISABLED)
            # self.__constraint.min_ = None

    def __on_has_max_changed(self, _1, _2, _3):
        has_max = self.__has_max_checkbox_var.get()
        if has_max:
            self.__max_spinbox.config(state=tk.ACTIVE)
            has_min = self.__has_min_checkbox_var.get()
            if has_min:
                min_ = self.__min_spinbox_var.get()
                self.__max_spinbox_var.set(min_)
                # self.__constraint.max_ = min_
            else:
                self.__max_spinbox_var.set(0)
                self.__constraint.max_ = 0
        else:
            self.__max_spinbox_var.set('')
            self.__max_spinbox.config(state=tk.DISABLED)
            # self.__constraint.max_ = None

    def __on_min_changed(self, _1, _2, _3):
        try:
            min_ = self.__min_spinbox_var.get()
            # self.__constraint.min_ = min_
            has_max = self.__has_max_checkbox_var.get()
            if has_max:
                max_ = self.__max_spinbox_var.get()
                if min_ > max_:
                    self.__max_spinbox_var.set(min_)
                    # self.__constraint.max_ = min_
        except tk.TclError as e:
            print(e)
            # self.__constraint.min_ = None

    def __on_max_changed(self, _1, _2, _3):
        try:
            max_ = self.__max_spinbox_var.get()
            # self.__constraint.max = max_
            has_min = self.__has_min_checkbox_var.get()
            if has_min:
                min_ = self.__min_spinbox_var.get()
                if min_ > max_:
                    self.__min_spinbox_var.set(max_)
                    # self.__constraint.min_ = max_
        except tk.TclError as e:
            print(e)
            # self.__constraint.max_ = None

    def __ok(self):
        # Update constraint values
        name = self.__name_entry_var.get()
        if name in self.__check_name_with:
            messagebox.showerror('Add constraint error.', f'Constraint {name} already exists.')
            return
        self.__constraint.name = name
        self.__constraint.description = self.__description_text.get(1.0, tk.END)
        self.__constraint.components_ids = self.__components_ids
        # self.__constraint.contains = self.__contains_var.get()
        self.__constraint.distinct = self.__distinct_checkbox_var.get()

        if self.__has_min_checkbox_var.get():   # If component has min
            try:
                min_ = self.__min_spinbox_var.get()
                self.__constraint.min_ = min_
            except tk.TclError as e:
                print(e)
                self.__constraint.min_ = None
        if self.__has_max_checkbox_var.get():   # If component has max
            try:
                max_ = self.__max_spinbox_var.get()
                self.__constraint.max_ = max_
            except tk.TclError as e:
                print(e)
                self.__constraint.max_ = None
        self.__callback(self.__constraint)
        self._window.destroy()
