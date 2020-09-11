import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
from typing import Optional

from pubsub import pub

import actions
from model import Component
from state import State
from view.ask_string_window import AskStringWindow
from view.scrollbars_listbox import ScrollbarListbox
from view.abstract import HasCommonSetup, SubscribesToEvents, Resetable, Tab
from view.vertical_notebook.create_hierarchy_window import CreateHierarchyWindow
from view.common import change_controls_state, trim_string

TAB_NAME = 'Hierarchy'

COL_ID_SYMMETRY_BREAKING = 'symmetry_breaking'
COL_ID_COUNT = 'count'
COL_NAME_SYMMETRY_BREAKING = 'Symmetry breaking?'
COL_NAME_COUNT = 'Count'

TREEVIEW_HEADING = 'Component'

BASE_COMPONENT_NAME = 'Base'

CONTROL_PAD_Y = 3
CONTROL_PAD_X = 20

FRAME_PAD_Y = 20
FRAME_PAD_X = 20


class HierarchyTab(Tab,
                   HasCommonSetup,
                   SubscribesToEvents,
                   Resetable):
    """Used to create, edit and remove components.

    Attributes:
        __selected_component: Currently selected component in the components hierarchy view.
    """
    def __init__(self, parent_notebook):
        self.__state: State = State()
        self.__selected_component: Optional[Component] = None

        Tab.__init__(self, parent_notebook, TAB_NAME)
        HasCommonSetup.__init__(self)
        SubscribesToEvents.__init__(self)

    # HasCommonSetup
    def _create_widgets(self):
        self.__hierarchy_tree = ScrollbarListbox(self,
                                                 on_select_callback=self.__on_select_tree_item,
                                                 heading=TREEVIEW_HEADING,
                                                 extract_id=lambda x: x.id_,
                                                 extract_text=lambda x: x.name,
                                                 extract_ancestor=lambda x: '' if x.parent_id is None else x.parent_id,
                                                 values=self.__state.model.hierarchy,
                                                 )
        self.__right_frame = ttk.Frame(self)

        self.__cmp_name_var = tk.StringVar()
        self.__cmp_name_var.set('')
        self.__cmp_name_label = ttk.Label(self.__right_frame, anchor=tk.CENTER, textvariable=self.__cmp_name_var,
                                          style='Big.TLabel')
        self.__rename_button = ttk.Button(self.__right_frame, text='Rename', command=self.__on_rename, state=tk.DISABLED)
        self.__add_sibling_button = ttk.Button(self.__right_frame, text='Add sibling', command=self.__on_add_sibling)
        self.__add_child_button = ttk.Button(self.__right_frame, text='Add child', command=self.__on_add_child)
        self.__remove_button = ttk.Button(self.__right_frame, text='Remove', command=self.__remove, state=tk.DISABLED)
        self.__remove_recursively_button = ttk.Button(self.__right_frame, text='Remove recursively', state=tk.DISABLED,
                                                      command=lambda: self.__remove(recursively=True))
        self.__create_hierarchy_button = ttk.Button(self, text="Create hierarchy",
                                                    command=self.__on_create_hierarchy, width=14)

    def _setup_layout(self):
        self.__hierarchy_tree.grid(row=0, column=0, sticky=tk.NSEW)

        self.__right_frame.grid(row=0, column=1, sticky=tk.NSEW, pady=FRAME_PAD_Y, padx=FRAME_PAD_X)

        self.__cmp_name_label.grid(row=0, sticky=tk.EW, pady=CONTROL_PAD_Y)
        self.__rename_button.grid(row=1, sticky=tk.NSEW, pady=CONTROL_PAD_Y)
        self.__add_sibling_button.grid(row=2, sticky=tk.NSEW, pady=CONTROL_PAD_Y)
        self.__add_child_button.grid(row=3, sticky=tk.NSEW, pady=CONTROL_PAD_Y)
        self.__remove_button.grid(row=4, sticky=tk.NSEW, pady=CONTROL_PAD_Y)
        self.__remove_recursively_button.grid(row=5, sticky=tk.NSEW, pady=CONTROL_PAD_Y)

        self.__create_hierarchy_button.grid(row=1, column=0, padx=30, pady=5)
        # Hide widgets
        self.rowconfigure(0, weight=1)
        self.columnconfigure(1, weight=1, uniform='fred')
        self.columnconfigure(0, weight=3, uniform='fred')

        self.__right_frame.columnconfigure(0, weight=1)

    # SubscribesToListeners
    def _subscribe_to_events(self):
        pub.subscribe(self.__on_model_loaded, actions.MODEL_LOADED)
        pub.subscribe(self._reset, actions.RESET)

    # Hierarchy Treeview
    def __on_select_tree_item(self, cmp_id: int) -> None:
        """Executed whenever a tree item is selected (by mouse click).

        :param cmp_id: Id of the selected component.
        """
        selected_cmp: Component = self.__state.model.get_component(id_=cmp_id)
        self.__selected_component = selected_cmp
        self.__cmp_name_var.set(trim_string(selected_cmp.name, length=22))
        change_controls_state(tk.NORMAL,
                              self.__remove_button,
                              self.__remove_recursively_button,
                              self.__rename_button)

    def __on_model_loaded(self):
        """Executed whenever a model is loaded from file."""
        self._reset()
        self.__build_tree()

    def __build_tree(self) -> None:
        """Fills the tree view with components from model."""
        self.__hierarchy_tree.set_items(self.__state.model.hierarchy)

    # Resetable
    def _reset(self) -> None:
        self.__hierarchy_tree.set_items([])
        self.__selected_component = None
        self.__cmp_name_var.set('')
        change_controls_state(tk.DISABLED,
                              self.__remove_button,
                              self.__remove_recursively_button,
                              self.__rename_button)

    # Class-specific
    def __add(self, cmp_name: str, level: int, parent_id: Optional[int]) -> None:
        """Executed after creating of a new component.

        :param cmp_name: Name of a new component
        :param level: Level of the new component.
        :param parent_id: Id of the parent of the new component.
        """
        cmp = Component(cmp_name, level, parent_id=parent_id, is_leaf=True, symmetry_breaking=True)
        self.__state.model.add_component(cmp)
        self.__hierarchy_tree.add_item(cmp)
        self.__selected_component = cmp
        self.__cmp_name_var.set(trim_string(cmp.name, length=22))
        change_controls_state(tk.NORMAL,
                              self.__remove_button,
                              self.__remove_recursively_button,
                              self.__rename_button)
        pub.sendMessage(actions.HIERARCHY_EDITED)

    def __on_add_sibling(self) -> None:
        """Executed whenever the __add_sibling_button is pressed."""
        sibling_name = BASE_COMPONENT_NAME if self.__selected_component is None else self.__selected_component.name
        level = 0 if self.__selected_component is None else self.__selected_component.level
        parent_id = None if self.__selected_component is None else self.__selected_component.parent_id

        AskStringWindow(self, lambda cmp_name: self.__add(cmp_name, level, parent_id),
                        'Add sibling', f'Enter name of sibling of the {sibling_name} component.')

    def __on_add_child(self) -> None:
        """Executed whenever the __add_child_button is pressed."""
        sibling_name = BASE_COMPONENT_NAME if self.__selected_component is None else self.__selected_component.name
        level = 0 if self.__selected_component is None else self.__selected_component.level + 1
        parent_id = None if self.__selected_component is None else self.__selected_component.id_

        AskStringWindow(self, lambda cmp_name: self.__add(cmp_name, level, parent_id),
                        'Add sibling', f'Enter name of child of the {sibling_name} component.')

    def __rename(self, new_name: str) -> None:
        """Executed after renaming __selected_component.

        :param new_name: New name of the component.
        """
        cmp = self.__state.model.rename_component(self.__selected_component, new_name)
        self.__cmp_name_var.set(trim_string(cmp.name, length=22))
        self.__hierarchy_tree.rename_item(self.__selected_component)
        pub.sendMessage(actions.HIERARCHY_EDITED)

    def __on_rename(self) -> None:
        """Executed whenever the __rename_button is pressed."""
        if self.__selected_component:
            AskStringWindow(self, self.__rename, 'Rename component',
                            f'Enter new name for "{self.__selected_component.name}" component.',
                            string=self.__selected_component.name)

    def __remove(self, recursively=False) -> None:
        """Executed whenever the __rename_button or __remove_recursively_button is pressed.

        :param recursively: True if __remove_recursively_button is pressed. Removes the selected component and all of
            its children; Otherwise set to False and removes only the __selected_component, setting the
            parent_id of its children to __selected_component.parent_id.
        """
        if self.__selected_component:
            if recursively:
                self.__state.model.remove_component_recursively(self.__selected_component)
                self.__hierarchy_tree.remove_item_recursively(self.__selected_component)
            else:
                self.__state.model.remove_component_preserve_children(self.__selected_component)
                self.__hierarchy_tree.remove_item_preserve_children(self.__selected_component)
            change_controls_state(tk.DISABLED,
                                  self.__remove_button,
                                  self.__remove_recursively_button,
                                  self.__rename_button)
            self.__selected_component = None
            self.__cmp_name_var.set('')
            pub.sendMessage(actions.HIERARCHY_EDITED)

    def __create_hierarchy(self):
        """Executes when the hierarchy is created (in the CreateHierarchyWindow)."""
        self.__build_tree()
        pub.sendMessage(actions.HIERARCHY_EDITED)

    def __on_create_hierarchy(self) -> None:
        """Executed whenever the __create_hierarchy_button is pressed."""
        if self.__state.model.hierarchy:
            answer = messagebox.askyesno('Create hierarchy', 'Warning: hierarchy has already been created. \n '
                                                             'If you use this option again, previous hierarchy will be '
                                                             'overwritten, and you may lose all data regarding ports, '
                                                             'instances etc.\n If you plan to make simple changes, use '
                                                             'options such as "Create sibling", "Create child", etc.')
            if not answer:
                return

        CreateHierarchyWindow(self, self.__create_hierarchy)







