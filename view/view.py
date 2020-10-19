import tkinter as tk
from tkinter import ttk
from typing import Optional

from pubsub import pub

from misc import actions
from misc.file_operations import extract_file_name
from view.menu import Menu
from view.abstract import HasCommonSetup, SubscribesToEvents
from view.main_notebook import EncodingTab, InstancesTab
from view.vertical_notebook import TaxonomyTab, AssociationsTab, \
    PortsTab, ResourcesTab, ConstraintsTab


NEW_FILE_NAME = 'untitled'
WINDOW_TITLE = 'Benchmark Generator'


class View(ttk.Frame,
           HasCommonSetup,
           SubscribesToEvents):
    """Class holds all references for widgets.

    Attributes:
        __main_window: Application's main window (tk.Tk).
    """
    def __init__(self,
                 main_window: tk.Tk):
        ttk.Frame.__init__(self, main_window)

        main_window.deiconify()     # Bring back window after withdraw

        self.__main_window: tk.Tk = main_window

        HasCommonSetup.__init__(self)
        SubscribesToEvents.__init__(self)

    def _create_widgets(self) -> None:
        self.__menu = Menu(self.__main_window)
        self.__main_notebook = ttk.Notebook(self.__main_window, style='Main.TNotebook')

        self.__encoding_frame = EncodingTab(self.__main_notebook)
        self.__instances_tab = InstancesTab(self.__main_notebook)

        self.__vertical_notebook = ttk.Notebook(self.__encoding_frame, style='Vertical.TNotebook')

        self.__taxonomy_tab = TaxonomyTab(self.__vertical_notebook)
        self.__associations_tab = AssociationsTab(self.__vertical_notebook)
        self.__ports_tab = PortsTab(self.__vertical_notebook)
        self.__resources_tab = ResourcesTab(self.__vertical_notebook)
        self.__constraints_tab = ConstraintsTab(self.__vertical_notebook)

    def _setup_layout(self) -> None:
        self.__main_notebook.grid(row=0, column=0, sticky=tk.NSEW)
        self.__vertical_notebook.grid(row=0, column=0, sticky=tk.NSEW)

        self.__main_window.rowconfigure(0, weight=1)
        self.__main_window.columnconfigure(0, weight=1)

        self.__set_geometry()
        self.__set_window_title()

    def _subscribe_to_events(self) -> None:
        pub.subscribe(self.__set_window_title, actions.MODEL_SAVED)
        pub.subscribe(self.__set_window_title, actions.RESET)

    def __set_window_title(self, file_name: Optional[str] = None) -> None:
        """Executed whenever the model is saved to a file or a new project is created.
        Updates window's title accordingly.

        :param file_name: Path to the file the model has been saved to.
        """
        if not file_name:
            file_name = NEW_FILE_NAME
        else:
            file_name = extract_file_name(file_name)
        self.__main_window.title(f'{file_name} - {WINDOW_TITLE}')

    def __set_geometry(self) -> None:
        """Sets window's dimensions."""
        try:
            self.__main_window.wm_state('zoomed')   # Windows
        except tk.TclError:
            try:
                self.__main_window.wm_attributes('-zoomed', 1)  # Linux / requires tests
            except tk.TclError:
                screen_width = self.__main_window.winfo_screenwidth()
                screen_height = self.__main_window.winfo_screenheight()
                self.__main_window.geometry(f'{screen_width}x{screen_height}+0+0')
