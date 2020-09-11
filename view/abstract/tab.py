"""Basic interface for ttk.Notebook's tab."""

import tkinter as tk
from abc import ABC, abstractmethod
from tkinter import ttk


class Tab(ABC,
          ttk.Frame):
    @abstractmethod
    def __init__(self,
                 parent_notebook: ttk.Notebook,
                 tab_name: str):
        """
        :param parent_notebook: Parent notebook of this Tab.
        :param tab_name: Name of the Tab in the notebook.
        """
        ttk.Frame.__init__(self, parent_notebook)
        self.grid(row=0, column=0, sticky=tk.NSEW)
        parent_notebook.add(self, text=tab_name)



