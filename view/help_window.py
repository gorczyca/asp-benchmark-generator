import re
import tkinter as tk
from tkinter import ttk
import webbrowser

from help_ import parse_text
from misc.project_info import PROJECT_WEBSITE
from view.abstract import HasCommonSetup, Window
from view.style import FRAME_PAD_Y, FRAME_PAD_X, FONT, FONT_BOLD, FONT_ITALIC, FONT_UNDERLINE, HEADER_FONT, \
    ADDITIONAL_COLOR_PRIMARY, CODE_FONT, TITLE_FONT

WINDOW_TITLE = 'Help'

WINDOW_WIDTH_RATIO = 0.75
WINDOW_HEIGHT_RATIO = 0.75

BOTTOM_PAD_Y = 30
NOTEPAD_TOP_PADY_Y = 20

TAB_TAG = 'tab'
TAB_RE = r'<tab>(.*?)</tab>'

HELP_INPUT_FILE_PATH = './help_text'


class HelpWindow(HasCommonSetup,
                 Window):
    """Used to present the user's guide."""
    def __init__(self, parent_frame):
        pass
        Window.__init__(self, parent_frame, WINDOW_TITLE)
        HasCommonSetup.__init__(self)

    def _create_widgets(self) -> None:
        self.__main_frame = ttk.Frame(self)
        self.__notebook = ttk.Notebook(self.__main_frame, style='Help.TNotebook')

        self.__tabs_widgets = []
        for tab_name, tab_text in self.get_tabs():
            tab_frame = ttk.Frame(self.__notebook)
            self.__notebook.add(tab_frame, text=tab_name)
            y_scrollbar = ttk.Scrollbar(tab_frame, orient=tk.VERTICAL)
            text_widget = tk.Text(tab_frame, font=FONT, yscrollcommand=y_scrollbar.set, wrap=tk.WORD)
            self.__configure_tags(text_widget)
            # Insert and format text
            self.__format_text(text_widget, tab_text)
            text_widget.config(state=tk.DISABLED)
            y_scrollbar.config(command=text_widget.yview)
            self.__tabs_widgets.append((tab_frame, y_scrollbar, text_widget))

        self.__problems_frame = ttk.Frame(self)
        self.__problems_text_label = ttk.Label(self.__problems_frame, text='In case of problems, please refer to:')
        self.__problems_webiste_label = ttk.Label(self.__problems_frame, text=PROJECT_WEBSITE, style='Link.TLabel',
                                                  cursor='hand2')
        self.__problems_webiste_label.bind('<Button-1>', lambda _: webbrowser.open_new_tab(PROJECT_WEBSITE))

    def _setup_layout(self) -> None:
        self._set_geometry(height_ratio=WINDOW_HEIGHT_RATIO, width_ratio=WINDOW_WIDTH_RATIO)

        self.__main_frame.grid(row=0, column=0, sticky=tk.NSEW)
        self.__notebook.grid(row=0, column=0, sticky=tk.NSEW, padx=FRAME_PAD_X, pady=FRAME_PAD_Y)

        self.__problems_frame.grid(row=1, column=0, sticky=tk.NSEW, padx=FRAME_PAD_X, pady=[0, FRAME_PAD_Y])
        self.__problems_text_label.grid(row=0, column=0, sticky=tk.W + tk.NS)
        self.__problems_webiste_label.grid(row=0, column=1, sticky=tk.W + tk.NS)

        for (tab_frame, tab_scrollbar, tab_text) in self.__tabs_widgets:
            tab_scrollbar.grid(row=0, column=1, sticky=tk.NSEW)
            tab_text.grid(row=0, column=0, sticky=tk.NSEW, pady=[NOTEPAD_TOP_PADY_Y, 0])
            tab_frame.columnconfigure(0, weight=1)
            tab_frame.rowconfigure(0, weight=1)

        self.__main_frame.columnconfigure(0, weight=1)
        self.__main_frame.rowconfigure(0, weight=1)

        self.__problems_frame.columnconfigure(1, weight=1)

        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)



    @staticmethod
    def get_tabs():
        with open(HELP_INPUT_FILE_PATH, 'r', encoding='utf-8') as file:
            help_text = file.read()
            matches = re.findall(f'({TAB_RE})', help_text)
            for i, match in enumerate(matches):
                index = help_text.index(match[0])
                if len(matches) >= i + 2:   # There is a next element
                    next_index = help_text.index(matches[i+1][0])
                    tab_text = help_text[index+len(match[0]):next_index-1]
                else:
                    tab_text = help_text[index+len(match[0]):]
                yield match[1], tab_text.lstrip()

    @staticmethod
    def __format_text(text_widget: tk.Text, text: str):
        extracted_text, tags_dict = parse_text(text)
        text_widget.insert(1.0, extracted_text)
        for key, list_ in tags_dict.items():
            for start, len_ in list_:
                text_widget.tag_add(key, f'1.0+{start}c', f'1.0+{start+len_}c')

    @staticmethod
    def __configure_tags(text_widget: tk.Text):
        text_widget.tag_configure('b', font=FONT_BOLD)
        text_widget.tag_configure('u', font=FONT_UNDERLINE)
        text_widget.tag_configure('i', font=FONT_ITALIC)
        text_widget.tag_configure('h', font=HEADER_FONT)
        text_widget.tag_configure('color', foreground=ADDITIONAL_COLOR_PRIMARY, font=FONT_BOLD)
        text_widget.tag_configure('code', font=CODE_FONT)
        text_widget.tag_configure('title', font=TITLE_FONT)
