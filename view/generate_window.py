import tkinter as tk
from tkinter import ttk

from settings import Settings
from state import State
from view.abstract.has_common_setup import HasCommonSetup
from view.abstract.window import Window

WINDOW_TITLE = 'Generate logic program'

WINDOW_WIDTH_RATIO = 0.4
WINDOW_HEIGHT_RATIO = 0.8


class GenerateWindow(HasCommonSetup,
                     Window):
    def __init__(self, parent_frame, callback):
        self.__state = State()
        self.__callback = callback

        Window.__init__(self, parent_frame, WINDOW_TITLE)
        HasCommonSetup.__init__(self)

    def _create_widgets(self) -> None:
        self.__show_predicates_container_frame = ttk.Frame(self._window)
        self.__show_predicates_canvas = tk.Canvas(self.__show_predicates_container_frame)
        self.__show_predicates_canvas_frame = ttk.Frame(self.__show_predicates_canvas)
        self.__show_predicates_canvas_y_scrollbar = ttk.Scrollbar(self.__show_predicates_container_frame,
                                                                  orient=tk.VERTICAL,
                                                                  command=self.__show_predicates_canvas.yview)
        # Bind the scrollbar event
        self.__show_predicates_canvas_frame.bind('<Configure>',
                                                 lambda _: self.__show_predicates_canvas.configure(scrollregion=self.__show_predicates_canvas.bbox('all')))
        self.__show_predicates_canvas.create_window((0, 0), window=self.__show_predicates_canvas_frame, anchor=tk.NW)
        self.__show_predicates_canvas.configure(yscrollcommand=self.__show_predicates_canvas_y_scrollbar.set)
        # Bind mousewheel event when cursor in frame
        self.__show_predicates_canvas_frame.bind('<Enter>',
                                                 lambda _: self.__show_predicates_canvas.bind_all('<MouseWheel>', self.__on_mousewheel))
        # Unbound if cursor leaves
        self.__show_predicates_canvas_frame.bind('<Leave>',
                                                 lambda _: self.__show_predicates_canvas.unbind_all('<MouseWheel'))


        self.__show_predicates_checkbox_widgets = []
        self.__shown_predicates_dict = Settings.get_settings().shown_predicates_dict
        # Show predicate checkboxes
        for predicate_symbol, show in self.__shown_predicates_dict.items():
            var = tk.BooleanVar(value=show)
            label = ttk.Label(self.__show_predicates_canvas_frame, text=predicate_symbol)
            checkbox = ttk.Checkbutton(self.__show_predicates_canvas_frame, variable=var)
            self.__show_predicates_checkbox_widgets.append((var, label, checkbox))

    def _setup_layout(self) -> None:
        self.__show_predicates_container_frame.grid(row=0, column=0, sticky=tk.NSEW)
        self.__show_predicates_canvas.grid(row=0, column=0, sticky=tk.NSEW)
        self.__show_predicates_canvas_y_scrollbar.grid(row=0, column=1, sticky=tk.NS + tk.E)

        self.window.columnconfigure(0, weight=1)
        self.window.rowconfigure(0, weight=1)

        #self.__show_predicates_container_frame.rowconfigure(0, weight=1)
        self.__show_predicates_container_frame.columnconfigure(1, weight=1)

        self._set_geometry(height_ratio=WINDOW_HEIGHT_RATIO, width_ratio=WINDOW_WIDTH_RATIO)
        for i, (_, label, checkbox) in enumerate(self.__show_predicates_checkbox_widgets):
            checkbox.grid(row=i, column=0)
            label.grid(row=i, column=1, sticky=tk.W)

    def __on_mousewheel(self, event):
        #TODO: check if errors not thrown
        self.__show_predicates_canvas.yview_scroll(int(-1*(event.delta/120)), 'units')


