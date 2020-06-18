import tkinter as tk
from tkinter import ttk

# ('clam', 'alt', 'default', 'classic'
PARENT_THEME = 'alt'
# PARENT_THEME = 'radiance'
STYLE_NAME = 'CUSTOM_STYLE'

ACTIVE_COLOR = '#dF4F1F'
HOVER_COLOR = 'green'
FONT_TYPE = 'Arial'

FONT = (FONT_TYPE, 13)
FONT_BOLD = (FONT_TYPE, 13, 'bold')
BIG_FONT = (FONT_TYPE, 18)
BIG_FONT_BOLD = (FONT_TYPE, 18, 'bold')

VERTICAL_TAB_HEIGHT = 720
VERTICAL_TAB_WIDTH = 1080


class CustomTheme(ttk.Style):
    def __init__(self, master=None):
        ttk.Style.__init__(self, master)

        # font=('URW Gothic L','40','bold')
        self.style = ttk.Style(master)
        self.style.theme_create(STYLE_NAME, parent=PARENT_THEME, settings={
            '.': {'configure': {'font': FONT}},  # TODO: make more specific (too general)
            'Big.TLabel': {'configure': {'font': BIG_FONT_BOLD}},
            'Bold.TLabel': {'configure': {'font': FONT_BOLD}},
            # 'TSpinbox': {'configure': {'padding': 50}},
            "Vertical.TNotebook": {"configure": {"tabmargins": [10, 50, 10, 0], 'tabposition': 'wns'}},
            "Vertical.TNotebook.Tab": {"configure": {'width': 12, 'padding': [30, 30], 'borderwidth': 3,
                                                     'focuscolor': "#dd4814", 'font': BIG_FONT}, # usuwa tę brzydką ramkę
                                       "map": {"background": [("selected", ACTIVE_COLOR)], 'font': [('selected', BIG_FONT_BOLD)],
                                                "expand": [("selected", [1, 1, 1, 0])], 'foreground': [("selected", 'white')]}},
            'Main.TNotebook.Tab': {'configure': {'width': 10, 'padding': [5, 5]}},
            'Custom.Treeview': {'configure': {'highlightthickness': 0, 'bd': 0, 'font': ('Arial', 11)}},
            'Custom.Treeview.Heading': {'configure': {'font': ('Arial', 13, 'bold')}},
            #'TButton': {'map': {'highlightbackground': ACTIVE_COLOR}}
            #'TButton': {'configure': {'padding': [50, 0, 50, 0], 'border': '10', 'borderwidth': 100, 'relief': tk.SOLID},
            'TButton': {'configure': {'padding': [30, 0, 30, 0], 'relief': tk.SOLID },
                        #'map': {'foreground': [('pressed', 'white'), ('active', 'blue')],
                        'map': {'foreground': [('pressed', 'white')],
                                'background': [('pressed', '!disabled', ACTIVE_COLOR), ('active', 'white')],
                                'font': [('active', FONT_BOLD)]},
                        }

            })

        # self.style.layout("Custom.Treeview", [('Custom.Treeview.treearea', {'sticky': 'nswe'})])  # Remove the borders

    def use(self):
        self.style.theme_use(STYLE_NAME)