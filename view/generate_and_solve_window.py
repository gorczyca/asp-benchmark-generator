import tkinter as tk
from tkinter import ttk, messagebox

from exceptions import BGError
from file_operations import generate
from settings import Settings
from state import State
from view.generate_frame import GenerateFrame
from view.solve_frame import SolveFrame
from view.abstract import HasCommonSetup, Window
from view.common import change_controls_state
from view.style import FRAME_PAD_X, FRAME_PAD_Y, CONTROL_PAD_Y, CONTROL_PAD_X

WINDOW_TITLE = 'Generate logic program...'

GENERATED_FILE_SUFFIX = 'gen'

WINDOW_WIDTH_RATIO = 0.3
WINDOW_HEIGHT_RATIO = 0.675


class GenerateAndSolveWindow(HasCommonSetup,
                             Window):
    """Used for both: logic program file generation and solving."""
    def __init__(self,
                 parent_frame: ttk.Frame):
        self.__state = State()
        self.__settings = Settings.get_settings()

        Window.__init__(self, parent_frame, WINDOW_TITLE)
        HasCommonSetup.__init__(self)

        # Prevent from closing parent window when solving is in progress
        self.protocol('WM_DELETE_WINDOW', lambda: self.__solve_frame.on_close(self))

    def _create_widgets(self) -> None:
        self.__main_frame = ttk.Frame(self)
        self.__generate_frame = GenerateFrame(self.__main_frame, self.__settings, self.__state)
        self.__solve_frame = SolveFrame(self.__main_frame, self.__settings, self.__state)

        self.__ok_button = ttk.Button(self.__main_frame, text='Ok', command=self.__ok)
        self.__cancel_button = ttk.Button(self.__main_frame, text='Cancel', command=self.destroy)

    def _setup_layout(self) -> None:
        self._set_geometry(height_ratio=WINDOW_HEIGHT_RATIO, width_ratio=WINDOW_WIDTH_RATIO)

        self.__main_frame.grid(row=0, column=0, sticky=tk.NSEW, padx=FRAME_PAD_X, pady=FRAME_PAD_Y)
        self.__generate_frame.grid(row=0, column=0, columnspan=2, sticky=tk.NSEW)
        self.__solve_frame.grid(row=1, column=0, columnspan=2, sticky=tk.NSEW)

        self.__ok_button.grid(row=2, column=0, sticky=tk.EW, pady=CONTROL_PAD_Y, padx=(0, CONTROL_PAD_X))
        self.__cancel_button.grid(row=2, column=1, sticky=tk.EW, pady=CONTROL_PAD_Y, padx=(CONTROL_PAD_X, 0))

        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)

        self.__main_frame.rowconfigure(1, weight=1)
        self.__main_frame.columnconfigure(0, weight=1)
        self.__main_frame.columnconfigure(1, weight=1)

    def __change_window_controls_state(self, state: str) -> None:
        """Changes widgets' state.

        :param state: Desired state of the widgets (tk.NORMAL or tk.DISABLED).
        """
        self.__generate_frame.change_frame_controls_state(state)
        change_controls_state(state, self.__ok_button, self.__cancel_button)

    def __ok(self) -> None:
        """Executed whenever __ok_button is pressed."""
        try:
            generate(self.__generate_frame.export_to_path, self.__state.model,
                     self.__generate_frame.show_all_predicates, self.__generate_frame.shown_predicates_dict)
            self.__solve_frame.solve(self.__generate_frame.export_to_path,
                                     on_solving_finished=lambda: self.__change_window_controls_state(tk.NORMAL))
            self.__change_window_controls_state(tk.DISABLED)
        except BGError as e:
            messagebox.showerror('Error', e.message, parent=self)





