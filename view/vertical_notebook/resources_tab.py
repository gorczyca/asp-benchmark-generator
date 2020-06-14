from typing import Optional, Tuple, Any
import tkinter as tk
from tkinter import ttk

from pubsub import pub

import actions
from model.component import Component
from model.resource import Resource
from view.hierarchy_tree_column import Column
from view.hierarchy_tree import HierarchyTree
from view.vertical_notebook.vertical_notebook_tab import VerticalNotebookTab
from view.c_frame import CFrame

TAB_NAME = 'Resources'
SELECT_RESOURCE = '(select resource)'


class ResourcesTab(VerticalNotebookTab, CFrame):
    def __init__(self, parent, parent_notebook, *args, **kwargs):
        VerticalNotebookTab.__init__(self, parent_notebook, TAB_NAME, *args, **kwargs)
        CFrame.__init__(self, parent, parent_notebook)

        self.__hierarchy_tree: Optional[HierarchyTree] = None
        self.__selected_component: Optional[Component] = None
        self.__selected_resource: Optional[Resource] = None

    def _create_widgets(self):
        self.__right_frame = tk.Frame(self.frame)
        self.__right_top_frame = tk.Frame(self.__right_frame)
        self.__right_mid_frame = tk.Frame(self.__right_frame)
        self.__right_bot_frame = tk.Frame(self.__right_frame)
        # Resources Combobox
        self.__resource_combobox_var = tk.StringVar(value=SELECT_RESOURCE)
        self.__resource_combobox = ttk.Combobox(self.__right_top_frame,
                                                textvariable=self.__resource_combobox_var)
        self.__resource_combobox.grid(row=0, column=0)
        # Cmp label
        self.__cmp_label_var = tk.StringVar(value='COMPONENT')
        self.__cmp_label = ttk.Label(self.__right_mid_frame, textvariable=self.__cmp_label_var, style='Big.TLabel')

    def _setup_layout(self):
        self.__right_frame.grid(row=0, column=1, sticky=tk.NSEW)
        self.__cmp_label.grid(row=0, column=0, columnspan=4)

        self.__right_top_frame.grid(row=0, column=0, sticky=tk.NSEW)
        self.__right_mid_frame.grid(row=1, column=0, sticky=tk.NSEW)
        self.__right_bot_frame.grid(row=2, column=0, sticky=tk.NSEW)

        self.frame.columnconfigure(0, weight=2, uniform='fred')
        self.frame.columnconfigure(1, weight=1, uniform='fred')
        self.frame.rowconfigure(0, weight=1)

        self.__right_frame.grid_forget()
        self.__right_top_frame.grid_forget()
        self.__right_mid_frame.grid_forget()
        self.__right_bot_frame.grid_forget()

    def _subscribe_to_listeners(self):
        pub.subscribe(self.__build_tree, actions.HIERARCHY_CREATED)
        pub.subscribe(self.__build_tree, actions.HIERARCHY_EDITED)
        pub.subscribe(self.__reset, actions.RESET)

    def __build_tree(self):     # TODO: consider taking it out to some abstract class (this, reset, on_select etc)
        # TODO: take it out to class property
        columns = [
            Column('produces', 'Produces')
        ]

        if self.__hierarchy_tree:
            self.__hierarchy_tree.destroy()

        self.__hierarchy_tree = HierarchyTree(self.frame, self.controller.model.hierarchy, columns=columns,
                                              on_select_callback=self.__on_select,
                                              extract_values=self.__extract_values)

        resources_names = self.controller.model.get_all_resources_names()
        self.__resource_combobox['values'] = resources_names

        self.__right_frame.grid(row=0, column=1, sticky=tk.NSEW)    # Show right grid
        self.__right_top_frame.grid(row=0, column=0, sticky=tk.NSEW)    # Show the combobox

    def __add_resource(self):
        pass # TODO: from here

    def __extract_values(self, cmp: Component) -> Any:
        produces = ''
        if self.__selected_resource:    # TODO: this should be unnecessary
            if self.__selected_resource.id_ in cmp.produces:
                produces = cmp.produces[self.__selected_resource.id_]
        return produces

    def __on_select(self, cmp_id: int):
        selected_cmp: Component = self.controller.model.get_component_by_id(cmp_id)
        self.__selected_component = selected_cmp

        # Insert logic here

        self.__cmp_label_var.set(selected_cmp.name)

    def __reset(self):
        if self.__hierarchy_tree:
            self.__hierarchy_tree.destroy_()
            self.__hierarchy_tree = None
            self.__right_frame.grid_forget()

