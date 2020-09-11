"""Main notebook's encoding tab."""

from tkinter import ttk

from view.abstract import HasCommonSetup, Tab

TAB_NAME = 'Encoding'


class EncodingTab(Tab):
    """Used to set every encoding's information."""
    def __init__(self,
                 parent_notebook: ttk.Notebook):
        Tab.__init__(self, parent_notebook, TAB_NAME)
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)
