"""Stores and creates all style data."""

import tkinter as tk
from tkinter import ttk

# ('clam', 'alt', 'default', 'classic')
PARENT_THEME = 'alt'
THEME_NAME = 'theme'

ACTIVE_COLOR = '#dF4F1F'
HOVER_COLOR = '#d1d7f0'
FONT_TYPE = 'Arial'
CODE_FONT_TYPE = 'Courier'
SMALL_FONT_SIZE = 10
FONT_SIZE = 13
BIG_FONT_SIZE = 18

SMALL_FONT = (FONT_TYPE, SMALL_FONT_SIZE)

FONT = (FONT_TYPE, FONT_SIZE)
FONT_BOLD = (FONT_TYPE, FONT_SIZE, 'bold')
FONT_ITALIC = (FONT_TYPE, FONT_SIZE, 'italic')
FONT_UNDERLINE = (FONT_TYPE, FONT_SIZE, 'underline')
HEADER_FONT = (FONT_TYPE, BIG_FONT_SIZE, 'bold')
TITLE_FONT = (FONT_TYPE, BIG_FONT_SIZE, 'bold', 'underline')
CODE_FONT = (CODE_FONT_TYPE, FONT_SIZE)

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

FONT_COLOR_PRIMARY = '#2c3e50'
FONT_COLOR_SECONDARY = '#f5f6fa'


class CustomTheme(ttk.Style):
    def __init__(self, master=None, name=THEME_NAME):
        ttk.Style.__init__(self, master)
        self.__name = name
        self.theme_create(name, parent=PARENT_THEME, settings={
            '.': {'configure': {'font': FONT}},  # General font
            'Big.TLabel': {'configure': {'font': (FONT_TYPE, 18, 'bold')}},
            'Bold.TLabel': {'configure': {'font': FONT_BOLD}},
            'Small.TLabel': {'configure': {'font': SMALL_FONT}},
            'Vertical.TNotebook': {'configure': {'tabmargins': [10, 50, 10, 0],
                                                 'tabposition': 'wns',  # Pin notebook to the right side
                                                 'background': BACKGROUND_COLOR_PRIMARY}},
            'Vertical.TNotebook.Tab': {'configure': {'width': 12,
                                                     'padding': [30, 30],
                                                     'borderwidth': 3,
                                                     'focuscolor': ADDITIONAL_COLOR_PRIMARY,  # Remove ugly border
                                                     'font': (FONT_TYPE, 18),   # Set big font
                                                     'background': BACKGROUND_COLOR_PRIMARY
                                                     },
                                       'map': {'background': [('selected', ADDITIONAL_COLOR_PRIMARY)],
                                               'expand': [('selected', [1, 1, 1, 0])],
                                               'foreground': [('selected', FONT_COLOR_SECONDARY)],
                                               }},
            'Help.TNotebook.Tab': {'configure': {
                                                 'padding': [5, 5],
                                                 'background': BACKGROUND_COLOR_PRIMARY,
                                                 'focuscolor': BACKGROUND_COLOR_PRIMARY
                                                 }},    # remove ugly border
            'TNotebook': {'configure': {'background': BACKGROUND_COLOR_PRIMARY}},
            'Main.TNotebook.Tab': {'configure': {'width': 10,
                                                 'padding': [5, 5],
                                                 'background': BACKGROUND_COLOR_PRIMARY,
                                                 'focuscolor': BACKGROUND_COLOR_PRIMARY
                                                 }},    # remove ugly border
            'Treeview': {'configure': {'background': BACKGROUND_COLOR_PRIMARY,
                                       'fieldbackground': BACKGROUND_COLOR_3RD}},
            'Treeview.Heading': {'configure': {'background': ADDITIONAL_COLOR_PRIMARY,
                                               'foreground': FONT_COLOR_SECONDARY}},
            'Custom.Treeview': {'configure': {'highlightthickness': 0, 'bd': 0, 'font': ('Arial', 11),
                                              'background': BACKGROUND_COLOR_PRIMARY}},
            'Custom.Treeview.Heading': {'configure': {'font': ('Arial', 13, 'bold')}},
            'TLabel': {'configure': {'background': BACKGROUND_COLOR_PRIMARY}},
            'Link.TLabel': {'configure': {'foreground': 'blue',
                                          'font': FONT_UNDERLINE,
                                            }},
            'TButton': {'configure': {'padding': [30, 0, 30, 0], 'relief': tk.SOLID,
                                      'background': BACKGROUND_COLOR_PRIMARY,
                                      'focuscolor': BACKGROUND_COLOR_PRIMARY },   # Remove ugly border
                        'map': {'foreground': [# ('pressed', ADDITIONAL_COLOR_PRIMARY), # If pressed state is necessary
                                               ('active', FONT_COLOR_SECONDARY)],
                                'background': [('pressed', '!disabled', ADDITIONAL_COLOR_PRIMARY),
                                               ('active', ADDITIONAL_COLOR_PRIMARY)],
                                }},
            'SmallFont.TButton': {'configure': {'font': SMALL_FONT}},
            'TFrame': {'configure': {'padding': [FRAME_PAD_Y, FRAME_PAD_X],
                                     'background': BACKGROUND_COLOR_PRIMARY}},
            'Horizontal.TProgressbar': {'configure': {'background': ADDITIONAL_COLOR_PRIMARY}},
            'TRadiobutton': {'configure': {'background': BACKGROUND_COLOR_PRIMARY,
                                           'focuscolor': BACKGROUND_COLOR_PRIMARY}},  # Remove ugly border
            'TCheckbutton': {'configure': {'background': BACKGROUND_COLOR_PRIMARY,
                                           'focuscolor': BACKGROUND_COLOR_PRIMARY }},   # Remove ugly border
            'TScrollbar': {'configure': {'background': BACKGROUND_COLOR_PRIMARY}},
            'TCombobox': {'configure': {'background': BACKGROUND_COLOR_3RD,
                                        'selectbackground': BACKGROUND_COLOR_3RD,
                                        'selectforeground': FONT_COLOR_PRIMARY,
                                        }}
        })

    def use(self):
        """Activates the theme."""
        self.theme_use(self.__name)
