from tkinter import ttk
from view.tab import Tab
from view.vertical_notebook.edit_hierarchy_window import EditHierarchyWindow

TAB_NAME = 'Hierarchy'


class HierarchyTab(Tab):
    def __init__(self, parent, *args, **kwargs):
        Tab.__init__(self, parent, TAB_NAME, *args, **kwargs)

        self.hierarchy = None

        self.button = ttk.Button(self._frame, text="Edit hierarchy", command=self.__edit_hierarchy)

        self._frame.rowconfigure(0, weight=1)
        self._frame.columnconfigure(0, weight=1)
        self.button.grid(row=1, column=0)

    def __callback(self):
        pass

    def __edit_hierarchy(self):
        self._window = EditHierarchyWindow(self, self.__callback)







