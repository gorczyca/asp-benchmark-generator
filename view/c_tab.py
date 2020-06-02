import tkinter as tk


class CTab(tk.Frame):
    def __init__(self, parent, parent_notebook, tab_name, *args, **kwargs):
        tk.Frame.__init__(self, parent_notebook, *args, **kwargs)

        self.controller = parent.controller
        self.parent_notebook = parent_notebook

        self.frame = tk.Frame(parent_notebook, *args, **kwargs)
        self.parent_notebook.add(self.frame, text=tab_name)

