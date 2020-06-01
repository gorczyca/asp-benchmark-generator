import tkinter as tk
from tkinter import ttk

STYLE_NAME = 'CUSTOM_STYLE'


class CustomTheme(ttk.Style):
    def __init__(self, master=None, *args, **kwargs):
        ttk.Style.__init__(self, master,  *args, **kwargs)

        self.style = ttk.Style(master)
        self.style.theme_create(STYLE_NAME, parent='alt', settings={
            "Vertical.TNotebook": {"configure": {"tabmargins": [10, 50, 10, 0], 'tabposition': 'wns'}},
            "Vertical.TNotebook.Tab": {"configure": {'width': 12, 'padding': [50, 50], 'borderwidth': 3, 'focuscolor': "#dd4814"}, # usuwa tę brzydką ramkę
                                       "map": {"background": [("selected", "#dF4F1F")], "expand": [("selected", [1, 1, 1, 0])]}},
            'Main.TNotebook.Tab': {'configure': {'width': 10, 'padding': [5, 5]}}
            })

    def use(self):
        self.style.theme_use(STYLE_NAME)