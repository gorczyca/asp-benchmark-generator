import tkinter as tk
from abc import ABC, abstractmethod

from view.style import BACKGROUND_COLOR_PRIMARY, WINDOW_WIDTH_RATIO, WINDOW_HEIGHT_RATIO


class Window(ABC):
    @abstractmethod
    def __init__(self, parent_frame, window_title, bind_enter_callback=None):
        self._window = tk.Toplevel(parent_frame, bg=BACKGROUND_COLOR_PRIMARY)
        self._window.grab_set()
        self._window.title(window_title)
        # self._window.transient(1)     # TODO:
        # self._window.attributes('-toolwindow', 1)
        if bind_enter_callback:
            self._window.bind('<Return>', lambda _: bind_enter_callback())

    def _set_geometry(self, height=None, width=None, width_ratio=WINDOW_WIDTH_RATIO, height_ratio=WINDOW_HEIGHT_RATIO):
        screen_width = self._window.winfo_screenwidth()
        screen_height = self._window.winfo_screenheight()
        window_width = round(screen_width * width_ratio) if width is None else width
        window_height = round(screen_height * height_ratio) if height is None else height
        x_pos = round((screen_width - window_width) / 2)
        y_pos = round((screen_height - window_height) / 2)
        self._window.geometry(f'{window_width}x{window_height}+{x_pos}+{y_pos}')

    @property
    def window(self): return self._window
