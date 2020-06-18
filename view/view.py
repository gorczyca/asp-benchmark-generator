import tkinter as tk
from typing import Optional

from pubsub import pub

import actions
from view.main_notebook.main_notebook import MainNotebook
from view.main_notebook.encoding_tab import EncodingTab
from view.main_notebook.instances_tab import InstancesTab
from view.menu import Menu
from view.style import CustomTheme, VERTICAL_TAB_HEIGHT, VERTICAL_TAB_WIDTH
from view.vertical_notebook.vertical_notebook import VerticalNotebook
from view.vertical_notebook.hierarchy_tab import HierarchyTab
from view.vertical_notebook.associations_tab import AssociationsTab
from view.vertical_notebook.ports_tab import PortsTab
from view.vertical_notebook.resources_tab import ResourcesTab
from view.vertical_notebook.constraints_tab import ConstraintsTab

NEW_FILE_NAME = 'untitled'
WINDOW_TITLE = 'Benchmark Generator'
UNSAVED_CHANGES_SYMBOL = '*'


class View(tk.Frame):
    """Class holds all references for widgets.

    Attributes:
        __menu:
    """
    def __init__(self, controller, main_window, *args, **kwargs):
        tk.Frame.__init__(self, main_window, *args, **kwargs)
        self.__controller = controller
        self.__main_window = main_window

        self.__window_title: Optional[str] = None

        self.__init_title()
        # self.frame.geometry(WINDOW_SIZE)
        self.__setup_layout()

        pub.subscribe(self.__on_model_changed, actions.MODEL_CHANGED)
        pub.subscribe(self.__on_model_saved, actions.MODEL_SAVED)
        pub.subscribe(self.__init_title, actions.RESET)

    @property
    def controller(self): return self.__controller

    def __setup_layout(self):
        CustomTheme().use()

        self.__menu = Menu(self, self.__main_window)
        self.__main_notebook = MainNotebook(self, self.__main_window)

        self.__encoding_frame = EncodingTab(self, self.__main_notebook.notebook)
        self.__instances_tab = InstancesTab(self, self.__main_notebook.notebook)

        self.__vertical_notebook = VerticalNotebook(self, self.__encoding_frame.frame)

        self.__hierarchy_tab = HierarchyTab(self, self.__vertical_notebook.notebook,
                                            height=VERTICAL_TAB_HEIGHT, width=VERTICAL_TAB_WIDTH)
        self.__associations_tab = AssociationsTab(self, self.__vertical_notebook.notebook,
                                                  height=VERTICAL_TAB_HEIGHT, width=VERTICAL_TAB_WIDTH)
        self.__ports_tab = PortsTab(self, self.__vertical_notebook.notebook,
                                    height=VERTICAL_TAB_HEIGHT, width=VERTICAL_TAB_WIDTH)
        self.__resources_tab = ResourcesTab(self, self.__vertical_notebook.notebook,
                                            height=VERTICAL_TAB_HEIGHT, width=VERTICAL_TAB_WIDTH)
        self.__constraints_tab = ConstraintsTab(self, self.__vertical_notebook.notebook,
                                                height=VERTICAL_TAB_HEIGHT, width=VERTICAL_TAB_WIDTH)

    def __init_title(self):
        window_title = f'{NEW_FILE_NAME} - {WINDOW_TITLE}'
        self.__main_window.title(window_title)
        self.__window_title = window_title

    def __on_model_changed(self):
        self.__main_window.title(f'{UNSAVED_CHANGES_SYMBOL} {self.__window_title}')

    def __on_model_saved(self, file_name):
        window_title = f'{file_name} - {WINDOW_TITLE}'
        self.__main_window.title(window_title)
        self.__window_title = window_title







