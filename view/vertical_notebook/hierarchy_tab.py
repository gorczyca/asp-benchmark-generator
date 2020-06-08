from tkinter import ttk
from view.vertical_notebook.create_hierarchy_window import CreateHierarchyWindow
from view.hierarchy_tree import HierarchyTree
from view.vertical_notebook.vertical_notebook_tab import VerticalNotebookTab
from pubsub import pub
from controller import actions
from tkinter import messagebox, simpledialog
import tkinter as tk
# from view.hover_button import HoverButton

TAB_NAME = 'Hierarchy'

COL_ID_SYMMETRY_BREAKING = 'symmetry_breaking'
COL_ID_COUNT = 'count'
COL_NAME_SYMMETRY_BREAKING = 'Symmetry breaking?'
COL_NAME_COUNT = 'Count'

BUTTONS_PAD_X = 30
BUTTONS_PAD_Y = 3
LABEL_PAD_X = 40
LABEL_PAD_Y = 10


class HierarchyTab(VerticalNotebookTab):
    def __init__(self, parent, parent_notebook, *args, **kwargs):
        VerticalNotebookTab.__init__(self, parent, parent_notebook, TAB_NAME, *args, **kwargs)

        self.hierarchy_tree = None
        self.__selected_component_name = None
        self.__right_frame = tk.Frame(self.frame)
        # self.__right_frame.grid(row=0, column=1, sticky='nswe')

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

        self.__cmp_name_label.grid(row=0, sticky='nswe', padx=LABEL_PAD_X, pady=LABEL_PAD_Y)
        self.__rename_button.grid(row=1, sticky='nswe', padx=BUTTONS_PAD_X, pady=BUTTONS_PAD_Y)
        self.__add_sibling_button.grid(row=2, sticky='nswe', padx=BUTTONS_PAD_X, pady=BUTTONS_PAD_Y)
        self.__add_child_button.grid(row=3, sticky='nswe', padx=BUTTONS_PAD_X, pady=BUTTONS_PAD_Y)
        self.__remove_button.grid(row=4, sticky='nswe', padx=BUTTONS_PAD_X, pady=BUTTONS_PAD_Y)
        self.__remove_recursively_button.grid(row=5, sticky='nswe', padx=BUTTONS_PAD_X, pady=BUTTONS_PAD_Y)

        self.__right_frame.columnconfigure(0, weight=1)

        self.frame.rowconfigure(0, weight=1)
        self.frame.columnconfigure(0, weight=2, uniform='fred')
        self.frame.columnconfigure(1, weight=1, uniform='fred')

        self.__create_hierarchy_button = ttk.Button(self.frame, text="Create hierarchy",
                                                    command=self.__create_hierarchy, width=14)
        self.__create_hierarchy_button.grid(row=1, column=0, padx=30, pady=5)

        pub.subscribe(self.__reset, actions.RESET)
        pub.subscribe(self.__hierarchy_created, actions.HIERARCHY_CREATED)

    def __add_sibling(self):
        sibling_name = simpledialog.askstring('Add sibling', f'Enter name of sibling of the "{self.__selected_component_name}" component.')
        if sibling_name:
            selected_cmp = self.controller.model.get_component_by_name(self.__selected_component_name)
            new_item = self.controller.model.add_to_hierarchy(sibling_name, selected_cmp.level, selected_cmp.parent_id,
                                                              selected_cmp.is_leaf)
            self.hierarchy_tree.add_item(new_item)
            pub.sendMessage(actions.HIERARCHY_EDITED)

    def __add_child(self):
        child_name = simpledialog.askstring('Add child', f'Enter name of child of the "{self.__selected_component_name}" component.')
        if child_name:
            selected_cmp = self.controller.model.get_component_by_name(self.__selected_component_name)
            selected_cmp.is_leaf = False # if has a child then cannot be a leaf
            selected_cmp.symmetry_breaking = None # if isn't a leaf then cannot have symmetry breaking
            new_item = self.controller.model.add_to_hierarchy(child_name, selected_cmp.level + 1, selected_cmp.id_,
                                                              True)
            self.hierarchy_tree.add_item(new_item)
            pub.sendMessage(actions.HIERARCHY_EDITED)

    def __rename(self):
        old_name = self.__selected_component_name
        new_name = simpledialog.askstring('Rename', f'Enter new name for "{self.__selected_component_name}" component.')
        if new_name:
            # TODO: check if unique
            cmp = self.controller.model.get_component_by_name(old_name)
            self.__selected_component_name = new_name
            self.__cmp_name_var.set(new_name)
            cmp.set_name(new_name)
            self.hierarchy_tree.rename_item(cmp)
            pub.sendMessage(actions.HIERARCHY_EDITED)

    def __remove(self):
        cmp = self.controller.model.get_component_by_name(self.__selected_component_name)
        children = self.controller.model.remove_component_preserve_children(cmp)
        self.hierarchy_tree.remove_item_preserve_children(cmp, children)
        pub.sendMessage(actions.HIERARCHY_EDITED)
        self.__right_frame.grid_forget()

    def __remove_recursively(self):
        cmp = self.controller.model.get_component_by_name(self.__selected_component_name)
        removed_items = self.controller.model.remove_component_recursively(cmp)  # alternatively, remove just this one component
        self.hierarchy_tree.remove_items_recursively(cmp, removed_items)
        pub.sendMessage(actions.HIERARCHY_EDITED)
        self.__right_frame.grid_forget()

    def __on_select(self, cmp_name):
        self.__selected_component_name = cmp_name
        self.__cmp_name_var.set(cmp_name)
        self.__right_frame.grid(row=0, column=1, sticky='nswe')

    def __reset(self):
        self.__right_frame.grid_forget()
        if self.hierarchy_tree:
            self.hierarchy_tree.destroy_()
            self.hierarchy_tree = None

    def __hierarchy_created(self):
        hierarchy = self.controller.model.get_hierarchy()
        self.hierarchy_tree = HierarchyTree(self.frame, hierarchy, on_select_callback=self.__on_select)

    def __create_hierarchy(self):
        hierarchy = self.controller.model.get_hierarchy()
        if hierarchy:
            answer = messagebox.askyesno('Create hierarchy', 'Warning: hierarchy has already been created. \n '
                                                        'If you use this option again, previous hierarchy will be '
                                                        'overwritten, and you may lose all data regarding ports, '
                                                        'instances etc.\n If you plan to make simple changes, '
                                                        'use options such as "Create sibling", "Create child", etc.')
            if not answer:
                return

        self.__window = CreateHierarchyWindow(self, self.frame, self.__hierarchy_created)







