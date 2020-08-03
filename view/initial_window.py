import tkinter as tk
from json import JSONDecodeError
from tkinter import ttk, messagebox

from exceptions import BGError
from file_operations import open_, solve
from state import State
from view.ask_string_window import AskStringWindow
from view.style import CONTROL_PAD_Y, FRAME_PAD_X, FRAME_PAD_Y
from view.abstract.has_common_setup import HasCommonSetup
from view.abstract.window import Window

WINDOW_TITLE = 'Welcome'
WELCOME_TEXT = "Welcome to Benchmark Generator for configuration's problem ASP encodings."

WINDOW_WIDTH_RATIO = 0.4
WINDOW_HEIGHT = 300


class InitialWindow(HasCommonSetup,
                    Window):
    def __init__(self, parent_frame, callback):
        self.__state = State()
        self.__callback = callback

        Window.__init__(self, parent_frame, WINDOW_TITLE)
        HasCommonSetup.__init__(self)

    def _create_widgets(self) -> None:
        self.__welcome_label = ttk.Label(self._window, text=WELCOME_TEXT, anchor=tk.W)
        self.__create_new_project_button = ttk.Button(self._window, text='Create new project',
                                                      command=self.__on_create_new_project)
        self.__open_project_button = ttk.Button(self._window, text='Open project',
                                                command=self.__open_project)
        self.__solve_button = ttk.Button(self._window, text='Solve...', command=solve)

    def _setup_layout(self) -> None:
        self.__welcome_label.grid(row=0, sticky=tk.NSEW, pady=(FRAME_PAD_Y, CONTROL_PAD_Y), padx=FRAME_PAD_X)
        self.__create_new_project_button.grid(row=1, sticky=tk.EW, pady=CONTROL_PAD_Y, padx=FRAME_PAD_X)
        self.__open_project_button.grid(row=2, sticky=tk.EW, pady=CONTROL_PAD_Y, padx=FRAME_PAD_X)
        self.__solve_button.grid(row=3, sticky=tk.EW, pady=(CONTROL_PAD_Y, FRAME_PAD_Y), padx=FRAME_PAD_X)

        self._window.columnconfigure(0, weight=1)
        self._window.rowconfigure(0, weight=1)

        self._set_geometry(height=WINDOW_HEIGHT, width_ratio=WINDOW_WIDTH_RATIO)

    def __create_new_project(self, root_name: str):
        if root_name:
            self.__state.model.root_name = root_name
            self.__callback()
            self._window.destroy()
        else:
            raise BGError('Root name cannot be empty.')

    def __on_create_new_project(self):
        AskStringWindow(self._window, self.__create_new_project, window_title='Set root name',
                        prompt_text='Enter name of the root component')

    def __open_project(self):
        try:
            open_(self._window)
            self.__callback()
            self._window.destroy()
        except JSONDecodeError as e:
            messagebox.showerror('Error', f'Error while opening the project file.\n{e}')
        except BGError as e:
            messagebox.showerror('Error', e)

