import math
import tkinter as tk
from typing import Optional, Any, Tuple, List
from tkinter import ttk, simpledialog, messagebox

from pubsub import pub

import actions
from exceptions import ResourceError
from model.component import Component
from model.resource import Resource
from view.tree_view_column import Column
from view.hierarchy_tree import HierarchyTree
from view.abstract.has_controller_access import HasControllerAccess
from view.abstract.has_common_setup import HasCommonSetup
from view.abstract.subscribes_to_listeners import SubscribesToListeners
from view.abstract.has_hierarchy_tree import HasHierarchyTree
from view.abstract.tab import Tab
from view.abstract.resetable import Resetable

TAB_NAME = 'Resources'
SELECT_RESOURCE = '(select resource)'


class ResourcesTab(Tab,
                   HasControllerAccess,
                   HasCommonSetup,
                   SubscribesToListeners,
                   HasHierarchyTree,
                   Resetable):
    def __init__(self, parent, parent_notebook, *args, **kwargs):
        Tab.__init__(self, parent_notebook, TAB_NAME, *args, **kwargs)
        HasControllerAccess.__init__(self, parent)

        HasCommonSetup.__init__(self)
        SubscribesToListeners.__init__(self)
        HasHierarchyTree.__init__(self)

        self.__selected_resource: Optional[Resource] = None

    # HasCommonSetup
    def _create_widgets(self):
        self.__left_frame = tk.Frame(self.frame)
        self.__left_top_frame = tk.Frame(self.__left_frame)
        self.__left_mid_frame = tk.Frame(self.__left_frame)
        self.__left_bot_frame = tk.Frame(self.__left_frame)
        # Resources combobox
        self.__resource_combobox_var = tk.StringVar(value=SELECT_RESOURCE)
        self.__resource_combobox_var.trace('w', self.__on_combobox_changed)
        self.__resource_combobox = ttk.Combobox(self.__left_top_frame, state='readonly',
                                                textvariable=self.__resource_combobox_var)
        # C(r)ud Buttons
        self.__add_resource_button = ttk.Button(self.__left_top_frame, text='Add', state=tk.NORMAL,
                                                command=self.__add_resource)
        self.__rename_resource_button = ttk.Button(self.__left_top_frame, text='Rename', state=tk.DISABLED,
                                                   command=self.__rename_resource)
        self.__remove_resource_button = ttk.Button(self.__left_top_frame, text='Remove', state=tk.DISABLED,
                                                   command=self.__remove_resource)
        # Cmp label
        self.__cmp_label_var = tk.StringVar(value='COMPONENT')
        self.__cmp_label = ttk.Label(self.__left_frame, textvariable=self.__cmp_label_var, style='Big.TLabel')
        self.__produces_spinbox_label = ttk.Label(self.__left_mid_frame, text='Produces:')
        self.__produces_spinbox_var = tk.IntVar(value='')
        self.__produces_spinbox_var.trace('w', self.__on_produced_changed)
        self.__produces_spinbox = ttk.Spinbox(self.__left_mid_frame, from_=-math.inf, to=math.inf,
                                              textvariable=self.__produces_spinbox_var)

        self.__all_children_produce_spinbox_label = ttk.Label(self.__left_bot_frame, text='Produces:')
        self.__all_children_produce_spinbox_var = tk.IntVar(value='')
        self.__all_children_produce_spinbox = ttk.Spinbox(self.__left_bot_frame, from_=-math.inf, to=math.inf,
                                                          textvariable=self.__all_children_produce_spinbox_var)
        self.__apply_to_all_children_button = ttk.Button(self.__left_bot_frame, text='Apply to all children',
                                                         command=self.__apply_to_all_children)

    def _setup_layout(self):
        self.__left_frame.grid(row=0, column=0, sticky=tk.NSEW)

        self.__left_top_frame.grid(row=0, column=0, sticky=tk.NSEW)
        self.__resource_combobox.grid(row=0, column=0, columnspan=3, sticky=tk.NSEW)

        self.__add_resource_button.grid(row=1, column=0)
        self.__rename_resource_button.grid(row=1, column=1)
        self.__remove_resource_button.grid(row=1, column=2)

        self.__cmp_label.grid(row=1, column=0)

        self.__left_mid_frame.grid(row=2, column=0, sticky=tk.NSEW)
        self.__produces_spinbox_label.grid(row=0, column=0)
        self.__produces_spinbox.grid(row=0, column=1, columnspan=2)

        self.__left_bot_frame.grid(row=3, column=0, sticky=tk.NSEW)
        self.__all_children_produce_spinbox_label.grid(row=0, column=0)
        self.__all_children_produce_spinbox.grid(row=0, column=1, columnspan=2)
        self.__apply_to_all_children_button.grid(row=1, column=0, columnspan=3)

        self.frame.columnconfigure(0, weight=1, uniform='fred')
        self.frame.columnconfigure(1, weight=2, uniform='fred')
        self.frame.rowconfigure(0, weight=1)

        self.__left_frame.grid_forget()
        self.__left_top_frame.grid_forget()
        self.__cmp_label.grid_forget()
        self.__left_mid_frame.grid_forget()
        self.__left_bot_frame.grid_forget()

    # SubscribesToListeners
    def _subscribe_to_listeners(self):
        pub.subscribe(self._build_tree, actions.HIERARCHY_CREATED)
        pub.subscribe(self._build_tree, actions.HIERARCHY_EDITED)
        pub.subscribe(self._reset, actions.RESET)

    # HasHierarchyTree
    def _on_select_tree_item(self, cmp_id: int) -> None:
        if self.__selected_resource:
            selected_cmp: Component = self.controller.model.get_component_by_id(cmp_id)
            self._selected_component = selected_cmp

            self.__cmp_label.grid(row=1, column=0, columnspan=3)
            self.__cmp_label_var.set(selected_cmp.name)

            if selected_cmp.is_leaf:
                self.__left_bot_frame.grid_forget()
                produced = 0
                if self.__selected_resource.id_ in selected_cmp.produces:
                    produced = selected_cmp.produces[self.__selected_resource.id_]
                self.__produces_spinbox_var.set(produced)
                self.__left_mid_frame.grid(row=2, column=0, sticky=tk.NSEW)
            else:
                self.__left_mid_frame.grid_forget()
                self.__left_bot_frame.grid(row=3, column=0, sticky=tk.NSEW)

    @property
    def _columns(self) -> List[Column]:
        return [Column('produces', 'Produces')]

    def _extract_values(self, cmp: Component) -> Tuple[Any, ...]:
        produces = ''
        if self.__selected_resource:  # TODO: this should be unnecessary
            if self.__selected_resource.id_ in cmp.produces:
                produces = cmp.produces[self.__selected_resource.id_]
        return produces,    # Coma means 1-element tuple

    def _build_tree(self) -> None:
        if self._hierarchy_tree:
            self._destroy_tree()

        self._hierarchy_tree = HierarchyTree(self.frame, self.controller.model.hierarchy, columns=self._columns,
                                             on_select_callback=self._on_select_tree_item,
                                             extract_values=self._extract_values, grid_column=1)

        resources_names = self.controller.model.get_all_resources_names()
        self.__resource_combobox['values'] = sorted(resources_names)

        self.__left_frame.grid(row=0, column=0, sticky=tk.NSEW)  # Show left grid
        self.__left_top_frame.grid(row=0, column=0, sticky=tk.NSEW)  # Show the combobox

    def _destroy_tree(self) -> None:
        self._hierarchy_tree.destroy_()
        self._hierarchy_tree = None

    # Resetable
    def _reset(self) -> None:
        if self._hierarchy_tree:
            self._destroy_tree()

        self._selected_component = None
        self.__selected_resource = None
        # Hide widgets
        self.__left_frame.grid_forget()
        self.__left_top_frame.grid_forget()
        self.__cmp_label.grid_forget()
        self.__left_mid_frame.grid_forget()
        self.__left_bot_frame.grid_forget()
        # Set entries to default
        self.__resource_combobox['values'] = ()
        self.__resource_combobox_var.set(SELECT_RESOURCE)
        self.__produces_spinbox_var.set('')
        self.__all_children_produce_spinbox_var.set('')

    # Class-specific
    def __on_combobox_changed(self, _1, _2, _3):
        if self._hierarchy_tree:
            res_name = self.__resource_combobox_var.get()
            resource = self.controller.model.get_resource_by_name(res_name)
            self.__enable_rename_remove_buttons()
            self.__selected_resource = resource
            self.__update_tree()

    def __update_tree(self):
        leaf_cmps = self.controller.model.get_leaf_components()
        self._hierarchy_tree.update_values(leaf_cmps)

    def __add_resource(self):
        name = simpledialog.askstring('Add resource', f'Enter name of the new resource.')
        if name:
            try:
                resource = self.controller.model.add_resource(name)
                self.__selected_resource = resource
                self.__resource_combobox['values'] = sorted((*self.__resource_combobox['values'], name))
                self.__resource_combobox_var.set(name)
                self.__enable_rename_remove_buttons()
            except ResourceError as e:
                messagebox.showerror('Add resource error.', e.message)

    def __enable_rename_remove_buttons(self):
        self.__rename_resource_button.config(state=tk.NORMAL)
        self.__remove_resource_button.config(state=tk.NORMAL)

    def __disable_rename_remove_buttons(self):
        self.__rename_resource_button.config(state=tk.DISABLED)
        self.__remove_resource_button.config(state=tk.DISABLED)

    def __rename_resource(self):
        if self.__selected_resource:
            new_name = simpledialog.askstring('Rename', f'Enter new name for "{self.__selected_resource.name}" resource.')
            if new_name:
                try:
                    old_name = self.__selected_resource.name
                    self.controller.model.change_resource_name(self.__selected_resource, new_name)
                    updated_combobox_values = [val if val != old_name else new_name for val in
                                               [*self.__resource_combobox['values']]]
                    self.__resource_combobox['values'] = sorted(updated_combobox_values)
                    self.__resource_combobox_var.set(new_name)
                except ResourceError as e:
                    messagebox.showerror('Rename error.', e.message)

    def __remove_resource(self):
        if self.__selected_resource:
            removed_res = self.controller.model.remove_resource(self.__selected_resource)
            updated_combobox_values = [val for val in [*self.__resource_combobox['values']] if val != removed_res.name]
            self.__resource_combobox['values'] = updated_combobox_values
            self.__selected_resource = None
            self.__update_tree()
            self.__resource_combobox_var.set(SELECT_RESOURCE)
            self.__disable_rename_remove_buttons()

            self.__cmp_label.grid_forget()
            self.__left_mid_frame.grid_forget()
            self.__left_bot_frame.grid_forget()

    def __on_produced_changed(self, _1, _2, _3):
        if self._selected_component and self.__selected_resource:
            value = None
            try:
                value = self.__produces_spinbox_var.get()
            except tk.TclError as e:
                print(e)
            finally:
                if value:
                    self._selected_component.produces[self.__selected_resource.id_] = value
                elif self.__selected_resource.id_ in self._selected_component.produces:
                    del self._selected_component.produces[self.__selected_resource.id_]

                self._hierarchy_tree.update_values([self._selected_component])

    def __apply_to_all_children(self):
        if self._selected_component and self.__selected_resource:
            value = None
            try:
                value = self.__all_children_produce_spinbox_var.get()
            except tk.TclError as e:
                print(e)
            finally:
                updated_components = self.controller.model.set_resource_production_to_all_components_children(
                    self._selected_component, self.__selected_resource, value)
                self._hierarchy_tree.update_values(updated_components)
