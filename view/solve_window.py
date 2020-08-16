import tkinter as tk
from multiprocessing import Process
from tkinter import ttk, messagebox
from threading import Thread

from file_operations import LP_EXTENSION, solve_
from settings import Settings
from state import State
from view.abstract.has_common_setup import HasCommonSetup
from view.abstract.window import Window
from view.browse_file_path_frame import BrowseFilePathFrame
from view.solve_frame import SolveFrame
from view.style import FRAME_PAD_X, FRAME_PAD_Y, CONTROL_PAD_Y, CONTROL_PAD_X

WINDOW_TITLE = 'Solve a logic program...'

ANSWER_SETS_FILE_SUFFIX = 'as'

WINDOW_WIDTH_RATIO = 0.3
WINDOW_HEIGHT_RATIO = 0.4


class SolveWindow(HasCommonSetup,
                  Window):
    def __init__(self, parent_frame, callback):
        self.__state = State()
        self.__callback = callback
        self.__settings = Settings.get_settings()

        Window.__init__(self, parent_frame, WINDOW_TITLE)
        HasCommonSetup.__init__(self)

        self._window.protocol('WM_DELETE_WINDOW', self.__on_close)

    def _create_widgets(self) -> None:
        self.__main_frame = ttk.Frame(self._window)
        self.__solve_file_path_frame = BrowseFilePathFrame(self.__main_frame,
                                                           path=self.__settings.program_to_solve_path,
                                                           widget_label_text='Select logic program',
                                                           default_extension=LP_EXTENSION,
                                                           save=False)
        self.__solve_frame = SolveFrame(self.__main_frame, self.__settings, self.__state)
        self.__ok_button = ttk.Button(self.__main_frame, text='Ok', command=self.__ok)
        self.__cancel_button = ttk.Button(self.__main_frame, text='Cancel', command=self._window.destroy)

    def _setup_layout(self) -> None:
        self._set_geometry(height_ratio=WINDOW_HEIGHT_RATIO, width_ratio=WINDOW_WIDTH_RATIO)

        self.__main_frame.grid(row=0, column=0, sticky=tk.NSEW, padx=FRAME_PAD_X, pady=FRAME_PAD_Y)

        self.__solve_file_path_frame.grid(row=0, column=0, columnspan=2, sticky=tk.NSEW)

        self.__solve_frame.grid(row=1, column=0, columnspan=2, sticky=tk.NSEW, pady=CONTROL_PAD_Y)
        self.__ok_button.grid(row=2, column=0, sticky=tk.EW, pady=CONTROL_PAD_Y, padx=(0, CONTROL_PAD_X))
        self.__cancel_button.grid(row=2, column=1, sticky=tk.EW, pady=CONTROL_PAD_Y, padx=(CONTROL_PAD_X, 0))

        self.__main_frame.rowconfigure(1, weight=1)
        self.__main_frame.columnconfigure(0, weight=1)
        self.__main_frame.columnconfigure(1, weight=1)

        self._window.rowconfigure(0, weight=1)
        self._window.columnconfigure(0, weight=1)

    def __ok(self):
        self.__solve_frame.solve(self.__solve_file_path_frame.path)

    def __on_close(self):
        if self.__solve_frame.is_solving():
            answer = messagebox.askyesno('Stop', 'Solving is currently in process. Are you sure you want to cancel?', parent=self._window)
            if answer:
                self.__solve_frame.stop_solving()
        else:
            self._window.destroy()


