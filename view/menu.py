import tkinter as tk
from tkinter import ttk
from view.c_frame import CFrame


class Menu(CFrame):
    def __init__(self, parent, parent_frame, *args, **kwargs):
        CFrame.__init__(self, parent, parent_frame, *args, **kwargs)

        self.menu = tk.Menu(parent_frame, *args, **kwargs)

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

        self.menu.add_cascade(label='File', menu=file_menu)
        self.menu.add_cascade(label='Edit', menu=edit_menu)
        self.menu.add_cascade(label='Help', menu=help_menu)
        self.menu.add_cascade(label='About', menu=about_menu)

        self.parent_frame.config(menu=self.menu)

