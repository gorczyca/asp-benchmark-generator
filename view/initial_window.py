import tkinter as tk
from json import JSONDecodeError
from tkinter import ttk, messagebox

from exceptions import BGError
from file_operations import open_, solve
from model.model import Model
from settings import Settings
from state import State
from view.ask_string_window import AskStringWindow
from view.scrollbars_listbox import ScrollbarListbox
from view.style import CONTROL_PAD_Y, FRAME_PAD_X, FRAME_PAD_Y
from view.abstract.has_common_setup import HasCommonSetup
from view.abstract.window import Window
from file_operations import extract_file_name

WINDOW_TITLE = 'Welcome'
WELCOME_TEXT = "Welcome to Benchmark Generator\nfor configuration's problem ASP encodings."
TREEVIEW_HEADING = 'Recently opened projects'

WINDOW_WIDTH_RATIO = 0.45
WINDOW_HEIGHT = 300


class InitialWindow(HasCommonSetup,
                    Window):
    def __init__(self, parent_frame, callback):
        self.__state = State()
        self.__callback = callback

        self.__state.settings = Settings.get_settings()
        self.__recent_projects = len(self.__state.settings.recently_opened_projects) > 0

        Window.__init__(self, parent_frame, WINDOW_TITLE)
        HasCommonSetup.__init__(self)

    def _create_widgets(self) -> None:
        self.__main_frame = tk.Frame(self._window)
        self.__welcome_label = ttk.Label(self.__main_frame, text=WELCOME_TEXT, anchor=tk.W)
        self.__create_new_project_button = ttk.Button(self.__main_frame, text='Create new project',
                                                      command=self.__on_create_new_project)
        self.__open_project_button = ttk.Button(self.__main_frame, text='Open project',
                                                command=self.__open_project)
        self.__solve_button = ttk.Button(self.__main_frame, text='Solve...', command=solve)

        if self.__recent_projects:
            self.__recent_projects_listbox = ScrollbarListbox(self._window,
                                                              on_select_callback=self.__on_select_tree_item,
                                                              heading=TREEVIEW_HEADING,
                                                              extract_id=lambda x: self.__state.settings.recently_opened_projects.index(x),
                                                              extract_text=lambda x: f'{x.root_name} '
                                                                                     f'(~/{extract_file_name(x.path)})',
                                                              values=self.__state.settings.recently_opened_projects,
                                                              scrollbars=False)

    def _setup_layout(self) -> None:
        self.__welcome_label.grid(row=0, sticky=tk.EW, pady=CONTROL_PAD_Y)
        self.__create_new_project_button.grid(row=1, sticky=tk.EW, pady=CONTROL_PAD_Y)
        self.__open_project_button.grid(row=2, sticky=tk.EW, pady=CONTROL_PAD_Y)
        self.__solve_button.grid(row=3, sticky=tk.EW, pady=CONTROL_PAD_Y)

        if self.__recent_projects:
            self.__recent_projects_listbox.grid(row=0, column=0, sticky=tk.NSEW, pady=FRAME_PAD_Y, padx=(FRAME_PAD_X, 0))
            # TODO: center it! (don't put 60 there)
            self.__main_frame.grid(row=0, column=1, sticky=tk.NSEW, pady=FRAME_PAD_Y, padx=(60, FRAME_PAD_X))

            self._window.columnconfigure(0, weight=1)
            self._window.columnconfigure(1, weight=1)
        else:
            self.__main_frame.grid(row=0, column=0, sticky=tk.NSEW, pady=FRAME_PAD_Y, padx=FRAME_PAD_X)
            self._window.columnconfigure(0, weight=1)

        self.__main_frame.rowconfigure(0, weight=1)
        self._window.rowconfigure(0, weight=1)
        self._set_geometry(height=WINDOW_HEIGHT, width_ratio=WINDOW_WIDTH_RATIO)

    def __on_select_tree_item(self, path: str):
        pass

    def __create_new_project(self, root_name: str):
        if root_name:
            self.__state.model = Model(root_name=root_name)
            self.__callback()
            self._window.destroy()
        else:
            raise BGError('Root name cannot be empty.')

    def __on_create_new_project(self):
        AskStringWindow(self._window, self.__create_new_project, window_title='Set root name',
                        prompt_text='Enter name of the root component')

    def __open_project(self):
        try:
            open_()
            self.__callback()
            self._window.destroy()
        except JSONDecodeError as e:
            messagebox.showerror('Error', f'Error while opening the project file.\n{e}')
        except BGError as e:
            messagebox.showerror('Error', e)

