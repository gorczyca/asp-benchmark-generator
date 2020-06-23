from typing import Tuple, Any, List, Optional
import tkinter as tk
from tkinter import ttk

from model.component import Component
from view.abstract.base_frame import BaseFrame
from view.abstract.has_common_setup import HasCommonSetup
from view.abstract.has_controller_access import HasControllerAccess
from view.abstract.has_hierarchy_tree import HasHierarchyTree
from view.hierarchy_tree import HierarchyTree
from view.scrollbars_listbox import ScrollbarListbox
from view.tree_view_column import Column

SELECT_COMPONENTS_WINDOW_NAME = 'Select components'
SELECT_COMPONENTS_WINDOW_SIZE = '1080x720'
LABEL_INFO = 'If selected component from hierarchy on the left is not a leaf component, all of their leaf children' \
             'components will be added'


class SelectComponentsWindow(BaseFrame,
                             HasControllerAccess,
                             HasCommonSetup,
                             HasHierarchyTree):
    def __init__(self, parent, parent_frame, hierarchy, callback, select_leaf_components_only=False):
        BaseFrame.__init__(self, parent_frame)
        HasControllerAccess.__init__(self, parent)

        self.__hierarchy = hierarchy
        self.__select_leaf_components_only = select_leaf_components_only
        self.__callback = callback

        self.__selected_hierarchy_tree_item: Optional[Component] = None
        self.__selected_listbox_item: Optional[Component] = None

        HasCommonSetup.__init__(self)

    # HasCommonSetup
    def _create_widgets(self) -> None:
        self.__window = tk.Toplevel(self.parent_frame)
        self.__window.grab_set()
        self.__window.title(SELECT_COMPONENTS_WINDOW_NAME)
        self.__window.geometry(SELECT_COMPONENTS_WINDOW_SIZE)

        self._build_tree()

        self.__mid_frame = tk.Frame(self.__window)
        # if self.__select_leaf_components_only:
        #     self.__info_label = ttk.Label(self.__mid_frame, text=LABEL_INFO, wraplength=200, borderwidth=2,
        #                                   relief="groove", anchor=tk.W, justify=tk.LEFT).grid(row=0, column=0)
        self.__add_component_button = ttk.Button(self.__mid_frame, text='>>', command=self.__add_to_selected)
        self.__remove_component_button = ttk.Button(self.__mid_frame, text='<<', command=self.__remove_from_selected)

        self.__right_frame = tk.Frame(self.__window)
        self.__selected_components_label = ttk.Label(self.__right_frame, text='Selected components:', style='Big.TLabel')
        self.__components_listbox = ScrollbarListbox(self.__right_frame,  grid_row=1,
                                                     on_select_callback=self.__on_select_listbox_component,
                                                     columns=[Column('#0', 'Component', stretch=tk.YES)])

    def _setup_layout(self) -> None:
        self.__mid_frame.grid(row=0, column=1)
        self.__add_component_button.grid(row=1, column=0)
        self.__remove_component_button.grid(row=2, column=0)

        self.__right_frame.grid(row=0, column=2, sticky=tk.NSEW)
        self.__selected_components_label.grid(row=0, column=0)

        self.__right_frame.grid_columnconfigure(0, weight=1)
        self.__right_frame.grid_rowconfigure(1, weight=1)

        self.__window.rowconfigure(0, weight=1)
        self.__window.columnconfigure(0, weight=2, uniform='fred')
        self.__window.columnconfigure(1, weight=1, uniform='fred')
        self.__window.columnconfigure(2, weight=2, uniform='fred')

    def _on_select_tree_item(self, cmp_id: int) -> None:
        self.__selected_hierarchy_tree_item = self.controller.model.get_component_by_id(cmp_id)

    @property
    def _columns(self) -> List[Column]:
        return []

    def _extract_values(self, cmp: Component) -> Tuple[Any, ...]:
        pass

    def _build_tree(self) -> None:
        self._hierarchy_tree = HierarchyTree(self.__window, self.__hierarchy,
                                             on_select_callback=self._on_select_tree_item)

    def _destroy_tree(self) -> None:
        pass

    def __on_select_listbox_component(self, id_: int) -> None:
        self.__selected_listbox_item = self.controller.model.get_component_by_id(id_)

    def __add_to_selected(self):
        if self.__selected_hierarchy_tree_item:
            # TODO: check if leaf or not
            self.__components_listbox.add_item(self.__selected_hierarchy_tree_item)

    def __remove_from_selected(self):
        if self.__selected_listbox_item:
            # TODO: check if leaf or not
            self.__components_listbox.remove_item(self.__selected_listbox_item)
