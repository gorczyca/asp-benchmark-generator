from typing import Optional, Any, Tuple, List
import tkinter as tk
from tkinter import ttk

from pubsub import pub

import actions
from model.component import Component
from model.resource import Resource
from view.hierarchy_tree_column import Column
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

    # SubscribesToListeners
    def _subscribe_to_listeners(self):
        pub.subscribe(self._build_tree, actions.HIERARCHY_CREATED)
        pub.subscribe(self._build_tree, actions.HIERARCHY_EDITED)
        pub.subscribe(self._reset, actions.RESET)

    # HasHierarchyTree
    def _on_select_tree_item(self, cmp_id: int) -> None:
        selected_cmp: Component = self.controller.model.get_component_by_id(cmp_id)
        self._selected_component = selected_cmp

        # Insert logic here

        self.__cmp_label_var.set(selected_cmp.name)

    @property
    def _columns(self) -> List[Column]:
        return [ Column('produces', 'Produces') ]

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
                                             extract_values=self._extract_values)

        resources_names = self.controller.model.get_all_resources_names()
        self.__resource_combobox['values'] = resources_names

        self.__right_frame.grid(row=0, column=1, sticky=tk.NSEW)  # Show right grid
        self.__right_top_frame.grid(row=0, column=0, sticky=tk.NSEW)  # Show the combobox

    def _destroy_tree(self) -> None:
        self._hierarchy_tree.destroy_()
        self._hierarchy_tree = None

    # Resetable
    def _reset(self) -> None:
        if self._hierarchy_tree:
            self._destroy_tree()
        self.__right_frame.grid_forget()

    # Class-specific
    def __add_resource(self):
        pass    # TODO: from here

