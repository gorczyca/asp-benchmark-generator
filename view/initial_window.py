import tkinter as tk
from json import JSONDecodeError
from tkinter import ttk, messagebox, filedialog

from exceptions import BGError
from file_operations import open_, solve, load_from_file, JSON_EXTENSION
from model.model import Model
from settings import Settings
from state import State
from view.ask_string_window import AskStringWindow
from view.scrollbars_listbox import ScrollbarListbox
from view.style import CONTROL_PAD_Y, FRAME_PAD_X, FRAME_PAD_Y
from view.abstract.has_common_setup import HasCommonSetup
from view.abstract.window import Window
from file_operations import extract_file_name
from project_info import PROJECT_NAME, PROJECT_DESCRIPTION, PROJECT_VERSION

WINDOW_TITLE = 'Welcome to the Benchmark Generator'

TREEVIEW_HEADING = 'Recently opened projects'
VERSION_STRING = 'version'

WINDOW_WIDTH_RATIO = 0.5
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
        self.__main_frame = ttk.Frame(self._window)
        self.__labels_frame = ttk.Frame(self.__main_frame)
        self.__main_label = ttk.Label(self.__labels_frame, text=PROJECT_NAME, anchor=tk.CENTER, style='Big.TLabel')
        self.__secondary_label = ttk.Label(self.__labels_frame, text=PROJECT_DESCRIPTION, anchor=tk.CENTER)
        self.__version_label = ttk.Label(self.__labels_frame, text=f'{VERSION_STRING} {PROJECT_VERSION}',
                                         style='Small.TLabel', anchor=tk.CENTER)

        self.__create_new_project_button = ttk.Button(self.__main_frame, text='Create new project',
                                                      command=self.__on_create_new_project)
        self.__open_project_button = ttk.Button(self.__main_frame, text='Open project',
                                                command=self.__on_open_project)
        self.__solve_button = ttk.Button(self.__main_frame, text='Solve...', command=solve)

        if self.__recent_projects:
            self.__recent_projects_listbox = ScrollbarListbox(self._window,
                                                              on_select_callback=self.__on_select_recent_project,
                                                              heading=TREEVIEW_HEADING,
                                                              extract_id=lambda x: self.__state.settings.recently_opened_projects.index(x),
                                                              extract_text=lambda x: f'{x.root_name} '
                                                                                     f'(~/{extract_file_name(x.path)})',
                                                              values=self.__state.settings.recently_opened_projects,
                                                              scrollbars=False)

    def _setup_layout(self) -> None:
        self.__labels_frame.grid(row=0, sticky=tk.NSEW)
        self.__main_label.grid(row=0, sticky=tk.EW + tk.S, pady=CONTROL_PAD_Y)
        self.__secondary_label.grid(row=1, sticky=tk.EW, pady=CONTROL_PAD_Y)
        self.__version_label.grid(row=2, sticky=tk.EW + tk.N, pady=CONTROL_PAD_Y)

        self.__labels_frame.rowconfigure(0, weight=1)
        self.__labels_frame.rowconfigure(2, weight=1)
        self.__labels_frame.columnconfigure(0, weight=1)

        self.__create_new_project_button.grid(row=1, sticky=tk.EW, pady=CONTROL_PAD_Y)
        self.__open_project_button.grid(row=2, sticky=tk.EW, pady=CONTROL_PAD_Y)
        self.__solve_button.grid(row=3, sticky=tk.EW, pady=CONTROL_PAD_Y)

        if self.__recent_projects:
            self.__recent_projects_listbox.grid(row=0, column=0, sticky=tk.NSEW, pady=FRAME_PAD_Y, padx=FRAME_PAD_X)
            self.__main_frame.grid(row=0, column=1, sticky=tk.NSEW, pady=FRAME_PAD_Y, padx=FRAME_PAD_X)

            self._window.columnconfigure(0, weight=1)
            self._window.columnconfigure(1, weight=1)
        else:
            self.__main_frame.grid(row=0, column=0, sticky=tk.NSEW, pady=FRAME_PAD_Y, padx=FRAME_PAD_X)
            self._window.columnconfigure(0, weight=1)

        self.__main_frame.rowconfigure(0, weight=1)
        self.__main_frame.columnconfigure(0, weight=1)
        self._window.rowconfigure(0, weight=1)
        self._set_geometry(height=WINDOW_HEIGHT, width_ratio=WINDOW_WIDTH_RATIO)

    def __on_select_recent_project(self, project_index: int):
        try:
            project_info = self.__state.settings.recently_opened_projects[project_index]
            with open(project_info.path, 'r') as file:
                self.__open_project(file)
        except FileNotFoundError as e:
            messagebox.showerror('File not found', e)

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

    def __on_open_project(self):
        file = filedialog.askopenfile(mode='r', defaultextension=JSON_EXTENSION)
        self.__open_project(file)

    def __open_project(self, file):
        try:
            load_from_file(file)
            self.__callback()
            self._window.destroy()
        except JSONDecodeError as e:
            messagebox.showerror('Error', f'Error while opening the project file.\n{e}')
        except BGError as e:
            messagebox.showerror('Error', e)
