from tkinter import ttk
import tkinter as tk
from view.r_frame import RFrame


COL_ID_COMPONENT = '#0'
COL_NAME_COMPONENT = 'Component'

NONE_STRING = ''
BOOL_TO_STRING = {True: 'yes', False: 'no'}


class HierarchyTree(ttk.Treeview, RFrame):
    def __init__(self, parent, columns=None, *args, **kwargs): # TODO: column is a tuple (id, name, width, minwidth, stretch, anchor)
        ttk.Treeview.__init__(self, parent, **kwargs)
        RFrame.__init__(self, parent, *args, **kwargs)

        self.__tree = ttk.Treeview(self.parent._frame, **kwargs)

        self.__tree.column(COL_ID_COMPONENT, width=270, minwidth=270)  # TODO: find values for width, minwidth
        self.__tree.heading(COL_ID_COMPONENT, text=COL_NAME_COMPONENT, anchor=tk.W)

        self.__column_ids = []
        if columns:
            column_ids = [col[0] for col in columns]
            self.__column_ids = column_ids
            self.__tree['columns'] = column_ids
            for col in columns:
                self.__tree.column(col[0], width=col[2], minwidth=col[3], stretch=col[4])
                self.__tree.heading(col[0], text=col[1], anchor=col[5])    # TODO: lepiej to

        self.__add_to_treeview('', self.root.hierarchy)
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
