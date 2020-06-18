import tkinter as tk
from abc import ABC, abstractmethod


class BaseFrame(tk.Frame, ABC):
    @abstractmethod
    def __init__(self, parent_frame):
        tk.Frame.__init__(self, parent_frame)
        self.parent_frame = parent_frame
