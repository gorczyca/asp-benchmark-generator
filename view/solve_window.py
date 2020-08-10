import math
import os
import tkinter as tk
from tkinter import ttk, filedialog

from settings import Settings
from solver.solver import InstanceRepresentation
from state import State
from view.abstract.has_common_setup import HasCommonSetup
from view.abstract.window import Window
from file_operations import CSV_EXTENSION

WINDOW_TITLE = 'Solve a logic program...'

ANSWER_SETS_FILE_SUFFIX = 'as'

WINDOW_WIDTH_RATIO = 0.4
WINDOW_HEIGHT_RATIO = 0.8


class SolveWindow(HasCommonSetup,
                  Window):
    def __init__(self, parent_frame, callback):
        self.__state = State()
        self.__callback = callback
        self.__settings = Settings.get_settings()

        Window.__init__(self, parent_frame, WINDOW_TITLE)
        HasCommonSetup.__init__(self)

    def _create_widgets(self) -> None:
        self.__answer_sets_count_spinbox_label = ttk.Label(self._window, text='Answer sets count:')
        self.__answer_sets_count_spinbox_var = tk.IntVar(value=self.__settings.answer_sets_count)
        self.__answer_sets_count_spinbox = ttk.Spinbox(self._window, from_=0, to=math.inf,
                                                       textvariable=self.__answer_sets_count_spinbox_var)

        self.__representation_radiobuttons_var = tk.IntVar(value=self.__settings.instance_representation.value)
        self.__representation_radiobuttons = []
        for Repr in InstanceRepresentation:
            radiobutton = ttk.Radiobutton(self._window, value=Repr.value, text=Repr.name,
                                          variable=self.__representation_radiobuttons_var)
            self.__representation_radiobuttons.append(radiobutton)

        self.__shown_predicates_only_checkbox_var = tk.BooleanVar(value=self.__settings.shown_predicates_only)
        self.__shown_predicates_only_checkbox_label = ttk.Label(self._window, text='Shown predicates only:')
        self.__shown_predicates_only_checkbox = ttk.Checkbutton(self._window,
                                                                variable=self.__shown_predicates_only_checkbox_var)

        self.__generate_to_label = ttk.Label(self._window, text='Save to:')
        self.__browse_file_button = ttk.Button(self._window, text='Browse...', command=self.__on_browse_path)
        self.__generate_to_path_label_var = tk.StringVar(value='Set target location.')
        self.__generate_to_path_label = ttk.Label(self._window, textvariable=self.__generate_to_path_label_var)

        if self.__state.file is not None:
            root_name = self.__state.model.root_name
            dir_name = os.path.dirname(self.__state.file.name)
            path = os.path.join(dir_name, f'{root_name}_{ANSWER_SETS_FILE_SUFFIX}{CSV_EXTENSION}')
            path = os.path.normpath(path)   # Normalize the back- & front-slashes
            self.__generate_to_path_label_var.set(path)

    def _setup_layout(self) -> None:
        self.__answer_sets_count_spinbox_label.grid(row=0, column=0)
        self.__answer_sets_count_spinbox.grid(row=0, column=1, sticky=tk.NSEW)

        for i, radiobutton in enumerate(self.__representation_radiobuttons):
            radiobutton.grid(row=1, column=i*2)

        self.__shown_predicates_only_checkbox_label.grid(row=2, column=0)
        self.__shown_predicates_only_checkbox.grid(row=2, column=1)

        self.__generate_to_label.grid(row=3, column=0)
        self.__generate_to_path_label.grid(row=4, column=0)
        self.__browse_file_button.grid(row=4, column=1)

    def __on_browse_path(self):
        # TODO:
        # filename = tkFileDialog.asksaveasfilename(defaultextension=".espace",
        #                                           filetypes=(("espace file", "*.espace"), ("All Files", "*.*")))
        file_path = filedialog.asksaveasfilename(defaultextension=CSV_EXTENSION, parent=self._window)
        if file_path:
            file_path = os.path.normpath(file_path)
            self.__generate_to_path_label_var.set(file_path)







