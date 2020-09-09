import os
import tkinter as tk
from tkinter import ttk, filedialog

from file_operations import ALL_FILES_TYPE
from view.abstract import HasCommonSetup
from view.style import CONTROL_PAD_Y, CONTROL_PAD_X


SELECT_PATH_STRING = '(Select file path)'


class BrowseFilePathFrame(ttk.Frame,
                          HasCommonSetup):
    def __init__(self, parent_frame,
                 path: str = None,
                 widget_label_text: str = '',
                 default_extension: str = '',
                 initial_file: str = '',
                 title: str = '',
                 save: bool = True,
                 **kwargs):
        ttk.Frame.__init__(self, parent_frame, **kwargs)

        self.__path = path
        self.__widget_label_text = widget_label_text
        self.__default_extension = default_extension
        self.__save = save
        self.__initial_file = initial_file
        self.__title = title if title else 'Save as:' if save else 'Open as:'

        HasCommonSetup.__init__(self)

    def _create_widgets(self) -> None:
        self.__widget_label = ttk.Label(self, text=self.__widget_label_text)
        self.__browse_file_button = ttk.Button(self, text='Browse...', command=self.__on_browse_path)
        path_label_var = SELECT_PATH_STRING if not self.__path else os.path.normpath(self.__path)
        self.__path_label_var = tk.StringVar(value=path_label_var)
        self.__path_label = ttk.Label(self, textvariable=self.__path_label_var,
                                      style='Bold.TLabel')

    def _setup_layout(self) -> None:
        self.__widget_label.grid(row=0, column=0, sticky=tk.W, pady=CONTROL_PAD_Y, padx=CONTROL_PAD_X)
        self.__browse_file_button.grid(row=0, column=1, sticky=tk.E, pady=CONTROL_PAD_Y, padx=CONTROL_PAD_X)
        self.__path_label.grid(row=1, column=0, columnspan=2, sticky=tk.EW, pady=CONTROL_PAD_Y, padx=CONTROL_PAD_X)

        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)

    def __on_browse_path(self):
        if self.__save:
            file_path = filedialog.asksaveasfilename(defaultextension=self.__default_extension,
                                                     filetypes=((f'{self.__default_extension} file', f'*{self.__default_extension}'), ALL_FILES_TYPE),
                                                     initialfile=self.__initial_file, title=self.__title,
                                                     parent=self)
        else:
            file_path = filedialog.askopenfilename(filetypes=((f'{self.__default_extension} file', f'*{self.__default_extension}'), ALL_FILES_TYPE),
                                                   title=self.__title,
                                                   parent=self)
        if file_path:
            self.__path = file_path
            norm_file_path = os.path.normpath(file_path)
            self.__path_label_var.set(norm_file_path)

    @property
    def path(self) -> str:
        return self.__path

    def change_state(self, state):
        self.__browse_file_button.config(state=state)


