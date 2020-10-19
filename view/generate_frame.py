from tkinter import ttk
import tkinter as tk
from typing import Dict

from code_generator.code_generator import SYMBOLS_WITH_ARITIES, INSTANCES_FACTS
from misc.file_operations import LP_EXTENSION
from misc.settings import Settings
from misc.state import State
from view.browse_file_path_frame import BrowseFilePathFrame
from view.abstract import HasCommonSetup
from view.common import get_target_file_location, change_controls_state
from view.style import BACKGROUND_COLOR_PRIMARY, CONTROL_PAD_Y, CONTROL_PAD_X

GENERATED_FILE_SUFFIX = 'gen'
SHOW_PREDICATES_CONTAINER_FRAME_HEIGHT = 200
EXPORT_WINDOW_TITLE = 'Export logic program to:'


class GenerateFrame(ttk.Frame,
                    HasCommonSetup):
    """Reusable frame with all logic program generation related settings."""
    def __init__(self, parent_frame, settings: Settings, state: State, **kwargs):
        self.__state: State = state
        self.__settings: Settings = settings

        ttk.Frame.__init__(self, parent_frame, **kwargs)
        HasCommonSetup.__init__(self)

    def _create_widgets(self) -> None:
        self.__show_predicates_label = ttk.Label(self, text='Show selected predicates:')
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

        self.__show_all_predicates_checkbox_var = tk.BooleanVar(value=self.__settings.show_all_predicates)
        self.__show_all_predicates_checkbox_var.trace('w', self.__on_show_all_predicates_changed)
        self.__show_all_predicates_checkbox_label = ttk.Label(self, text='Show all predicates:')
        self.__show_all_predicates_checkbox = ttk.Checkbutton(self, variable=self.__show_all_predicates_checkbox_var)

        root_name = '' if not self.__state.model else self.__state.model.root_name
        path, file_name = get_target_file_location(self.__state.file, root_name,
                                                   suffix=GENERATED_FILE_SUFFIX, extension=LP_EXTENSION)
        self.__export_to_path_frame = BrowseFilePathFrame(self, path,
                                                          widget_label_text=EXPORT_WINDOW_TITLE,
                                                          title=EXPORT_WINDOW_TITLE,
                                                          default_extension=LP_EXTENSION)

    def _setup_layout(self) -> None:
        self.__show_predicates_label.grid(row=0, column=0, sticky=tk.N + tk.W, pady=CONTROL_PAD_Y, padx=CONTROL_PAD_X)
        self.__show_predicates_container_frame.grid(row=0, column=1, sticky=tk.NSEW, pady=CONTROL_PAD_Y, padx=CONTROL_PAD_X)

        self.__show_predicates_canvas.grid(row=0, column=0, sticky=tk.NSEW)
        self.__show_predicates_canvas_y_scrollbar.grid(row=0, column=1, sticky=tk.NS + tk.E)

        for i, (_, label, checkbox) in enumerate(self.__show_predicates_checkbox_widgets_dict.values()):
            checkbox.grid(row=i, column=0, padx=CONTROL_PAD_X)
            label.grid(row=i, column=1, sticky=tk.W)

        self.__show_all_predicates_checkbox_label.grid(row=1, column=0, sticky=tk.W, pady=CONTROL_PAD_Y, padx=CONTROL_PAD_X)
        self.__show_all_predicates_checkbox.grid(row=1, column=1, sticky=tk.E, pady=CONTROL_PAD_Y, padx=CONTROL_PAD_X)

        self.__export_to_path_frame.grid(row=2, column=0, columnspan=2, sticky=tk.EW + tk.S, pady=CONTROL_PAD_Y)

        self.__show_predicates_container_frame.columnconfigure(0, weight=1)

        self.columnconfigure(0, weight=1, uniform='fred')
        self.columnconfigure(1, weight=1, uniform='fred')

        self.rowconfigure(1, weight=1)
        self.rowconfigure(2, weight=1)

    def __on_mousewheel(self, event) -> None:
        """Executes whenever mousewheel is scrolled and cursor is inside the __show_predicates_canvas."""
        self.__show_predicates_canvas.yview_scroll(int(-1*(event.delta/120)), 'units')

    def __on_unbind_scroll(self, _) -> None:
        """Unbinds the mousewheel scroll event from __show_predicates_canvas (whenever cursor leaves the canvas).

        This cannot be a lambda expression (for some reason), because it would not unbind.
        """
        self.__show_predicates_canvas.unbind_all('<MouseWheel>')

    def __on_show_all_predicates_changed(self, *_):
        """Executes whenever __show_all_predicates_checkbox is toggled."""
        show_all = self.__show_all_predicates_checkbox_var.get()
        if show_all:
            state = tk.DISABLED
            # Set all specific predicate checkboxes to unchecked
            for (var, _0, _1) in self.__show_predicates_checkbox_widgets_dict.values():
                var.set(False)
        else:
            state = tk.NORMAL
            # Restore values of specific predicate checkboxes
            for predicate_symbol, show in self.__settings.shown_predicates_dict.items():
                self.__show_predicates_checkbox_widgets_dict[predicate_symbol][0].set(show)

        # Block / unblock specific predicate checkboxes
        change_controls_state(state,
                              *[checkbox for (_0, _1, checkbox) in self.__show_predicates_checkbox_widgets_dict.values()])

    @property
    def export_to_path(self):
        """Returns the export to path."""
        return self.__export_to_path_frame.path

    @property
    def shown_predicates_dict(self) -> Dict[str, bool]:
        """Returns the dictionary indicating for which predicate symbols to generate the "#show" directive.

        :return: Dictionary of type predicate_symbol: show.
        """
        return {predicate_symbol: checkbox_var.get() for predicate_symbol, (checkbox_var, _1, _2)
                in self.__show_predicates_checkbox_widgets_dict.items()}

    @property
    def show_all_predicates(self) -> bool:
        """Returns the __show_all_predicates_checkbox value."""
        return self.__show_all_predicates_checkbox_var.get()

    def change_frame_controls_state(self, state) -> None:
        """Changes widgets' state.

        :param state: Desired state of the widgets (tk.NORMAL or tk.DISABLED).
        """
        change_controls_state(state,
                              *[checkbox for (_0, _1, checkbox) in self.__show_predicates_checkbox_widgets_dict.values()],
                              self.__show_all_predicates_checkbox)
        self.__export_to_path_frame.change_state(state)
