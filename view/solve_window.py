import tkinter as tk
from tkinter import ttk, messagebox

from exceptions import BGError
from file_operations import LP_EXTENSION
from settings import Settings
from state import State
from view import BrowseFilePathFrame, SolveFrame
from view.abstract import HasCommonSetup, Window
from view.common import change_controls_state
from view.style import FRAME_PAD_X, FRAME_PAD_Y, CONTROL_PAD_Y, CONTROL_PAD_X

WINDOW_TITLE = 'Solve a logic program...'
SELECT_FILE_TITLE = 'Select logic program file:'

ANSWER_SETS_FILE_SUFFIX = 'as'

WINDOW_WIDTH_RATIO = 0.3
WINDOW_HEIGHT_RATIO = 0.4


class SolveWindow(HasCommonSetup,
                  Window):
    def __init__(self, parent_frame):
        self.__state = State()
        self.__settings = Settings.get_settings()

        Window.__init__(self, parent_frame, WINDOW_TITLE)
        HasCommonSetup.__init__(self)

        self.protocol('WM_DELETE_WINDOW', lambda: self.__solve_frame.on_close(self))

    def _create_widgets(self) -> None:
        self.__main_frame = ttk.Frame(self)
        self.__solve_file_path_frame = BrowseFilePathFrame(self.__main_frame,
                                                           path=self.__settings.program_to_solve_path,
                                                           widget_label_text='Select logic program',
                                                           title=SELECT_FILE_TITLE,
                                                           default_extension=LP_EXTENSION,
                                                           save=False)
        self.__solve_frame = SolveFrame(self.__main_frame, self.__settings, self.__state)
        self.__ok_button = ttk.Button(self.__main_frame, text='Ok', command=self.__ok)
        self.__cancel_button = ttk.Button(self.__main_frame, text='Cancel', command=self.destroy)

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

        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)

    def __ok(self):
        try:
            self.__solve_frame.solve(self.__solve_file_path_frame.path,
                                     on_solved=lambda: self.__change_window_controls_state(tk.NORMAL))
            self.__change_window_controls_state(tk.DISABLED)
        except BGError as e:
            messagebox.showerror('Error', e.message, parent=self)

    def __change_window_controls_state(self, state):
        change_controls_state(state,
                              self.__ok_button,
                              self.__cancel_button)
        self.__solve_file_path_frame.change_state(state)

