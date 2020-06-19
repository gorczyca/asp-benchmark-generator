import tkinter as tk
from tkinter import ttk

from view.abstract.base_frame import BaseFrame
from view.abstract.has_common_setup import HasCommonSetup


class MainNotebook(BaseFrame,
                   HasCommonSetup):
    def __init__(self, parent, parent_frame):
        BaseFrame.__init__(self, parent_frame)

        HasCommonSetup.__init__(self)

    def _create_widgets(self):
        self.notebook = ttk.Notebook(self.parent_frame, style='Main.TNotebook')

    def _setup_layout(self):
        self.notebook.grid(row=0, column=0, sticky=tk.E)

