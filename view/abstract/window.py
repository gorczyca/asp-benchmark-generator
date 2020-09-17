"""Basic interface for custom windows."""

import tkinter as tk
from abc import ABC, abstractmethod
from tkinter import ttk
from typing import Optional, Callable

from view.style import BACKGROUND_COLOR_PRIMARY, WINDOW_WIDTH_RATIO, WINDOW_HEIGHT_RATIO


class Window(ABC,
             tk.Toplevel):
    @abstractmethod
    def __init__(self,
                 parent_frame,
                 window_title: str,
                 bind_enter_callback: Optional[Callable] = None):
        """
        :param parent_frame: Parent frame.
        :param window_title: Window title.
        :param bind_enter_callback: Callback function, to be exectured when 'Enter' is pressed.
        """
        tk.Toplevel.__init__(self, parent_frame, bg=BACKGROUND_COLOR_PRIMARY)
        self.grab_set()
        self.focus()
        self.title(window_title)
        if bind_enter_callback:
            self.bind('<Return>', lambda _: bind_enter_callback())

    def _set_geometry(self, height=None, width=None, width_ratio=WINDOW_WIDTH_RATIO, height_ratio=WINDOW_HEIGHT_RATIO):
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        window_width = round(screen_width * width_ratio) if width is None else width
        window_height = round(screen_height * height_ratio) if height is None else height
        x_pos = round((screen_width - window_width) / 2)
        y_pos = round((screen_height - window_height) / 2)
        self.geometry(f'{window_width}x{window_height}+{x_pos}+{y_pos}')
