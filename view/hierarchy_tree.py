from tkinter import ttk
import tkinter as tk
from view.c_frame import CFrame


COL_ID_COMPONENT = '#0'
COL_NAME_COMPONENT = 'Component'


class HierarchyTree(ttk.Treeview):
    def __init__(self, parent_frame, hierarchy, columns=None, on_select_callback=None, extract_values=lambda cmp: [],
                 **kwargs):
        ttk.Treeview.__init__(self, parent_frame, **kwargs)
        # CFrame.__init__(self, parent, parent_frame, *args, **kwargs)

        self.parent_frame = parent_frame

        self.items = {}

        self.__tree = ttk.Treeview(self.parent_frame, style='Custom.Treeview', selectmode='extended', **kwargs)

        self.__extract_values = extract_values

        if on_select_callback:
            self.__tree.bind('<ButtonRelease-1>', self.__item_selected)
            self.__on_select_callback = on_select_callback

        self.__tree.column(COL_ID_COMPONENT, stretch=tk.YES)  # TODO: find values for width, minwidth
        self.__tree.heading(COL_ID_COMPONENT, text=COL_NAME_COMPONENT, anchor=tk.W)

        self.__column_ids = []
        if columns:
            column_ids = [col.id for col in columns]
            self.__column_ids = column_ids
            self.__tree['columns'] = column_ids
            for col in columns:
                self.__tree.column(col.id, stretch=col.stretch)
                self.__tree.heading(col.id, text=col.name, anchor=col.anchor)    # TODO: lepiej to

        self.__build_tree(hierarchy)
        self.__tree.grid(row=0, column=0, sticky='nswe')

    def add_item(self, cmp):
        ancestor = '' if cmp.parent_id is None else self.items[cmp.parent_id]  # TODO: do poprawy to
        values = self.__extract_values(cmp)
        self.items[cmp.id_] = self.__tree.insert(ancestor, tk.END, text=cmp.name, values=values)

    def rename_item(self, cmp):
        self.__tree.item(self.items[cmp.id_], text=cmp.get_name())

    def remove_items_recursively(self, root, cmps_to_remove):
        self.__tree.delete(self.items[root.id_])
        for c in cmps_to_remove:
            self.items.pop(c.id_)

    def remove_item_preserve_children(self, item, children):
        cmp_parent = self.__tree.parent(self.items[item.id_])
        children_count = len(children)
        for c in children:
            self.__tree.move(self.items[c.id_], cmp_parent, children_count)
        self.__tree.delete(self.items[item.id_])

    def update_values(self, cmps):
        for cmp in cmps:
            self.__update_value(cmp)

    def __update_value(self, cmp):
        values = self.__extract_values(cmp)
        self.__tree.item(self.items[cmp.id_], values=values)

    def __item_selected(self, _):
        selected_item_name = self.__tree.item(self.__tree.focus())['text']
        if selected_item_name is not '':
            self.__on_select_callback(selected_item_name)

    def destroy_(self):
        self.__tree.destroy()
        self.__tree = None
        self.items = {}

    def __build_tree(self, hierarchy):
        for cmp in hierarchy:
            values = self.__extract_values(cmp)
            ancestor = '' if cmp.parent_id is None else self.items[cmp.parent_id]  # TODO: do poprawy to
            self.items[cmp.id_] = self.__tree.insert(ancestor, tk.END, text=cmp.name, values=values)
