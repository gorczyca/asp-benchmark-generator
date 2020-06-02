from tkinter import ttk
import tkinter as tk
from view.c_frame import CFrame


COL_ID_COMPONENT = '#0'
COL_NAME_COMPONENT = 'Component'

NONE_STRING = ''
BOOL_TO_STRING = {True: 'yes', False: 'no'}


class HierarchyTree(ttk.Treeview):
    def __init__(self, parent_frame, hierarchy, columns=None, **kwargs): # TODO: column is a tuple (id, name, width, minwidth, stretch, anchor)
        ttk.Treeview.__init__(self, parent_frame, **kwargs)
        # CFrame.__init__(self, parent, parent_frame, *args, **kwargs)

        self.parent_frame = parent_frame

        self.__tree = ttk.Treeview(self.parent_frame, **kwargs)

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

        self.__add_to_treeview('', hierarchy)
        self.__tree.grid(row=0, column=0, sticky='nswe')

    def __add_to_treeview(self, ancestor, children):
        for cmp in children:
            values = []
            for col_id in self.__column_ids:
                value = cmp.get_by_name(col_id)
                if type(value) is bool:
                    value = BOOL_TO_STRING[value]
                elif not value:
                    value = NONE_STRING
                values.append(value)
            cmp_in_tree = self.__tree.insert(ancestor, tk.END, text=cmp.name, values=values)
            self.__add_to_treeview(cmp_in_tree, cmp.children)
