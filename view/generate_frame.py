import os
from tkinter import ttk
import tkinter as tk

from code_generator.code_generator import SYMBOLS_WITH_ARITIES, INSTANCES_FACTS
from file_operations import LP_EXTENSION
from settings import Settings
from state import State
from view.abstract.has_common_setup import HasCommonSetup
from view.browse_file_path_frame import BrowseFilePathFrame
from view.common import get_target_file_location
from view.style import BACKGROUND_COLOR_PRIMARY, CONTROL_PAD_Y, CONTROL_PAD_X

GENERATED_FILE_SUFFIX = 'gen'
SHOW_PREDICATES_CONTAINER_FRAME_HEIGHT = 200


class GenerateFrame(ttk.Frame,
                    HasCommonSetup):
    def __init__(self, parent_frame, settings: Settings, state: State, **kwargs):
        self.__state: State = state
        self.__settings: Settings = settings

        ttk.Frame.__init__(self, parent_frame, **kwargs)
        HasCommonSetup.__init__(self)

    def _create_widgets(self) -> None:
        self.__show_predicates_label = ttk.Label(self, text='Show predicates:')
        self.__show_predicates_container_frame = ttk.Frame(self, relief=tk.SOLID, borderwidth=1)
        self.__show_predicates_canvas = tk.Canvas(self.__show_predicates_container_frame,
                                                  height=SHOW_PREDICATES_CONTAINER_FRAME_HEIGHT,
                                                  background=BACKGROUND_COLOR_PRIMARY,
                                                  bd=0, highlightthickness=0, relief=tk.RIDGE)
        self.__show_predicates_canvas_frame = ttk.Frame(self.__show_predicates_canvas)
        self.__show_predicates_canvas_y_scrollbar = ttk.Scrollbar(self.__show_predicates_container_frame,
                                                                  orient=tk.VERTICAL,
                                                                  command=self.__show_predicates_canvas.yview)
        # Bind the scrollbar event
        self.__show_predicates_canvas_frame.bind('<Configure>',
                                                 lambda _: self.__show_predicates_canvas.configure(
                                                     scrollregion=self.__show_predicates_canvas.bbox('all')))
        self.__show_predicates_canvas.create_window((0, 0), window=self.__show_predicates_canvas_frame, anchor=tk.NW)
        self.__show_predicates_canvas.configure(yscrollcommand=self.__show_predicates_canvas_y_scrollbar.set)
        # Bind mousewheel event when cursor in frame
        self.__show_predicates_canvas_frame.bind('<Enter>',
                                                 lambda _: self.__show_predicates_canvas.bind_all('<MouseWheel>',
                                                                                                  self.__on_mousewheel))
        # Unbound if cursor leaves
        self.__show_predicates_canvas_frame.bind('<Leave>', self.__on_unbind_scroll)

        self.__show_predicates_checkbox_widgets_dict = {}
        # Show predicate checkboxes
        for predicate_symbol, show in self.__settings.shown_predicates_dict.items():
            var = tk.BooleanVar(value=show)
            label_text = predicate_symbol
            if predicate_symbol != INSTANCES_FACTS:
                label_text += f'/{SYMBOLS_WITH_ARITIES[predicate_symbol]}'
            label = ttk.Label(self.__show_predicates_canvas_frame, text=label_text)
            checkbox = ttk.Checkbutton(self.__show_predicates_canvas_frame, variable=var)
            self.__show_predicates_checkbox_widgets_dict[predicate_symbol] = (var, label, checkbox)

        path = get_target_file_location(self.__state.file, self.__state.model.root_name,
                                        suffix=GENERATED_FILE_SUFFIX, extension=LP_EXTENSION)
        self.__export_to_path_frame = BrowseFilePathFrame(self, path, widget_label_text='Export logic program to:', default_extension=LP_EXTENSION)

    def _setup_layout(self) -> None:
        self.__show_predicates_label.grid(row=0, column=0, sticky=tk.N + tk.W, pady=CONTROL_PAD_Y, padx=CONTROL_PAD_X)
        self.__show_predicates_container_frame.grid(row=0, column=1, sticky=tk.NSEW, pady=CONTROL_PAD_Y, padx=CONTROL_PAD_X)

        self.__show_predicates_canvas.grid(row=0, column=0, sticky=tk.NSEW)
        self.__show_predicates_canvas_y_scrollbar.grid(row=0, column=1, sticky=tk.NS + tk.E)

        for i, (_, label, checkbox) in enumerate(self.__show_predicates_checkbox_widgets_dict.values()):
            checkbox.grid(row=i, column=0, padx=CONTROL_PAD_X)
            label.grid(row=i, column=1, sticky=tk.W)

        self.__export_to_path_frame.grid(row=2, column=0, columnspan=2, sticky=tk.NSEW, pady=CONTROL_PAD_Y)

        self.__show_predicates_container_frame.columnconfigure(0, weigh=1)

        self.columnconfigure(0, weight=1, uniform='fred')
        self.columnconfigure(1, weight=1, uniform='fred')

        self.rowconfigure(1, weight=1)

    def __on_mousewheel(self, event):
        self.__show_predicates_canvas.yview_scroll(int(-1*(event.delta/120)), 'units')

    def __on_unbind_scroll(self, _):
        # This cannot be a lambda (for some reason), otherwise it does not unbind.
        self.__show_predicates_canvas.unbind_all('<MouseWheel>')

    @property
    def export_to_path(self):
        return self.__export_to_path_frame.path

    @property
    def shown_predicates_dict(self):
        return {predicate_symbol: checkbox_var.get() for predicate_symbol, (checkbox_var, _1, _2)
                in self.__show_predicates_checkbox_widgets_dict.items()}
