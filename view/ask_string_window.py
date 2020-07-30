import tkinter as tk
from tkinter import ttk, messagebox

from exceptions import BGError
from view.abstract.has_common_setup import HasCommonSetup
from view.abstract.window import Window
from view.style import CONTROL_PAD_Y, CONTROL_PAD_X, FRAME_PAD_Y, FRAME_PAD_X

WINDOW_HEIGHT = 100
WINDOW_WIDTH_RATIO = 0.3
WINDOW_TITLE = 'Enter string'
PROMPT = 'Enter string'


class AskStringWindow(HasCommonSetup,
                      Window):
    def __init__(self, parent_frame, callback, window_title=WINDOW_TITLE, prompt_text=PROMPT, string=''):
        self.__callback = callback
        self.__prompt_text = prompt_text
        self.__string = string

        Window.__init__(self, parent_frame, window_title, bind_enter_callback=self.__ok)
        HasCommonSetup.__init__(self)

    def _create_widgets(self) -> None:
        self.__prompt_label = ttk.Label(self._window, text=self.__prompt_text, anchor=tk.W)

        self.__string_entry_var = tk.StringVar(value=self.__string)
        self.__string_entry = ttk.Entry(self._window, textvariable=self.__string_entry_var)
        self.__string_entry.focus()
        self.__ok_button = ttk.Button(self._window, text='OK', command=self.__ok)
        self.__cancel_button = ttk.Button(self._window, text='Cancel', command=self._window.destroy)

    def _setup_layout(self) -> None:
        self.__prompt_label.grid(row=0, column=0, columnspan=2, sticky=tk.EW, padx=FRAME_PAD_X, pady=(FRAME_PAD_Y, CONTROL_PAD_Y))

        self.__string_entry.grid(row=1, column=0, columnspan=2, sticky=tk.EW, padx=FRAME_PAD_X, pady=CONTROL_PAD_Y)
        self.__ok_button.grid(row=2, column=0, sticky=tk.EW, padx=(FRAME_PAD_X, CONTROL_PAD_X),
                              pady=(CONTROL_PAD_Y, FRAME_PAD_Y))
        self.__cancel_button.grid(row=2, column=1, sticky=tk.EW, padx=(CONTROL_PAD_X, FRAME_PAD_X),
                                  pady=(CONTROL_PAD_Y, FRAME_PAD_Y))

        self._window.columnconfigure(0, weight=1)
        self._window.columnconfigure(1, weight=1)
        self._window.rowconfigure(0, weight=1)

        self._set_geometry(height=WINDOW_HEIGHT, width_ratio=WINDOW_WIDTH_RATIO)

    def __ok(self):
        try:
            string = self.__string_entry_var.get()
            self.__callback(string)
            self._window.grab_release()
            self._window.destroy()
        except BGError as e:
            messagebox.showerror('Error', e.message, parent=self._window)
