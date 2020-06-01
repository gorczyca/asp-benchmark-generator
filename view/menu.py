import tkinter as tk
from tkinter import ttk
from view.r_frame import RFrame


class Menu(RFrame):
    def __init__(self, parent, *args, **kwargs):
        RFrame.__init__(self, parent, *args, **kwargs)

        self._menu = tk.Menu(self.parent.frame, *args, **kwargs)

        file_menu = tk.Menu(tearoff=0)
        file_menu.add_command(label='New')
        file_menu.add_separator()
        file_menu.add_command(label='Open')
        file_menu.add_command(label='Save')
        file_menu.add_command(label='Save as...')

        #TODO: finish the rest
        edit_menu = tk.Menu(tearoff=0)
        help_menu = tk.Menu(tearoff=0)
        about_menu = tk.Menu(tearoff=0)

        self._menu.add_cascade(label='File', menu=file_menu)
        self._menu.add_cascade(label='Edit', menu=edit_menu)
        self._menu.add_cascade(label='Help', menu=help_menu)
        self._menu.add_cascade(label='About', menu=about_menu)
        self.parent.frame.config(menu=self._menu)

