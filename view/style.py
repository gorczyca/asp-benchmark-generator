import tkinter as tk
from tkinter import ttk

# ('clam', 'alt', 'default', 'classic')
PARENT_THEME = 'alt'
STYLE_NAME = 'CUSTOM_STYLE'
DARK_THEME = 'DARK_STYLE'

ACTIVE_COLOR = '#dF4F1F'
ACTIVE_COLOR_2 = 'black'
HOVER_COLOR = 'green'
FONT_TYPE = 'Arial'

SMALL_FONT = (FONT_TYPE, 10)
FONT = (FONT_TYPE, 13)
FONT_BOLD = (FONT_TYPE, 13, 'bold')
BIG_FONT = (FONT_TYPE, 18)
BIG_FONT_BOLD = (FONT_TYPE, 18, 'bold')
MEDIUM_FONT = (FONT_TYPE, 15)
MEDIUM_FONT_BOLD = (FONT_TYPE, 15, 'bold')

WINDOW_WIDTH_RATIO = 0.75
WINDOW_HEIGHT_RATIO = 0.75

CONTROL_PAD_Y = 3
CONTROL_PAD_X = 3

FRAME_PAD_Y = 10
FRAME_PAD_X = 10

BACKGROUND_COLOR_PRIMARY = '#f5f6fa'
BACKGROUND_COLOR_SECONDARY = '#8c98c6'
BACKGROUND_COLOR_3RD = '#ffffff'

ADDITIONAL_COLOR_PRIMARY = '#0A3D62'
ADDITIONAL_COLOR_SECONDARY = '#0A3D62'

FONT_COLOR_PRIMARY = '#2c3e50'
FONT_COLOR_SECONDARY = '#f5f6fa'


class CustomTheme(ttk.Style):
    def __init__(self, master=None):
        ttk.Style.__init__(self, master)
        self.style = ttk.Style(master)
        self.style.theme_create(DARK_THEME, parent=PARENT_THEME, settings={
            '.': {'configure': {'font': FONT}},  # TODO: it is too general
            'Big.TLabel': {'configure': {'font': BIG_FONT_BOLD}},
            'Bold.TLabel': {'configure': {'font': FONT_BOLD}},
            'Medium.Bold.TLabel': {'configure': {'font': MEDIUM_FONT_BOLD}},
            'Small.TLabel': {'configure': {'font': SMALL_FONT}},
            "Vertical.TNotebook": {"configure": {"tabmargins": [10, 50, 10, 0], 'tabposition': 'wns',
                                                 'background': BACKGROUND_COLOR_PRIMARY}},
            "Vertical.TNotebook.Tab": {"configure": {'width': 12, 'padding': [30, 30], 'borderwidth': 3,
                                                     'focuscolor': ADDITIONAL_COLOR_PRIMARY,  # remove ugly border
                                                     'font': BIG_FONT,
                                                     'background': BACKGROUND_COLOR_PRIMARY},
                                       "map": {"background": [("selected", ADDITIONAL_COLOR_PRIMARY)],
                                               "expand": [("selected", [1, 1, 1, 0])],
                                               'foreground': [("selected", FONT_COLOR_SECONDARY)]}},
            'Main.TNotebook': {'configure': {'background': BACKGROUND_COLOR_PRIMARY}},
            'Main.TNotebook.Tab': {'configure': {'width': 10, 'padding': [5, 5], 'background': BACKGROUND_COLOR_PRIMARY,
                                                 'focuscolor': BACKGROUND_COLOR_PRIMARY,    # remove ugly border
                                                 }},
            'Treeview': {'configure': {'background': BACKGROUND_COLOR_PRIMARY,
                                       'fieldbackground': BACKGROUND_COLOR_3RD}},
            'Treeview.Heading': {'configure': {'background': ADDITIONAL_COLOR_SECONDARY,
                                               'foreground': FONT_COLOR_SECONDARY}},
            'Custom.Treeview': {'configure': {'highlightthickness': 0, 'bd': 0, 'font': ('Arial', 11),
                                              'background': BACKGROUND_COLOR_PRIMARY}},
            'Custom.Treeview.Heading': {'configure': {'font': ('Arial', 13, 'bold')}},
            # 'TButton': {'map': {'highlightbackground': ACTIVE_COLOR}}
            # 'TButton': {'configure': {'padding': [50, 0, 50, 0], 'border': '10', 'borderwidth': 100, 'relief': tk.SOLID},
            #'TLabel': {'configure': {'background': BACKGROUND_COLOR_PRIMARY}},
            'TLabel': {'configure': {'background': BACKGROUND_COLOR_PRIMARY}},
            'TButton': {'configure': {'padding': [30, 0, 30, 0], 'relief': tk.SOLID,
                                      'background': BACKGROUND_COLOR_PRIMARY,
                                      'focuscolor': BACKGROUND_COLOR_PRIMARY    # remove ugly border
                                      },
                        # 'map': {'foreground': [('pressed', 'white'), ('active', 'blue')],
                        'map': {'foreground': [# ('pressed', ADDITIONAL_COLOR),
                                               ('active', FONT_COLOR_SECONDARY)],
                                'background': [('pressed', '!disabled', ADDITIONAL_COLOR_PRIMARY),
                                               ('active', ADDITIONAL_COLOR_PRIMARY)],
                                 #'font': [('active', FONT_BOLD)]},
                                }
                        },
            'TFrame': {'configure': {'padding': [FRAME_PAD_Y, FRAME_PAD_X], 'background': BACKGROUND_COLOR_PRIMARY}},
            'TCheckbutton': {'configure': {'background': BACKGROUND_COLOR_PRIMARY,
                                           'focuscolor': BACKGROUND_COLOR_PRIMARY }},   # remove ugly border
            'TScrollbar': {'configure': {'background': BACKGROUND_COLOR_PRIMARY}},
            'TCombobox': {'configure': {'background': BACKGROUND_COLOR_3RD,
                                        'selectbackground': BACKGROUND_COLOR_3RD,
                                        'selectforeground': FONT_COLOR_PRIMARY,
                                        # 'fieldbackground': BACKGROUND_COLOR_PRIMARY
                                        }
                          }
        })

    def use(self):
        self.style.theme_use(DARK_THEME)
