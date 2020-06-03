import tkinter as tk
from view.style import CustomTheme
from view.menu import Menu
from view.main_notebook.main_notebook import MainNotebook, EncodingTab, InstancesTab
from view.vertical_notebook.vertical_notebook import VerticalNotebook, HierarchyTab, AssociationsTab, \
    PortsTab, ResourcesTab, ConstraintsTab

WINDOW_TITLE = 'Benchmark Generator'


class View(tk.Frame):
    def __init__(self, controller, main_window, *args, **kwargs):
        tk.Frame.__init__(self, main_window, *args, **kwargs)
        self.controller = controller
        self.frame = main_window
        self.frame.title(WINDOW_TITLE)
        # self.frame.geometry(WINDOW_SIZE)
        self.__setup_layout()

    def __setup_layout(self):
        CustomTheme().use()

        self.__menu = Menu(self, self.frame)
        self.__main_notebook = MainNotebook(self, self.frame)

        self.__encoding_frame = EncodingTab(self, self.__main_notebook.notebook)
        self.__instances_tab = InstancesTab(self, self.__main_notebook.notebook)

        self.__vertical_notebook = VerticalNotebook(self, self.__encoding_frame.frame)

        self.__hierarchy_tab = HierarchyTab(self, self.__vertical_notebook.notebook)
        self.__associations_tab = AssociationsTab(self, self.__vertical_notebook.notebook)
        self.__ports_tab = PortsTab(self, self.__vertical_notebook.notebook)
        self.__resources_tab = ResourcesTab(self, self.__vertical_notebook.notebook)
        self.__constraints_tab = ConstraintsTab(self, self.__vertical_notebook.notebook)



