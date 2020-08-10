import os
import tkinter as tk
from tkinter import ttk, filedialog

from settings import Settings
from state import State
from view.abstract.has_common_setup import HasCommonSetup
from view.abstract.window import Window
from file_operations import LP_EXTENSION

WINDOW_TITLE = 'Generate logic program...'

GENERATED_FILE_SUFFIX = 'gen'

WINDOW_WIDTH_RATIO = 0.4
WINDOW_HEIGHT_RATIO = 0.8


class GenerateWindow(HasCommonSetup,
                     Window):
    def __init__(self, parent_frame, callback):
        self.__state = State()
        self.__callback = callback
        self.__settings = Settings.get_settings()

        Window.__init__(self, parent_frame, WINDOW_TITLE)
        HasCommonSetup.__init__(self)

    def _create_widgets(self) -> None:
        self.__show_predicates_label = ttk.Label(self._window, text='Show predicates:')
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
        self.__show_predicates_canvas_frame.bind('<Leave>', self.__on_unbind_scroll)

        self.__show_predicates_checkbox_widgets = []
        # Show predicate checkboxes
        for predicate_symbol, show in self.__settings.shown_predicates_dict.items():
            var = tk.BooleanVar(value=show)
            label = ttk.Label(self.__show_predicates_canvas_frame, text=predicate_symbol)
            checkbox = ttk.Checkbutton(self.__show_predicates_canvas_frame, variable=var)
            self.__show_predicates_checkbox_widgets.append((var, label, checkbox))

        self.__generate_to_label = ttk.Label(self._window, text='Generate to:')
        self.__browse_file_button = ttk.Button(self._window, text='Browse...', command=self.__on_browse_path)
        self.__generate_to_path_label_var = tk.StringVar(value='Set target location.')
        self.__generate_to_path_label = ttk.Label(self._window, textvariable=self.__generate_to_path_label_var)

        if self.__state.file is not None:
            root_name = self.__state.model.root_name
            dir_name = os.path.dirname(self.__state.file.name)
            path = os.path.join(dir_name, f'{root_name}_{GENERATED_FILE_SUFFIX}{LP_EXTENSION}')
            path = os.path.normpath(path)   # Normalize the back- & front-slashes
            self.__generate_to_path_label_var.set(path)

    def _setup_layout(self) -> None:
        self.__show_predicates_label.grid(row=0, column=0)
        self.__show_predicates_container_frame.grid(row=1, column=0, sticky=tk.NSEW)
        self.__show_predicates_canvas.grid(row=0, column=0, sticky=tk.NSEW)
        self.__show_predicates_canvas_y_scrollbar.grid(row=0, column=1, sticky=tk.NS + tk.E)

        for i, (_, label, checkbox) in enumerate(self.__show_predicates_checkbox_widgets):
            checkbox.grid(row=i, column=0)
            label.grid(row=i, column=1, sticky=tk.W)

        self.__generate_to_label.grid(row=2, column=0)
        self.__generate_to_path_label.grid(row=3, column=0)
        self.__browse_file_button.grid(row=3, column=1)

        self.window.columnconfigure(0, weight=1)
        self.window.rowconfigure(0, weight=1)

        self.__show_predicates_container_frame.columnconfigure(1, weight=1)
        self._set_geometry(height_ratio=WINDOW_HEIGHT_RATIO, width_ratio=WINDOW_WIDTH_RATIO)

    def __on_browse_path(self):
        # TODO:
        # filename = tkFileDialog.asksaveasfilename(defaultextension=".espace",
        #                                           filetypes=(("espace file", "*.espace"), ("All Files", "*.*")))
        file_path = filedialog.asksaveasfilename(defaultextension=LP_EXTENSION, parent=self._window)
        if file_path:
            file_path = os.path.normpath(file_path)
            self.__generate_to_path_label_var.set(file_path)

    def __on_mousewheel(self, event):
        self.__show_predicates_canvas.yview_scroll(int(-1*(event.delta/120)), 'units')

    def __on_unbind_scroll(self, _):
        # This cannot be a lambda (for some reason), otherwise it does not unbind.
        self.__show_predicates_canvas.unbind_all('<MouseWheel>')





