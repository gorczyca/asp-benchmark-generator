import math
from threading import Thread, Event
from tkinter import ttk, messagebox
import tkinter as tk
from typing import Optional, Callable

from exceptions import BGError
from file_operations import CSV_EXTENSION, solve
from settings import Settings
from solver import InstanceRepresentation
from state import State
from view.browse_file_path_frame import BrowseFilePathFrame
from view.abstract import HasCommonSetup, Window
from view.common import get_target_file_location, change_controls_state
from view.style import CONTROL_PAD_X, CONTROL_PAD_Y

ANSWER_SETS_FILE_SUFFIX = 'as'
EXPORT_WINDOW_TITLE = 'Export answer sets to:'


class SolveFrame(ttk.Frame,
                 HasCommonSetup):
    """Reusable frame with all logic program solving and answer set extraction related settings.

    Attributes:
        __answer_sets_count_label_string: Used to represent the target number of answer sets in the
        __answer_sets_count: Number of answer sets.
        __input_path: Input ASP encoding file path.
        __stop_event: Used to communicate with the solver thread (to terminate it from the outside).
        __solve_thread: Thread on which solving is executed.
            (Use of a Thread is necessary not to block the main, UI thread).
        __on_solving_finished: Callback function executed when solving process finishes.
        __on_stopped_callback: Callback function executed when solving process is interrupted.
    """
    def __init__(self, parent_frame,
                 settings: Settings,
                 state: State,
                 **kwargs):
        self.__state: State = state
        self.__settings: Settings = settings

        self.__answer_sets_count_label_string: str = '?'
        self.__answer_sets_count: int = 0
        self.__input_path: Optional[str] = None

        self.__stop_event: Optional[Event] = None
        self.__solve_thread: Optional[Thread] = None
        self.__on_solving_finished: Optional[Callable] = None
        self.__on_stopped_callback: Optional[Callable] = None

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
        for inst_repr in InstanceRepresentation:
            radiobutton = ttk.Radiobutton(self, value=inst_repr.value, text=inst_repr.name,
                                          variable=self.__representation_radiobuttons_var)
            self.__representation_radiobuttons.append(radiobutton)

        self.__shown_predicates_only_checkbox_var = tk.BooleanVar(value=self.__settings.shown_predicates_only)
        self.__shown_predicates_only_checkbox_label = ttk.Label(self, text='Shown predicates only:')
        self.__shown_predicates_only_checkbox = ttk.Checkbutton(self, variable=self.__shown_predicates_only_checkbox_var)

        self.__show_predicates_symbols_checkbox_var = tk.BooleanVar(value=self.__settings.shown_predicates_only)
        self.__show_predicates_symbols_checkbox_label = ttk.Label(self, text='Shown predicates only:')
        self.__show_predicates_symbols_checkbox = ttk.Checkbutton(self, variable=self.__shown_predicates_only_checkbox_var)

        root_name = '' if not self.__state.model else self.__state.model.root_name
        path, file_name = get_target_file_location(self.__state.file, root_name,
                                                   suffix=ANSWER_SETS_FILE_SUFFIX, extension=CSV_EXTENSION)
        self.__export_to_path_frame = BrowseFilePathFrame(self, path,
                                                          widget_label_text=EXPORT_WINDOW_TITLE,
                                                          title=EXPORT_WINDOW_TITLE,
                                                          default_extension=CSV_EXTENSION)

        self.__progress_label = ttk.Label(self, text='Progress:')
        self.__current_answer_set_number_label_var = tk.StringVar(value='-/-')
        self.__current_answer_set_number_label = ttk.Label(self, textvariable=self.__current_answer_set_number_label_var)

        self.__progressbar_var = tk.IntVar(value=0)
        self.__progressbar = ttk.Progressbar(self, orient=tk.HORIZONTAL, style='Horizontal.TProgressbar',
                                             variable=self.__progressbar_var)
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

    def __on_progress(self, current_answer_set_number: int) -> None:
        """Executed after generation of each answer set.
        Updates __current_answer_set_number_label and __progressbar.

        :param current_answer_set_number: Number of current answer set.
        """
        self.__current_answer_set_number_label_var.set(f'{current_answer_set_number} / {self.__answer_sets_count_label_string}')
        if self.__answer_sets_count > 0:
            self.__progressbar_var.set(current_answer_set_number)

    def solve(self, input_path: Optional[str], on_solving_finished: Optional[Callable] = None) -> None:
        """Starts the solving thread and disables widgets.

        :param input_path: Input ASP encoding file path.
        :param on_solving_finished: Callback function executed when solving process finishes.
        """
        if not input_path:
            raise BGError('Input file path is not specified.')
        elif not self.__export_to_path_frame.path:
            raise BGError('Export path is not specified.')

        self.__input_path = input_path
        self.__stop_event = Event()
        self.__on_solving_finished = on_solving_finished
        self.__solve_thread = Thread(target=self.__solve, args=(self.__stop_event,))
        self.__solve_thread.start()

        change_controls_state(tk.NORMAL, self.__stop_button)    # Enable stop button
        change_controls_state(tk.DISABLED,
                              self.__answer_sets_count_spinbox,
                              *self.__representation_radiobuttons,
                              self.__shown_predicates_only_checkbox)
        self.__export_to_path_frame.change_state(tk.DISABLED)   # Disable other widgets

    def stop_solving(self) -> None:
        """Stops the solving thread by setting the __stop_event"""
        if self.__stop_event is not None:
            self.__stop_event.set()

    def is_solving(self) -> None:
        """Returns the information whether solving is in progress."""
        return self.__solve_thread and self.__solve_thread.is_alive()

    def __stop_progressbar(self, answer_sets_count: int, complete: bool = True):
        """Stops the progressbar. Only relevant for the 'indeterminate' progressbar mode.

        :param answer_sets_count: Target number of answer sets.
        :param complete: True indicates that solving is complete; False that it has been interrupted.
        """
        if answer_sets_count == 0:
            self.__progressbar.stop()
            if complete:
                self.__progressbar.config(mode='determinate', maximum=100)  # Default maximum
                self.__progressbar_var.set(100)

    def __solve(self, stop_event: Event):
        """Starts solving. To be executed on a non-main Thread.

        :param stop_event: Used to communicate with this thread from the outside.
        """
        answer_sets_count = self.__answer_sets_count_spinbox_var.get()
        try:
            self.__answer_sets_count = answer_sets_count
            self.__progressbar_var.set(0)
            if answer_sets_count == 0:
                self.__progressbar.config(mode='indeterminate', maximum=100) # Default maximum
                self.__progressbar.start()
                self.__answer_sets_count_label_string = '?'
            else:
                self.__answer_sets_count_label_string = str(answer_sets_count)
                self.__progressbar.config(maximum=answer_sets_count)

            self.__current_answer_set_number_label_var.set(f'0 / {self.__answer_sets_count_label_string}')
            solving_complete = solve(input_path=self.__input_path,
                                     output_path=self.__export_to_path_frame.path,
                                     answer_sets_count=answer_sets_count,
                                     instance_representation=InstanceRepresentation(self.__representation_radiobuttons_var.get()),
                                     shown_predicates_only=self.__shown_predicates_only_checkbox_var.get(),
                                     show_predicates_symbols=self.__show_predicates_symbols_checkbox_var.get(),
                                     stop_event=stop_event,
                                     on_progress=self.__on_progress)

            if solving_complete:
                self.__stop_progressbar(answer_sets_count, complete=True)
                messagebox.showinfo('Solving complete', f'Answer sets exported to {self.__export_to_path_frame.path}', parent=self)
            else:
                # Solving has been interrupted
                self.__stop_progressbar(answer_sets_count, complete=False)
                messagebox.showinfo('Solving has been interrupted.', f'Part of answer sets exported to {self.__export_to_path_frame.path}',
                                    parent=self)
                if self.__on_stopped_callback is not None:
                    self.__on_stopped_callback()
        except RuntimeError as e:
            self.__progressbar.stop()
            messagebox.showerror('Error', e, parent=self)
        finally:
            if self.__on_solving_finished is not None:
                self.__on_solving_finished()
            # Restore widgets
            change_controls_state(tk.DISABLED, self.__stop_button)    # Disable stop button
            change_controls_state(tk.NORMAL,
                                  self.__answer_sets_count_spinbox,
                                  *self.__representation_radiobuttons,
                                  self.__shown_predicates_only_checkbox)
            self.__export_to_path_frame.change_state(tk.NORMAL)   # Enable other widgets

    def on_close(self, window: Window) -> None:
        """Prevents from closing the parent window of this frame, whenever solving is in progress.

        :param window: Window, prevented from closing.
        """
        if self.is_solving():
            answer = messagebox.askyesno('Stop', 'Solving is currently in progress. Are you sure you want to cancel?', parent=window)
            if answer:
                self.__on_stopped_callback = lambda: window.destroy()
                self.stop_solving()
        else:
            window.destroy()
