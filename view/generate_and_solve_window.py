import tkinter as tk
from tkinter import ttk, messagebox

from code_generator.code_generator import generate_code
from file_operations import extract_file_name, solve_
from settings import Settings
from state import State
from view.abstract.has_common_setup import HasCommonSetup
from view.abstract.window import Window
from view.generate_frame import GenerateFrame
from view.solve_frame import SolveFrame
from view.style import FRAME_PAD_X, FRAME_PAD_Y, CONTROL_PAD_Y, CONTROL_PAD_X

WINDOW_TITLE = 'Generate logic program...'

GENERATED_FILE_SUFFIX = 'gen'

WINDOW_WIDTH_RATIO = 0.3
WINDOW_HEIGHT_RATIO = 0.6


class GenerateAndSolveWindow(HasCommonSetup,
                             Window):
    def __init__(self, parent_frame, callback):
        self.__state = State()
        self.__callback = callback
        self.__settings = Settings.get_settings()

        Window.__init__(self, parent_frame, WINDOW_TITLE)
        HasCommonSetup.__init__(self)

    def _create_widgets(self) -> None:
        self.__main_frame = ttk.Frame(self._window)
        self.__generate_frame = GenerateFrame(self.__main_frame, self.__settings, self.__state)
        self.__solve_frame = SolveFrame(self.__main_frame, self.__settings, self.__state)

        self.__ok_button = ttk.Button(self.__main_frame, text='Ok', command=self.__ok)
        self.__cancel_button = ttk.Button(self.__main_frame, text='Cancel', command=self._window.destroy)

    def _setup_layout(self) -> None:
        self._set_geometry(height_ratio=WINDOW_HEIGHT_RATIO, width_ratio=WINDOW_WIDTH_RATIO)

        self.__main_frame.grid(row=0, column=0, sticky=tk.NSEW, padx=FRAME_PAD_X, pady=FRAME_PAD_Y)
        self.__generate_frame.grid(row=0, column=0, columnspan=2, sticky=tk.NSEW)
        self.__solve_frame.grid(row=1, column=0, columnspan=2, sticky=tk.NSEW)

        self.__ok_button.grid(row=2, column=0, sticky=tk.EW, pady=CONTROL_PAD_Y, padx=(0, CONTROL_PAD_X))
        self.__cancel_button.grid(row=2, column=1, sticky=tk.EW, pady=CONTROL_PAD_Y, padx=(CONTROL_PAD_X, 0))

        self._window.rowconfigure(0, weight=1)
        self._window.columnconfigure(0, weight=1)

        self.__main_frame.rowconfigure(1, weight=1)
        self.__main_frame.columnconfigure(0, weight=1)
        self.__main_frame.columnconfigure(1, weight=1)

    def __ok(self):
        # TODO: 1: bugs & messy
        # TODO: 2: DRY
        export_program_to_path = self.__generate_frame.export_to_path
        code = generate_code(self.__state.model, self.__generate_frame.shown_predicates_dict)
        with open(export_program_to_path, 'w') as output_file:
            output_file.write(code)
            output_file.close()
            file_name = extract_file_name(export_program_to_path)
            # messagebox.showinfo('Export successful.', f'Exported successfully to\n{file_name}.', parent=self._window)
            # TODO:
            self.__settings.save_changes(shown_predicates_dict=self.__generate_frame.shown_predicates_dict)
            self.__solve_frame.set_progressbar_max()
            solve_(self._window,
                   input_path=export_program_to_path,
                   output_path=self.__solve_frame.export_path,
                   answer_sets_count=self.__solve_frame.answer_sets_count,
                   instance_representation=self.__solve_frame.instance_representation,
                   shown_predicates_only=self.__solve_frame.shown_predicates_only,
                   show_predicates_symbols=self.__solve_frame.show_predicates_symbols,
                   settings=self.__settings,
                   on_progress=lambda progress: self.__solve_frame.set_progressbar_value(progress))





