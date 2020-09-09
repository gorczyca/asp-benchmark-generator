import tkinter as tk
from tkinter import ttk
from typing import Optional

from pubsub import pub

import actions
from file_operations import extract_file_name
from view import Menu
from view.abstract import HasCommonSetup, SubscribesToEvents
from view.main_notebook import MainNotebook, EncodingTab, InstancesTab
from view.vertical_notebook import VerticalNotebook, HierarchyTab, AssociationsTab, \
    PortsTab, ResourcesTab, ConstraintsTab


NEW_FILE_NAME = 'untitled'
WINDOW_TITLE = 'Benchmark Generator'
UNSAVED_CHANGES_SYMBOL = '*'


class View(ttk.Frame,
           HasCommonSetup,
           SubscribesToEvents):
    """Class holds all references for widgets.

    Attributes:
        __menu:
    """
    def __init__(self, main_window):
        ttk.Frame.__init__(self, main_window)

        self.__main_window = main_window
        self.__window_title: Optional[str] = None

        HasCommonSetup.__init__(self)
        SubscribesToEvents.__init__(self)

    def _create_widgets(self) -> None:
        self.__menu = Menu(self.__main_window)
        self.__main_notebook = MainNotebook(self.__main_window)

        self.__encoding_frame = EncodingTab(self.__main_notebook.notebook)
        self.__instances_tab = InstancesTab(self.__main_notebook.notebook)

        self.__vertical_notebook = VerticalNotebook(self.__encoding_frame.frame)

        self.__hierarchy_tab = HierarchyTab(self.__vertical_notebook.notebook)
        self.__associations_tab = AssociationsTab(self.__vertical_notebook.notebook)
        self.__ports_tab = PortsTab(self.__vertical_notebook.notebook)
        self.__resources_tab = ResourcesTab(self.__vertical_notebook.notebook)
        self.__constraints_tab = ConstraintsTab(self.__vertical_notebook.notebook)

    def _setup_layout(self) -> None:
        self.__main_window.rowconfigure(0, weight=1)
        self.__main_window.columnconfigure(0, weight=1)

        self.__set_geometry()
        self.__init_title()

    def _subscribe_to_events(self) -> None:
        pub.subscribe(self.__on_model_saved, actions.MODEL_SAVED)
        pub.subscribe(self.__init_title, actions.RESET)

    def __init_title(self):
        window_title = f'{NEW_FILE_NAME} - {WINDOW_TITLE}'
        self.__main_window.title(window_title)
        self.__window_title = window_title

    def __on_model_saved(self, file_name=None):
        if not file_name:
            file_name = NEW_FILE_NAME
        else:
            file_name = extract_file_name(file_name)
        window_title = f'{file_name} - {WINDOW_TITLE}'
        self.__main_window.title(window_title)
        self.__window_title = window_title

    def __set_geometry(self):
        try:
            self.__main_window.wm_state('zoomed')   # Windows
        except tk.TclError as e:
            try:
                self.__main_window.wm_attributes('-zoomed', 1)  # Linux / requires tests
            except tk.TclError as e:
                screen_width = self.__main_window.winfo_screenwidth()
                screen_height = self.__main_window.winfo_screenheight()
                self.__main_window.geometry(f'{screen_width}x{screen_height}+0+0')
