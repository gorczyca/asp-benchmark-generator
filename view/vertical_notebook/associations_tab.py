import math
import tkinter as tk
from tkinter import ttk
from typing import Optional, Tuple, Any

from pubsub import pub

import actions
from model.component import Component
from model.association import Association
from view.abstract.tab import Tab
from view.hierarchy_tree_column import Column
from view.hierarchy_tree import HierarchyTree
from view.abstract.has_controller_access import HasControllerAccess
from view.abstract.has_common_setup import HasCommonSetup
from view.abstract.subscribes_to_listeners import SubscribesToListeners
from view.abstract.has_treeview import HasTreeView # TODO: rename

TAB_NAME = 'Associations'


class AssociationsTab(Tab, HasControllerAccess, HasCommonSetup, SubscribesToListeners, HasTreeView):
    def __init__(self, parent, parent_notebook, *args, **kwargs):
        Tab.__init__(self, parent_notebook, TAB_NAME, *args, **kwargs)
        HasControllerAccess.__init__(self, parent)

        HasCommonSetup.__init__(self)
        SubscribesToListeners.__init__(self)
        HasTreeView.__init__(self)

        # TODO: move
        self.__hierarchy_tree: Optional[HierarchyTree] = None
        self.__selected_component: Optional[Component] = None

    def _create_widgets(self):
        self.__right_frame = tk.Frame(self.frame)
        # Cmp label
        self.__cmp_label_var = tk.StringVar(value='COMPONENT')
        self.__cmp_label = ttk.Label(self.__right_frame, textvariable=self.__cmp_label_var, style='Big.TLabel')
        # Has association checkbox
        self.__has_association_checkbox_var = tk.BooleanVar(value=False)
        self.__has_association_checkbox_var.trace('w', self.__on_has_association_changed)
        self.__has_association_checkbox_label = ttk.Label(self.__right_frame, text='Has association?')
        self.__has_association_checkbox = ttk.Checkbutton(self.__right_frame,
                                                          variable=self.__has_association_checkbox_var)
        # Has min checkbox
        self.__has_min_checkbox_var = tk.BooleanVar(value=False)
        self.__has_min_checkbox_var.trace('w', self.__on_has_min_changed)
        self.__has_min_checkbox_label = ttk.Label(self.__right_frame, text='Has min?')
        self.__has_min_checkbox = ttk.Checkbutton(self.__right_frame, state=tk.DISABLED,
                                                  variable=self.__has_min_checkbox_var)

        self.__min_spinbox_var = tk.IntVar(value='')
        self.__min_spinbox_var.trace('w', self.__on_min_changed)
        self.__min_spinbox = ttk.Spinbox(self.__right_frame, from_=0, to=math.inf, state=tk.DISABLED,
                                         textvariable=self.__min_spinbox_var)
        # Has max checkbox
        self.__has_max_checkbox_var = tk.BooleanVar(value=False)
        self.__has_max_checkbox_var.trace('w', self.__on_has_max_changed)
        self.__has_max_checkbox_label = ttk.Label(self.__right_frame, text='Has max?')
        self.__has_max_checkbox = ttk.Checkbutton(self.__right_frame, state=tk.DISABLED,
                                                  variable=self.__has_max_checkbox_var)

        self.__max_spinbox_var = tk.IntVar(value='')
        self.__max_spinbox_var.trace('w', self.__on_max_changed)
        self.__max_spinbox = ttk.Spinbox(self.__right_frame, from_=0, to=math.inf, state=tk.DISABLED,
                                         textvariable=self.__max_spinbox_var)

    def _setup_layout(self):
        self.__right_frame.grid(row=0, column=1, sticky=tk.NSEW)
        self.__cmp_label.grid(row=0, column=0, columnspan=4)
        self.__has_association_checkbox_label.grid(row=1, column=0, columnspan=2, sticky=tk.W)
        self.__has_association_checkbox.grid(row=1, column=2, columnspan=2, sticky=tk.W)
        self.__has_min_checkbox_label.grid(row=2, column=0, sticky=tk.W)
        self.__has_min_checkbox.grid(row=2, column=1, sticky=tk.E)
        self.__has_max_checkbox_label.grid(row=2, column=2, sticky=tk.W)
        self.__has_max_checkbox.grid(row=2, column=3, sticky=tk.E)
        self.__min_spinbox.grid(row=3, column=0, columnspan=2)
        self.__max_spinbox.grid(row=3, column=2, columnspan=2)

        self.frame.columnconfigure(0, weight=2, uniform='fred')
        self.frame.columnconfigure(1, weight=1, uniform='fred')
        self.frame.rowconfigure(0, weight=1)

        self.__right_frame.grid_forget()

    def _subscribe_to_listeners(self):
        pub.subscribe(self.__build_tree, actions.HIERARCHY_CREATED)
        pub.subscribe(self.__build_tree, actions.HIERARCHY_EDITED)
        pub.subscribe(self.__reset, actions.RESET)

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
        has_association = self.__has_association_checkbox_var.get()
        if has_association:
            if not self.__selected_component.association:
                self.__selected_component.association = Association()
            self.__has_min_checkbox.config(state=tk.NORMAL)
            self.__has_max_checkbox.config(state=tk.NORMAL)
        else:
            self.__disable_widgets()
            self.__selected_component.association = None
        self.__hierarchy_tree.update_values([self.__selected_component])

    def __on_has_min_changed(self, _1, _2, _3):
        has_min = self.__has_min_checkbox_var.get()
        if has_min:
            self.__min_spinbox.config(state=tk.ACTIVE)
            if self.__selected_component.association and self.__selected_component.association.min_:
                self.__min_spinbox_var.set(self.__selected_component.association.min_)
            else:
                self.__min_spinbox_var.set(0)
        else:
            self.__min_spinbox_var.set('')
            self.__min_spinbox.config(state=tk.DISABLED)

    def __on_has_max_changed(self, _1, _2, _3):
        has_max = self.__has_max_checkbox_var.get()
        if has_max:
            self.__max_spinbox.config(state=tk.ACTIVE)
            if self.__selected_component.association.max_:
                self.__max_spinbox_var.set(self.__selected_component.association.max_)
            else:
                if self.__selected_component.association.min_:
                    # If component has a minimum association, set the value of Spinbox to it
                    self.__max_spinbox_var.set(self.__selected_component.association.min_)
                else:
                    # Otherwise set it to 0
                    self.__max_spinbox_var.set(0)
        else:
            self.__max_spinbox_var.set('')
            self.__max_spinbox.config(state=tk.DISABLED)

    def __on_min_changed(self, _1, _2, _3):
        if self.__selected_component.association:
            # This gets triggered at unpredicted moments (e.g. enabling and disabling widgets
            # so it's necessary to check this condition.
            try:
                min_ = self.__min_spinbox_var.get()
                self.__selected_component.association.min_ = min_
                if self.__selected_component.association.max_ \
                   and self.__selected_component.association.max_ < min_:  # If max < min; set max to min
                    self.__selected_component.association.max_ = min_
                    self.__max_spinbox_var.set(min_)
            except tk.TclError as e:
                print(e)
                self.__selected_component.association.min_ = ''
            finally:
                self.__hierarchy_tree.update_values([self.__selected_component])

    def __on_max_changed(self, _1, _2, _3):
        if self.__selected_component.association:
            try:
                max_ = self.__max_spinbox_var.get()
                self.__selected_component.association.max_ = max_
                if self.__selected_component.association.min_ \
                   and self.__selected_component.association.min_ > max_:  # If min > max; set min to max
                    self.__selected_component.association.min_ = max_
                    self.__min_spinbox_var.set(max_)
            except tk.TclError as e:
                print(e)
                self.__selected_component.association.max_ = ''
            finally:
                self.__hierarchy_tree.update_values([self.__selected_component])

    def __build_tree(self):
        columns = [
            Column('has_association', 'Has association?'),
            Column('min', 'Min'),
            Column('max', 'Max')]

        if self.__hierarchy_tree:
            self.__hierarchy_tree.destroy_()

        self.__hierarchy_tree = HierarchyTree(self.frame, self.controller.model.hierarchy, columns=columns,
                                              on_select_callback=self.__on_select,
                                              extract_values=AssociationsTab.__extract_values)

    @staticmethod
    def __extract_values(cmp: Component) -> Tuple[str, Any, Any]:
        """This static method is necessary because at the time of writing this None-aware operators such as (?., ??) are not
        supported.
        """
        has_association = ''
        min_ = ''
        max_ = ''
        if cmp.association:
            has_association = 'Yes'
            min_ = cmp.association.min_ if cmp.association.min_ is not None else ''
            max_ = cmp.association.max_ if cmp.association.max_ is not None else ''
        return has_association, min_, max_

    def __on_select(self, cmp_id: int):
        selected_cmp: Component = self.controller.model.get_component_by_id(cmp_id)
        self.__selected_component = selected_cmp

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
        self.__right_frame.grid(row=0, column=1, sticky=tk.NSEW)

    def __reset(self):
        if self.__hierarchy_tree:
            self.__hierarchy_tree.destroy_()
            self.__hierarchy_tree = None
            self.__right_frame.grid_forget()
