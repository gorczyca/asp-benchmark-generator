import tkinter as tk
from tkinter import ttk
from typing import List, Callable, Any

from model.component import Component

COL_ID_COMPONENT = '#0'
COL_NAME_COMPONENT = 'Component'


class HierarchyTree(ttk.Treeview):
    def __init__(self, parent_frame, hierarchy: List[Component], columns=None, on_select_callback=None,
                 extract_values: Callable[[Component], Any] = lambda cmp: [], **kwargs):
        ttk.Treeview.__init__(self, parent_frame, **kwargs)

        self.parent_frame = parent_frame

        self.__tree = ttk.Treeview(self.parent_frame, style='Custom.Treeview', selectmode='extended', **kwargs)

        self.__extract_values = extract_values

        if on_select_callback:
            self.__tree.bind('<ButtonRelease-1>', self.__item_selected)
            self.__on_select_callback = on_select_callback

        self.__tree.column(COL_ID_COMPONENT, stretch=tk.YES)  # TODO: find values for width, minwidth
        self.__tree.heading(COL_ID_COMPONENT, text=COL_NAME_COMPONENT, anchor=tk.W)

        self.__column_ids = []
        if columns:
            column_ids = [col.id_ for col in columns]
            self.__column_ids = column_ids
            self.__tree['columns'] = column_ids
            for col in columns:
                self.__tree.column(col.id_, stretch=col.stretch)
                self.__tree.heading(col.id_, text=col.name, anchor=col.anchor)    # TODO: better

        self.__build_tree(hierarchy)
        self.__tree.grid(row=0, column=0, sticky='nswe')

    def add_item(self, cmp: Component):
        ancestor = '' if cmp.parent_id is None else cmp.parent_id  # TODO: do poprawy to
        values = self.__extract_values(cmp)
        self.__tree.insert(ancestor, tk.END, iid=cmp.id_, text=cmp.name, values=values)

    def rename_item(self, cmp: Component):
        self.__tree.item(cmp.id_, text=cmp.name)

    def remove_items_recursively(self, cmp: Component):
        self.__tree.delete(cmp.id_)

    def remove_item_preserve_children(self, cmp: Component, children: List[Component]):
        cmp_parent = self.__tree.parent(cmp.id_)
        children_count = len(children)
        for c in children:
            self.__tree.move(c.id_, cmp_parent, children_count) # TODO: check with tk.END
        self.__tree.delete(cmp.id_)

    def update_values(self, cmps: List[Component]):
        for c in cmps:
            self.__update_value(c)

    def __update_value(self, cmp: Component):
        values = self.__extract_values(cmp)
        self.__tree.item(cmp.id_, values=values)

    def __item_selected(self, _):
        selected_item_id_str: str = self.__tree.focus()
        if selected_item_id_str:
            self.__on_select_callback(int(selected_item_id_str))

    def destroy_(self):
        self.__tree.destroy()
        self.__tree = None      # TODO: is that necessary?

    def __build_tree(self, hierarchy: List[Component]):
        for cmp in hierarchy:
            values = self.__extract_values(cmp)
            ancestor = cmp.parent_id if cmp.parent_id is not None else ''
            self.__tree.insert(ancestor, tk.END, iid=cmp.id_, text=cmp.name, values=values)

