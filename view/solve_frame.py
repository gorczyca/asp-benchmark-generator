import math
from tkinter import ttk
import tkinter as tk

from file_operations import CSV_EXTENSION
from settings import Settings
from solver.solver import InstanceRepresentation
from state import State
from view.abstract.has_common_setup import HasCommonSetup
from view.browse_path_frame import BrowsePathFrame
from view.common import get_target_file_location
from view.style import CONTROL_PAD_X, CONTROL_PAD_Y

ANSWER_SETS_FILE_SUFFIX = 'as'


class SolveFrame(ttk.Frame,
                 HasCommonSetup):
    def __init__(self, parent_frame, settings: Settings, state: State, **kwargs):
        self.__state: State = state
        self.__settings: Settings = settings

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

        path = get_target_file_location(self.__state.file, self.__state.model.root_name,
                                        suffix=ANSWER_SETS_FILE_SUFFIX, extension=CSV_EXTENSION)
        self.__export_to_path_frame = BrowsePathFrame(self, path, widget_label_text='Export to:', default_extension=CSV_EXTENSION)

    def _setup_layout(self) -> None:
        self.__answer_sets_count_spinbox_label.grid(row=0, column=0, sticky=tk.W, pady=CONTROL_PAD_Y, padx=CONTROL_PAD_X)
        self.__answer_sets_count_spinbox.grid(row=0, column=1, columnspan=3, sticky=tk.EW, pady=CONTROL_PAD_Y, padx=CONTROL_PAD_X)

        self.__representation_radiobuttons_label.grid(row=1, column=0, sticky=tk.W, pady=CONTROL_PAD_Y, padx=CONTROL_PAD_X)
        for i, radiobutton in enumerate(self.__representation_radiobuttons):
            radiobutton.grid(row=1, column=i+1, sticky=tk.EW, pady=CONTROL_PAD_Y, padx=CONTROL_PAD_X)

        self.__shown_predicates_only_checkbox_label.grid(row=2, column=0, sticky=tk.W, pady=CONTROL_PAD_Y, padx=CONTROL_PAD_X)
        self.__shown_predicates_only_checkbox.grid(row=2, column=1, columnspan=3, sticky=tk.E, pady=CONTROL_PAD_Y, padx=CONTROL_PAD_X)

        self.__export_to_path_frame.grid(row=3, column=0, columnspan=4, sticky=tk.NSEW)

        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        self.columnconfigure(2, weight=1)
        self.columnconfigure(3, weight=1)
