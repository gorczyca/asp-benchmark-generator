import tkinter as tk
from tkinter import ttk

STYLE_NAME = 'CUSTOM_STYLE'

class CustomTheme(ttk.Style):
    def __init__(self, master=None, *args, **kwargs):
        ttk.Style.__init__(self, master,  *args, **kwargs)

        self.style = ttk.Style(master)
        self.style.theme_create(STYLE_NAME, parent='alt', settings={
            "Vertical.TNotebook": {"configure": {"tabmargins": [10, 10, 10, 10], 'tabposition': 'wns' } },
            "Vertical.TNotebook.Tab": {"configure": {'width': 30, 'padding': [30,30] }},
            'Main.TNotebook.Tab': {'configure': {'width': 20, 'padding': [20,20]}}
            })

    def use(self):
        self.style.theme_use(STYLE_NAME)