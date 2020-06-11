from tkinter import ttk

from view.c_frame import CFrame


class VerticalNotebook(CFrame):
    def __init__(self, parent, parent_frame, *args, **kwargs):
        CFrame.__init__(self, parent, parent_frame, *args, **kwargs)

        self.notebook = ttk.Notebook(self.parent_frame, style='Vertical.TNotebook')

        # TODO: move
        self.notebook.grid(row=0, column=0, sticky='nw')
