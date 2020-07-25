import tkinter as tk
from tkinter import ttk, simpledialog, filedialog

from state import State
from view.style import CONTROL_PAD_Y, FRAME_PAD_X
from view.abstract.has_common_setup import HasCommonSetup
from view.abstract.window import Window

WINDOW_TITLE = 'Welcome'

WINDOW_WIDTH_RATIO = 0.25
WINDOW_HEIGHT = 100


class InitialWindow(HasCommonSetup,
                    Window):
    def __init__(self, parent_frame, callback):
        self.__state = State()
        self.__callback = callback

        Window.__init__(self, parent_frame, WINDOW_TITLE)
        HasCommonSetup.__init__(self)

    def _create_widgets(self) -> None:
        self.__create_new_project_button = ttk.Button(self._window, text='Create new project',
                                                      command=self.__create_new_project)
        self.__open_project_button = ttk.Button(self._window, text='Open project',
                                                command=self.__open_project)
        self.__solve_button = ttk.Button(self._window, text='Solve...', command=self.__solve)

    def _setup_layout(self) -> None:
        self.__create_new_project_button.grid(row=0, sticky=tk.EW, pady=CONTROL_PAD_Y, padx=FRAME_PAD_X)
        self.__open_project_button.grid(row=1, sticky=tk.EW, pady=CONTROL_PAD_Y, padx=FRAME_PAD_X)
        self.__solve_button.grid(row=2, sticky=tk.EW, pady=CONTROL_PAD_Y, padx=FRAME_PAD_X)

        self._window.columnconfigure(0, weight=1)

        self._window.rowconfigure(0, weight=1)
        self._window.rowconfigure(1, weight=1)
        self._window.rowconfigure(2, weight=1)

        self._set_geometry(height=WINDOW_HEIGHT, width_ratio=WINDOW_WIDTH_RATIO)

    def __create_new_project(self):
        root_name = simpledialog.askstring('Set root name', 'Enter name of the root component')
        if root_name:
            self.__callback()
            self._window.destroy()

    def __open_project(self):
        # TODO: don't repeat yourself (same is in the menu)
        file = filedialog.askopenfile(mode='r', defaultextension=JSON_EXTENSION)
        if file:
            self.__state.file = file
            json = file.read()
            model = json_converter.json_to_model(json)
            self.__state.model = model
            file_name = Menu.__extract_file_name(file.name)
            pub.sendMessage(actions.MODEL_SAVED, file_name=file_name)
            pub.sendMessage(actions.MODEL_LOADED)

    def __solve(self):
        pass

