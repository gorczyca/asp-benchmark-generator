import tkinter as tk
from tkinter import ttk, messagebox

from pubsub import pub

import actions
from exceptions import BGError
from model.helpers import string_converter
from state import State
from view.abstract.has_common_setup import HasCommonSetup
from view.style import FONT_BOLD, FRAME_PAD_Y, FRAME_PAD_X
from view.abstract.window import Window
from view.common_callbacks import select_all_text

WINDOW_TITLE = 'Edit hierarchy'
LABEL_TEXT = 'Input hierarchy of view.\n("Tab" means subcomponent of component above.)'


class CreateHierarchyWindow(HasCommonSetup,
                            Window):
    def __init__(self, parent_frame, callback):
        self.__state = State()
        self.__callback = callback

        Window.__init__(self, parent_frame, WINDOW_TITLE)
        HasCommonSetup.__init__(self)

    # HasCommonSetup
    def _create_widgets(self):
        self.__text_frame = ttk.Frame(self)
        self.__x_scrollbar = ttk.Scrollbar(self.__text_frame, orient=tk.HORIZONTAL)
        self.__y_scrollbar = ttk.Scrollbar(self.__text_frame, orient=tk.VERTICAL)
        self.__text = tk.Text(self.__text_frame, wrap=tk.NONE, font=FONT_BOLD,
                              xscrollcommand=self.__x_scrollbar.set, yscrollcommand=self.__y_scrollbar.set)

        self.__text.focus()
        self.__text.mark_set(tk.INSERT, 1.0)
        self.__text.bind('<Control-a>', select_all_text)

        if self.__state.model.hierarchy:
            hierarchy_string = string_converter.hierarchy_to_string(self.__state.model.hierarchy)
            self.__text.insert(1.0, hierarchy_string)

        self.__x_scrollbar.config(command=self.__text.xview)
        self.__y_scrollbar.config(command=self.__text.yview)

        self.__label = ttk.Label(self, text=LABEL_TEXT, anchor=tk.W)

        self.__buttons_frame = ttk.Frame(self)
        self.__ok_button = ttk.Button(self.__buttons_frame, text='Ok', command=self.__ok)
        self.__cancel_button = ttk.Button(self.__buttons_frame, text='Cancel', command=self.destroy)

    def _setup_layout(self):
        self.__label.grid(row=0, column=0, sticky=tk.NSEW, padx=FRAME_PAD_X, pady=FRAME_PAD_Y)

        self.__text_frame.grid(row=1, column=0, columnspan=2, sticky=tk.NSEW, padx=FRAME_PAD_X, pady=FRAME_PAD_Y)
        self.__text_frame.columnconfigure(0, weight=1)
        self.__text_frame.rowconfigure(0, weight=1)

        self.__text.grid(column=0, row=0, sticky=tk.NSEW)

        self.__x_scrollbar.grid(row=1, column=0, sticky=tk.EW + tk.W)
        self.__y_scrollbar.grid(row=0, column=1, sticky=tk.NS + tk.E)

        self.__ok_button.grid(row=0, column=0, sticky=tk.E, pady=5)
        self.__cancel_button.grid(row=0, column=1, sticky=tk.W, pady=5)

        self.__buttons_frame.grid(row=2, column=0, columnspan=2, sticky=tk.NSEW)
        self.__buttons_frame.columnconfigure(0, weight=1)
        self.__buttons_frame.columnconfigure(1, weight=1)

        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

        self._set_geometry()

    # Class-specific
    def __ok(self):
        try:
            hierarchy_string = self.__text.get(1.0, tk.END)
            hierarchy = string_converter.string_to_hierarchy(hierarchy_string)
            self.__state.model.set_hierarchy(hierarchy)  # Sets hierarchy and marks leaves
            pub.sendMessage(actions.HIERARCHY_EDITED)
            pub.sendMessage(actions.MODEL_CHANGED)
            self.__callback()
            self.grab_release()
            self.destroy()
        except BGError as e:
            messagebox.showerror('Error', e.message, parent=self)




