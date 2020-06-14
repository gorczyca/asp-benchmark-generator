import tkinter as tk
from tkinter import messagebox, simpledialog
from tkinter import ttk
from typing import Optional

from pubsub import pub

import actions
from exceptions import HierarchyStringError
from model.component import Component
from view.c_frame import CFrame
from view.hierarchy_tree import HierarchyTree
from view.vertical_notebook.create_hierarchy_window import CreateHierarchyWindow
from view.vertical_notebook.vertical_notebook_tab import VerticalNotebookTab

TAB_NAME = 'Hierarchy'

COL_ID_SYMMETRY_BREAKING = 'symmetry_breaking'
COL_ID_COUNT = 'count'
COL_NAME_SYMMETRY_BREAKING = 'Symmetry breaking?'
COL_NAME_COUNT = 'Count'

BUTTONS_PAD_X = 30
BUTTONS_PAD_Y = 3
LABEL_PAD_X = 40
LABEL_PAD_Y = 10


class HierarchyTab(VerticalNotebookTab, CFrame):
    def __init__(self, parent, parent_notebook, *args, **kwargs):
        VerticalNotebookTab.__init__(self, parent_notebook, TAB_NAME, *args, **kwargs)
        CFrame.__init__(self, parent, parent_notebook)

        self.__hierarchy_tree: Optional[HierarchyTree] = None
        self.__selected_component: Optional[Component] = None

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

    def _subscribe_to_listeners(self):
        pub.subscribe(self.__reset, actions.RESET)
        pub.subscribe(self.__hierarchy_created, actions.HIERARCHY_CREATED)

    def __add_sibling(self):
        sibling_name = simpledialog.askstring('Add sibling', f'Enter name of sibling of the "'
                                                             f'{self.__selected_component.name}" component.')
        try:
            if sibling_name:
                new_item = self.controller.model.add_component_to_hierarchy(sibling_name, self.__selected_component.level,
                                                                            self.__selected_component.parent_id,
                                                                            self.__selected_component.is_leaf)
                self.__hierarchy_tree.add_item(new_item)
                pub.sendMessage(actions.HIERARCHY_EDITED)
        except HierarchyStringError as e:
            messagebox.showerror('Rename error.', e.message)

    def __add_child(self):
        child_name = simpledialog.askstring('Add child', f'Enter name of child of the "'
                                                         f'{self.__selected_component.name}" component.')
        if child_name:
            try:
                new_item = self.controller.model.add_component_to_hierarchy(child_name,
                                                                            self.__selected_component.level+1,
                                                                            self.__selected_component.id_, is_leaf=True)
                self.__hierarchy_tree.add_item(new_item)
                pub.sendMessage(actions.HIERARCHY_EDITED)
            except HierarchyStringError as e:
                messagebox.showerror('Add component error.', e.message)

    def __rename(self):
        new_name = simpledialog.askstring('Rename', f'Enter new name for "{self.__selected_component.name}" component.')
        if new_name:
            try:
                self.controller.model.change_components_name(self.__selected_component, new_name)
                self.__cmp_name_var.set(new_name)
                self.__hierarchy_tree.rename_item(self.__selected_component)
                pub.sendMessage(actions.HIERARCHY_EDITED)
            except HierarchyStringError as e:
                messagebox.showerror('Rename error.', e.message)

    def __remove(self):
        children = self.controller.model.remove_component_from_hierarchy_preserve_children(self.__selected_component)
        self.__hierarchy_tree.remove_item_preserve_children(self.__selected_component, children)
        self.__right_frame.grid_forget()
        self.__selected_component = None
        pub.sendMessage(actions.HIERARCHY_EDITED)

    def __remove_recursively(self):
        self.controller.model.remove_component_from_hierarchy_recursively(self.__selected_component)
        self.__hierarchy_tree.remove_items_recursively(self.__selected_component)
        self.__right_frame.grid_forget()
        self.__selected_component = None
        pub.sendMessage(actions.HIERARCHY_EDITED)

    def __on_select(self, cmp_id):
        selected_component: Component = self.controller.model.get_component_by_id(cmp_id)
        self.__selected_component = selected_component
        self.__cmp_name_var.set(selected_component.name)
        self.__right_frame.grid(row=0, column=1, sticky=tk.NSEW)

    def __reset(self):
        self.__right_frame.grid_forget()
        if self.__hierarchy_tree:
            self.__hierarchy_tree.destroy_()
            self.__hierarchy_tree = None

    def __hierarchy_created(self):
        if self.__hierarchy_tree:
            self.__hierarchy_tree.destroy_()
        self.__hierarchy_tree = HierarchyTree(self.frame, self.controller.model.hierarchy,
                                              on_select_callback=self.__on_select)

    def __create_hierarchy(self):
        if self.controller.model.hierarchy:
            answer = messagebox.askyesno('Create hierarchy', 'Warning: hierarchy has already been created. \n '
                                                             'If you use this option again, previous hierarchy will be '
                                                             'overwritten, and you may lose all data regarding ports, '
                                                             'instances etc.\n If you plan to make simple changes, use '
                                                             'options such as "Create sibling", "Create child", etc.')
            if not answer:
                return

        self.__window = CreateHierarchyWindow(self, self.frame, self.__hierarchy_created)







