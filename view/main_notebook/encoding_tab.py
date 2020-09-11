"""Main notebook's encoding tab."""
from tkinter import ttk

from view.abstract import HasCommonSetup, Tab

TAB_NAME = 'Encoding'


class EncodingTab(Tab,
                  HasCommonSetup):
    """Used to set every encoding's information."""
    def __init__(self,
                 parent_notebook: ttk.Notebook):
        Tab.__init__(self, parent_notebook, TAB_NAME)
        HasCommonSetup.__init__(self)

    def _create_widgets(self) -> None:
        pass

    def _setup_layout(self) -> None:
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)
