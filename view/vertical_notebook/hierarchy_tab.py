import tkinter as tk
from tkinter import messagebox, simpledialog
from tkinter import ttk
from typing import List, Tuple, Any

from pubsub import pub

import actions
from exceptions import HierarchyStringError
from model.component import Component
from view.abstract.has_hierarchy_tree import HasHierarchyTree
from view.abstract.has_common_setup import HasCommonSetup
from view.abstract.subscribes_to_listeners import SubscribesToListeners
from view.abstract.has_controller_access import HasControllerAccess
from view.abstract.resetable import Resetable
from view.abstract.tab import Tab
from view.hierarchy_tree import HierarchyTree
from view.hierarchy_tree_column import Column
from view.vertical_notebook.create_hierarchy_window import CreateHierarchyWindow

TAB_NAME = 'Hierarchy'

COL_ID_SYMMETRY_BREAKING = 'symmetry_breaking'
COL_ID_COUNT = 'count'
COL_NAME_SYMMETRY_BREAKING = 'Symmetry breaking?'
COL_NAME_COUNT = 'Count'

BUTTONS_PAD_X = 30
BUTTONS_PAD_Y = 3
LABEL_PAD_X = 40
LABEL_PAD_Y = 10


class HierarchyTab(Tab,
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

    # HasCommonSetup
    def _create_widgets(self):
        self.__right_frame = tk.Frame(self.frame)

        self.__cmp_name_var = tk.StringVar()
        self.__cmp_name_var.set('COMPONENT')
        self.__cmp_name_label = ttk.Label(self.__right_frame, anchor=tk.CENTER, textvariable=self.__cmp_name_var,
                                          style='Big.TLabel')
        self.__rename_button = ttk.Button(self.__right_frame, text='Rename', command=self.__rename)
        self.__add_sibling_button = ttk.Button(self.__right_frame, text='Add sibling', command=self.__add_sibling)
        self.__add_child_button = ttk.Button(self.__right_frame, text='Add child', command=self.__add_child)
        self.__remove_button = ttk.Button(self.__right_frame, text='Remove', command=self.__remove)
        self.__remove_recursively_button = ttk.Button(self.__right_frame, text='Remove recursively',
                                                      command=self.__remove_recursively)
        self.__create_hierarchy_button = ttk.Button(self.frame, text="Create hierarchy",
                                                    command=self.__create_hierarchy, width=14)

    def _setup_layout(self):
        self.frame.rowconfigure(0, weight=1)
        self.frame.columnconfigure(0, weight=2, uniform='fred')
        self.frame.columnconfigure(1, weight=1, uniform='fred')

        self.__right_frame.columnconfigure(0, weight=1)

        self.__cmp_name_label.grid(row=0, sticky=tk.NSEW, padx=LABEL_PAD_X, pady=LABEL_PAD_Y)
        self.__rename_button.grid(row=1, sticky=tk.NSEW, padx=BUTTONS_PAD_X, pady=BUTTONS_PAD_Y)
        self.__add_sibling_button.grid(row=2, sticky=tk.NSEW, padx=BUTTONS_PAD_X, pady=BUTTONS_PAD_Y)
        self.__add_child_button.grid(row=3, sticky=tk.NSEW, padx=BUTTONS_PAD_X, pady=BUTTONS_PAD_Y)
        self.__remove_button.grid(row=4, sticky=tk.NSEW, padx=BUTTONS_PAD_X, pady=BUTTONS_PAD_Y)
        self.__remove_recursively_button.grid(row=5, sticky=tk.NSEW, padx=BUTTONS_PAD_X, pady=BUTTONS_PAD_Y)

        self.__create_hierarchy_button.grid(row=1, column=0, padx=30, pady=5)

    # SubscribesToListeners
    def _subscribe_to_listeners(self):
        pub.subscribe(self._reset, actions.RESET)
        pub.subscribe(self._build_tree, actions.HIERARCHY_CREATED)

    # HasHierarchyTree
    def _on_select_tree_item(self, cmp_id: int) -> None:
        selected_component: Component = self.controller.model.get_component_by_id(cmp_id)
        self._selected_component = selected_component
        self.__cmp_name_var.set(selected_component.name)
        self.__right_frame.grid(row=0, column=1, sticky=tk.NSEW)

    @property
    def _columns(self) -> List[Column]:
        return []    # TODO: will this work?

    def _extract_values(self, cmp: Component) -> Tuple[Any, ...]:
        pass    # TODO: will this work?

    def _build_tree(self) -> None:
        if self._hierarchy_tree:
            self._hierarchy_tree.destroy_()
        self._hierarchy_tree = HierarchyTree(self.frame, self.controller.model.hierarchy,
                                             on_select_callback=self._on_select_tree_item)

    def _destroy_tree(self) -> None:
        self._hierarchy_tree.destroy_()
        self._hierarchy_tree = None

    # Resetable
    def _reset(self) -> None:
        if self._hierarchy_tree:
            self._destroy_tree()
        self.__right_frame.grid_forget()

    # Class-specific
    def __add_sibling(self) -> None:
        sibling_name = simpledialog.askstring('Add sibling', f'Enter name of sibling of the "'
                                                             f'{self._selected_component.name}" component.')
        try:
            if sibling_name:
                new_item = self.controller.model.add_component_to_hierarchy(sibling_name, self._selected_component.level,
                                                                            self._selected_component.parent_id,
                                                                            self._selected_component.is_leaf)
                self._hierarchy_tree.add_item(new_item)
                pub.sendMessage(actions.HIERARCHY_EDITED)
        except HierarchyStringError as e:
            messagebox.showerror('Rename error.', e.message)

    def __add_child(self) -> None:
        child_name = simpledialog.askstring('Add child', f'Enter name of child of the "'
                                                         f'{self._selected_component.name}" component.')
        if child_name:
            try:
                new_item = self.controller.model.add_component_to_hierarchy(child_name,
                                                                            self._selected_component.level + 1,
                                                                            self._selected_component.id_, is_leaf=True)
                self._hierarchy_tree.add_item(new_item)
                pub.sendMessage(actions.HIERARCHY_EDITED)
            except HierarchyStringError as e:
                messagebox.showerror('Add component error.', e.message)

    def __rename(self) -> None:
        new_name = simpledialog.askstring('Rename', f'Enter new name for "{self._selected_component.name}" component.')
        if new_name:
            try:
                self.controller.model.change_components_name(self._selected_component, new_name)
                self.__cmp_name_var.set(new_name)
                self._hierarchy_tree.rename_item(self._selected_component)
                pub.sendMessage(actions.HIERARCHY_EDITED)
            except HierarchyStringError as e:
                messagebox.showerror('Rename error.', e.message)

    def __remove(self) -> None:
        children = self.controller.model.remove_component_from_hierarchy_preserve_children(self._selected_component)
        self._hierarchy_tree.remove_item_preserve_children(self._selected_component, children)
        self.__right_frame.grid_forget()
        self._selected_component = None
        pub.sendMessage(actions.HIERARCHY_EDITED)

    def __remove_recursively(self) -> None:
        self.controller.model.remove_component_from_hierarchy_recursively(self._selected_component)
        self._hierarchy_tree.remove_items_recursively(self._selected_component)
        self.__right_frame.grid_forget()
        self._selected_component = None
        pub.sendMessage(actions.HIERARCHY_EDITED)

    def __create_hierarchy(self) -> None:
        if self.controller.model.hierarchy:
            answer = messagebox.askyesno('Create hierarchy', 'Warning: hierarchy has already been created. \n '
                                                             'If you use this option again, previous hierarchy will be '
                                                             'overwritten, and you may lose all data regarding ports, '
                                                             'instances etc.\n If you plan to make simple changes, use '
                                                             'options such as "Create sibling", "Create child", etc.')
            if not answer:
                return

        self.__window = CreateHierarchyWindow(self, self.frame, self._build_tree)







