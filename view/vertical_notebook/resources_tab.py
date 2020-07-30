import math
import tkinter as tk
from typing import Optional, Any, Tuple, List
from tkinter import ttk, simpledialog, messagebox

from pubsub import pub

import actions
from exceptions import BGError
from model.component import Component
from model.resource import Resource
from state import State
from view.scrollbars_listbox import ScrollbarListbox
from view.tree_view_column import Column
from view.abstract.has_common_setup import HasCommonSetup
from view.abstract.subscribes_to_events import SubscribesToEvents
from view.abstract.tab import Tab
from view.abstract.resetable import Resetable
from view.common import change_controls_state, trim_string
from view.style import FONT

TAB_NAME = 'Resources'
SELECT_RESOURCE = '(select resource)'
TREEVIEW_HEADING = 'Component'

CONTROL_PAD_Y = 3

FRAME_PAD_Y = 10
FRAME_PAD_X = 10


class ResourcesTab(Tab,
                   HasCommonSetup,
                   SubscribesToEvents,
                   Resetable):
    def __init__(self, parent_notebook):
        self.__state = State()
        self.__selected_resource: Optional[Resource] = None
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
                                                 columns=[Column('produces', 'Produces')],
                                                 values=self.__state.model.hierarchy,
                                                 )
        self.__left_frame = ttk.Frame(self._frame)
        # Resources combobox
        self.__resource_combobox_var = tk.StringVar(value=SELECT_RESOURCE)
        self.__resource_combobox_var.trace('w', self.__on_combobox_changed)
        self.__resource_combobox = ttk.Combobox(self.__left_frame, state='readonly', font=FONT,
                                                textvariable=self.__resource_combobox_var)
        # Fill the Combobox
        resources_names = self.__state.model.get_all_resources_names()
        self.__resource_combobox['values'] = sorted(resources_names)
        self.__resource_combobox_var.set(SELECT_RESOURCE)
        # C(r)ud Buttons
        self.__add_resource_button = ttk.Button(self.__left_frame, text='Add', state=tk.NORMAL,
                                                command=self.__add_resource)
        self.__rename_resource_button = ttk.Button(self.__left_frame, text='Rename', state=tk.DISABLED,
                                                   command=self.__rename_resource)
        self.__remove_resource_button = ttk.Button(self.__left_frame, text='Remove', state=tk.DISABLED,
                                                   command=self.__remove_resource)
        # Cmp label
        self.__cmp_label_var = tk.StringVar(value='COMPONENT')
        self.__cmp_label = ttk.Label(self.__left_frame, textvariable=self.__cmp_label_var, style='Big.TLabel', anchor=tk.CENTER)
        self.__produces_spinbox_label = ttk.Label(self.__left_frame, text='Produces:')
        self.__produces_spinbox_var = tk.IntVar(value='')
        self.__produces_spinbox_var.trace('w', self.__on_produced_changed)
        self.__produces_spinbox = ttk.Spinbox(self.__left_frame, from_=-math.inf, to=math.inf,
                                              textvariable=self.__produces_spinbox_var)

        self.__all_children_produce_spinbox_label = ttk.Label(self.__left_frame, text='Produces:')
        self.__all_children_produce_spinbox_var = tk.IntVar(value=0)
        self.__all_children_produce_spinbox = ttk.Spinbox(self.__left_frame, from_=-math.inf, to=math.inf,
                                                          textvariable=self.__all_children_produce_spinbox_var)
        self.__apply_to_all_children_button = ttk.Button(self.__left_frame, text='Apply to all children',
                                                         command=self.__apply_to_all_children)

    def _setup_layout(self):
        self.__hierarchy_tree.grid(row=0, column=1, sticky=tk.NSEW)

        self.__left_frame.grid(row=0, column=0, sticky=tk.NSEW, pady=FRAME_PAD_Y, padx=FRAME_PAD_X)

        self.__resource_combobox.grid(row=0, column=0, columnspan=2, sticky=tk.NSEW, pady=CONTROL_PAD_Y)

        self.__add_resource_button.grid(row=1, column=0, columnspan=2, sticky=tk.NSEW, pady=CONTROL_PAD_Y)
        self.__rename_resource_button.grid(row=2, column=0, columnspan=2, sticky=tk.NSEW, pady=CONTROL_PAD_Y)
        self.__remove_resource_button.grid(row=3, column=0, columnspan=2, sticky=tk.NSEW, pady=CONTROL_PAD_Y)

        self.__cmp_label.grid(row=4, column=0, columnspan=2, pady=CONTROL_PAD_Y, sticky=tk.EW)

        self.__produces_spinbox_label.grid(row=5, column=0, pady=CONTROL_PAD_Y, sticky=tk.W)
        self.__produces_spinbox.grid(row=5, column=1, pady=CONTROL_PAD_Y, sticky=tk.NSEW)

        self.__all_children_produce_spinbox_label.grid(row=5, column=0, pady=CONTROL_PAD_Y, sticky=tk.W)
        self.__all_children_produce_spinbox.grid(row=5, column=1, pady=CONTROL_PAD_Y, sticky=tk.NSEW)
        self.__apply_to_all_children_button.grid(row=6, column=0, columnspan=2, sticky=tk.NSEW, pady=CONTROL_PAD_Y)

        self._frame.columnconfigure(0, weight=1, uniform='fred')
        self._frame.columnconfigure(1, weight=3, uniform='fred')
        self._frame.rowconfigure(0, weight=1)

        self.__left_frame.columnconfigure(1, weight=1)

        # Hide widgets
        self.__cmp_label.grid_forget()
        self.__produces_spinbox_label.grid_forget()
        self.__produces_spinbox.grid_forget()
        self.__all_children_produce_spinbox_label.grid_forget()
        self.__all_children_produce_spinbox.grid_forget()
        self.__apply_to_all_children_button.grid_forget()

    # SubscribesToListeners
    def _subscribe_to_events(self):
        pub.subscribe(self.__on_model_loaded, actions.MODEL_LOADED)
        pub.subscribe(self.__build_tree, actions.HIERARCHY_EDITED)
        pub.subscribe(self._reset, actions.RESET)

    # HasHierarchyTree
    def __on_select_tree_item(self, cmp_id: int) -> None:
        if self.__selected_resource:
            selected_cmp: Component = self.__state.model.get_component_by_id(cmp_id)
            self.__selected_component = selected_cmp

            self.__cmp_label.grid(row=4, column=0, columnspan=2, pady=CONTROL_PAD_Y, sticky=tk.EW)
            self.__cmp_label_var.set(trim_string(selected_cmp.name))

            if selected_cmp.is_leaf:
                self.__all_children_produce_spinbox_label.grid_forget()     # Hide widgets (changing all children)
                self.__all_children_produce_spinbox.grid_forget()
                self.__apply_to_all_children_button.grid_forget()
                produced = 0
                if self.__selected_resource.id_ in selected_cmp.produces:
                    produced = selected_cmp.produces[self.__selected_resource.id_]
                self.__produces_spinbox_var.set(produced)
                self.__produces_spinbox_label.grid(row=5, column=0, pady=CONTROL_PAD_Y, sticky=tk.W)
                self.__produces_spinbox.grid(row=5, column=1, pady=CONTROL_PAD_Y, sticky=tk.NSEW)
            else:
                self.__produces_spinbox_label.grid_forget()     # Hide widgets for leaves
                self.__produces_spinbox.grid_forget()
                # Show widgets (changing all children)
                self.__all_children_produce_spinbox_var.set(0)
                self.__all_children_produce_spinbox_label.grid(row=5, column=0, pady=CONTROL_PAD_Y, sticky=tk.W)
                self.__all_children_produce_spinbox.grid(row=5, column=1, pady=CONTROL_PAD_Y, sticky=tk.NSEW)
                self.__apply_to_all_children_button.grid(row=6, column=0, columnspan=2, sticky=tk.NSEW,
                                                         pady=CONTROL_PAD_Y)

    def __extract_values(self, cmp: Component) -> Tuple[Any, ...]:
        produces = ''
        if self.__selected_resource:
            if self.__selected_resource.id_ in cmp.produces:
                produces = cmp.produces[self.__selected_resource.id_]
        return produces,    # Coma means 1-element tuple

    def __build_tree(self) -> None:
        self.__hierarchy_tree.set_items(self.__state.model.hierarchy)

    def __on_model_loaded(self):
        self._reset()
        self.__build_tree()
        resources_names = self.__state.model.get_all_resources_names()
        self.__resource_combobox['values'] = sorted(resources_names)
        self.__resource_combobox_var.set(SELECT_RESOURCE)

    # Resetable
    def _reset(self) -> None:
        self.__selected_component = None
        self.__selected_resource = None
        # Hide widgets
        self.__produces_spinbox_label.grid_forget()
        self.__produces_spinbox.grid_forget()
        self.__all_children_produce_spinbox_label.grid_forget()
        self.__all_children_produce_spinbox.grid_forget()
        self.__apply_to_all_children_button.grid_forget()
        # Set entries to default
        self.__resource_combobox['values'] = ()
        self.__resource_combobox_var.set(SELECT_RESOURCE)
        self.__produces_spinbox_var.set('')
        self.__all_children_produce_spinbox_var.set('')
        # Disable buttons
        change_controls_state(tk.DISABLED,
                              self.__rename_resource_button,
                              self.__remove_resource_button)
        self.__hierarchy_tree.set_items([])

    # Class-specific
    def __on_combobox_changed(self, _1, _2, _3):
        res_name = self.__resource_combobox_var.get()
        resource = self.__state.model.get_resource_by_name(res_name)
        if resource:
            # Enable buttons
            change_controls_state(tk.NORMAL,
                                  self.__rename_resource_button,
                                  self.__remove_resource_button)
            self.__selected_resource = resource
            if self.__selected_component:
                if self.__selected_component.is_leaf:
                    produced = 0
                    if resource.id_ in self.__selected_component.produces:
                        produced = self.__selected_component.produces[self.__selected_resource.id_]
                    self.__produces_spinbox_var.set(produced)
                else:
                    self.__all_children_produce_spinbox_var.set('')

            if self.__hierarchy_tree:
                self.__hierarchy_tree.grid(row=0, column=1, sticky=tk.NSEW)
                self.__update_tree()

    def __update_tree(self):
        leaf_cmps = self.__state.model.get_leaf_components()
        self.__hierarchy_tree.update_values(*leaf_cmps)

    def __add_resource(self):
        name = simpledialog.askstring('Add resource', f'Enter name of the new resource.')
        if name:
            try:
                resource = self.__state.model.add_resource(name)
                self.__selected_resource = resource
                self.__resource_combobox['values'] = sorted((*self.__resource_combobox['values'], name))
                self.__resource_combobox_var.set(name)
                # Enable buttons
                change_controls_state(tk.NORMAL,
                                      self.__rename_resource_button,
                                      self.__remove_resource_button)
            except BGError as e:
                messagebox.showerror('Add resource error.', e.message)

    def __rename_resource(self):
        if self.__selected_resource:
            new_name = simpledialog.askstring('Rename', f'Enter new name for "{self.__selected_resource.name}" resource.')
            if new_name:
                try:
                    old_name = self.__selected_resource.name
                    self.__state.model.change_resource_name(self.__selected_resource, new_name)
                    updated_combobox_values = [val if val != old_name else new_name for val in
                                               [*self.__resource_combobox['values']]]
                    self.__resource_combobox['values'] = sorted(updated_combobox_values)
                    self.__resource_combobox_var.set(new_name)
                except BGError as e:
                    messagebox.showerror('Rename error.', e.message)

    def __remove_resource(self):
        if self.__selected_resource:
            removed_res = self.__state.model.remove_resource(self.__selected_resource)
            updated_combobox_values = [val for val in [*self.__resource_combobox['values']] if val != removed_res.name]
            self.__resource_combobox['values'] = updated_combobox_values
            self.__selected_resource = None

            self.__resource_combobox_var.set(SELECT_RESOURCE)
            # Disable buttons
            change_controls_state(tk.DISABLED,
                                  self.__rename_resource_button,
                                  self.__remove_resource_button)
            # Hide widgets
            self.__cmp_label.grid_forget()
            self.__produces_spinbox_label.grid_forget()
            self.__produces_spinbox.grid_forget()
            self.__all_children_produce_spinbox_label.grid_forget()
            self.__all_children_produce_spinbox.grid_forget()
            self.__apply_to_all_children_button.grid_forget()
            if self.__hierarchy_tree:
                self.__hierarchy_tree.grid_forget()

    def __on_produced_changed(self, _1, _2, _3):
        if self.__selected_component and self.__selected_resource:
            value = None
            try:
                value = self.__produces_spinbox_var.get()
            except tk.TclError as e:
                print(e)
            finally:
                if value:
                    self.__selected_component.produces[self.__selected_resource.id_] = value
                elif self.__selected_resource.id_ in self.__selected_component.produces:
                    del self.__selected_component.produces[self.__selected_resource.id_]

                self.__hierarchy_tree.update_values([self.__selected_component])

    def __apply_to_all_children(self):
        if self.__selected_component and self.__selected_resource:
            value = None
            try:
                value = self.__all_children_produce_spinbox_var.get()
            except tk.TclError as e:
                print(e)
            finally:
                updated_components = self.__state.model.set_resource_production_to_all_components_children(
                    self.__selected_component, self.__selected_resource, value)
                self.__hierarchy_tree.update_values(updated_components)
