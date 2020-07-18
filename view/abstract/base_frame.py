import tkinter as tk
from abc import ABC, abstractmethod
from tkinter import ttk


class BaseFrame(ttk.Frame, ABC):
    @abstractmethod
    def __init__(self, parent_frame):
        ttk.Frame.__init__(self, parent_frame)
        self.parent_frame = parent_frame
