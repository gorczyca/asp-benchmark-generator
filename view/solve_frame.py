import math
from threading import Thread, Event
from tkinter import ttk, messagebox
import tkinter as tk

from file_operations import CSV_EXTENSION, solve_
from settings import Settings
from solver.solver import InstanceRepresentation
from state import State
from view.abstract.has_common_setup import HasCommonSetup
from view.browse_file_path_frame import BrowseFilePathFrame
from view.common import get_target_file_location, change_controls_state
from view.style import CONTROL_PAD_X, CONTROL_PAD_Y

ANSWER_SETS_FILE_SUFFIX = 'as'


class SolveFrame(ttk.Frame,
                 HasCommonSetup):
    def __init__(self, parent_frame, settings: Settings, state: State, **kwargs):
        self.__state: State = state
        self.__settings: Settings = settings
        self.__parent_frame = parent_frame

        self.__answer_sets_count_label_string: str = '?'
        self.__answer_sets_count = 0
        self.__input_path = None

        self.__stop_event = None
        self.__solve_thread = None
        self.__on_solved_callback = None
        self.__on_stopped_callback = None

        ttk.Frame.__init__(self, parent_frame, **kwargs)
        HasCommonSetup.__init__(self)

    def _create_widgets(self) -> None:
        self.__answer_sets_count_spinbox_label = ttk.Label(self, text='Answer sets count:')
        self.__answer_sets_count_spinbox_var = tk.IntVar(value=self.__settings.answer_sets_count)
        self.__answer_sets_count_spinbox = ttk.Spinbox(self, from_=0, to=math.inf,
                                                       textvariable=self.__answer_sets_count_spinbox_var)

        self.__representation_radiobuttons_label = ttk.Label(self, text='Instance representation:')
        self.__representation_radiobuttons_var = tk.IntVar(value=self.__settings.instance_representation.value)
        self.__representation_radiobuttons = []
        for Repr in InstanceRepresentation:
            radiobutton = ttk.Radiobutton(self, value=Repr.value, text=Repr.name,
                                          variable=self.__representation_radiobuttons_var)
            self.__representation_radiobuttons.append(radiobutton)

        self.__shown_predicates_only_checkbox_var = tk.BooleanVar(value=self.__settings.shown_predicates_only)
        self.__shown_predicates_only_checkbox_label = ttk.Label(self, text='Shown predicates only:')
        self.__shown_predicates_only_checkbox = ttk.Checkbutton(self, variable=self.__shown_predicates_only_checkbox_var)

        self.__show_predicates_symbols_checkbox_var = tk.BooleanVar(value=self.__settings.shown_predicates_only)
        self.__show_predicates_symbols_checkbox_label = ttk.Label(self, text='Shown predicates only:')
        self.__show_predicates_symbols_checkbox = ttk.Checkbutton(self, variable=self.__shown_predicates_only_checkbox_var)

        path = get_target_file_location(self.__state.file, self.__state.model.root_name,
                                        suffix=ANSWER_SETS_FILE_SUFFIX, extension=CSV_EXTENSION)
        self.__export_to_path_frame = BrowseFilePathFrame(self, path, widget_label_text='Export answer sets to:',
                                                          default_extension=CSV_EXTENSION)

        self.__progress_label = ttk.Label(self, text='Progress:')
        self.__current_answer_set_number_label_var = tk.StringVar(value='-/-')
        self.__current_answer_set_number_label = ttk.Label(self, textvariable=self.__current_answer_set_number_label_var)

        self.__progressbar_var = tk.IntVar(value=0)
        self.__progressbar = ttk.Progressbar(self, orient=tk.HORIZONTAL, style='Horizontal.TProgressbar', variable=self.__progressbar_var)
        self.__stop_button = ttk.Button(self, text='Stop', state=tk.DISABLED, command=self.stop_solving)

    def _setup_layout(self) -> None:
        self.__answer_sets_count_spinbox_label.grid(row=0, column=0, sticky=tk.W, pady=CONTROL_PAD_Y, padx=CONTROL_PAD_X)
        self.__answer_sets_count_spinbox.grid(row=0, column=1, columnspan=3, sticky=tk.EW, pady=CONTROL_PAD_Y, padx=CONTROL_PAD_X)

        self.__representation_radiobuttons_label.grid(row=1, column=0, sticky=tk.W, pady=CONTROL_PAD_Y, padx=CONTROL_PAD_X)
        for i, radiobutton in enumerate(self.__representation_radiobuttons):
            radiobutton.grid(row=1, column=i+1, sticky=tk.EW, pady=CONTROL_PAD_Y, padx=CONTROL_PAD_X)

        self.__shown_predicates_only_checkbox_label.grid(row=2, column=0, sticky=tk.W, pady=CONTROL_PAD_Y, padx=CONTROL_PAD_X)
        self.__shown_predicates_only_checkbox.grid(row=2, column=1, columnspan=3, sticky=tk.E, pady=CONTROL_PAD_Y, padx=CONTROL_PAD_X)

        self.__export_to_path_frame.grid(row=3, column=0, columnspan=4, sticky=tk.NSEW)
        self.__progress_label.grid(row=4, column=0, sticky=tk.W, pady=CONTROL_PAD_Y, padx=CONTROL_PAD_X)
        self.__current_answer_set_number_label.grid(row=4, column=1, columnspan=3, sticky=tk.E, pady=CONTROL_PAD_Y, padx=CONTROL_PAD_X)
        self.__progressbar.grid(row=5, column=0, columnspan=3, sticky=tk.NSEW, pady=CONTROL_PAD_Y, padx=CONTROL_PAD_X)
        self.__stop_button.grid(row=5, column=3, sticky=tk.NSEW, pady=CONTROL_PAD_Y, padx=CONTROL_PAD_X)

        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        self.columnconfigure(2, weight=1)
        self.columnconfigure(3, weight=1)

    def __on_progress(self, current_answer_set_number: int):
        self.__current_answer_set_number_label_var.set(f'{current_answer_set_number} / {self.__answer_sets_count_label_string}')
        if self.__answer_sets_count > 0:
            self.__progressbar_var.set(current_answer_set_number)

    def solve(self, input_path: str, on_solved=None):
        self.__input_path = input_path
        self.__stop_event = Event()
        self.__on_solved_callback = on_solved
        self.__solve_thread = Thread(target=self.__solve, args=(self.__stop_event,))
        self.__solve_thread.start()

        change_controls_state(tk.NORMAL, self.__stop_button)    # Enable stop button
        change_controls_state(tk.DISABLED,
                              self.__answer_sets_count_spinbox,
                              *self.__representation_radiobuttons,
                              self.__shown_predicates_only_checkbox)
        self.__export_to_path_frame.change_state(tk.DISABLED)   # Disable other widgets

    def stop_solving(self):
        if self.__stop_event is not None:
            self.__stop_event.set()

    def is_solving(self):
        return self.__solve_thread and self.__solve_thread.is_alive()

    def __solve(self, stop_event: Event):
        # TODO: DRY
        answer_sets_count = self.__answer_sets_count_spinbox_var.get()
        self.__answer_sets_count = answer_sets_count
        self.__progressbar_var.set(0)
        if answer_sets_count == 0:
            self.__progressbar.config(mode='indeterminate')
            self.__progressbar.start()
        else:
            self.__answer_sets_count_label_string = str(answer_sets_count)
            self.__progressbar.config(maximum=answer_sets_count)

        self.__current_answer_set_number_label_var.set(f'0 / {self.__answer_sets_count_label_string}')
        solve_(self,
               input_path=self.__input_path,
               output_path=self.__export_to_path_frame.path,
               answer_sets_count=answer_sets_count,
               instance_representation=InstanceRepresentation(self.__representation_radiobuttons_var.get()),
               shown_predicates_only=self.__shown_predicates_only_checkbox_var.get(),
               show_predicates_symbols=self.__show_predicates_symbols_checkbox_var.get(),
               settings=self.__settings,
               stop_event=stop_event,
               on_progress=self.__on_progress)

        if self.__on_stopped_callback is not None:
            self.__on_stopped_callback()
            return

        if self.__on_solved_callback is not None:
            self.__on_solved_callback()

        if answer_sets_count == 0:
            self.__progressbar.stop()

        change_controls_state(tk.DISABLED, self.__stop_button)    # Disable stop button
        change_controls_state(tk.NORMAL,
                              self.__answer_sets_count_spinbox,
                              *self.__representation_radiobuttons,
                              self.__shown_predicates_only_checkbox)
        self.__export_to_path_frame.change_state(tk.NORMAL)   # Enable other widgets

        messagebox.showinfo('Solving complete', f'Answer set exported to {self.__export_to_path_frame.path}', parent=self)

    def on_close(self, window):
        if self.is_solving():
            answer = messagebox.askyesno('Stop', 'Solving is currently in process. Are you sure you want to cancel?', parent=window)
            if answer:
                self.__on_stopped_callback = lambda: window.destroy()
                self.stop_solving()
        else:
            window.destroy()





