import os
import tkinter as tk
from tkinter import ttk, filedialog
from typing import Optional

from file_operations import ALL_FILES_TYPE
from view.abstract import HasCommonSetup
from view.style import CONTROL_PAD_Y, CONTROL_PAD_X


SELECT_PATH_STRING = '(Select file path)'


class BrowseFilePathFrame(ttk.Frame,
                          HasCommonSetup):
    """Reusable frame to obtain the file path.

    Attributes:
        __path: File path.
            The parameter passed to it is the string obtained from this window.
        __widget_label_text: Text to be displayed in the frame.
        __default_extension: File's default extension.
        __save: If True then show save file dialog; otherwise show open file dialog.
        __title: (ask file) Window's title.
    """
    def __init__(self,
                 parent_frame: ttk.Frame,
                 path: Optional[str] = None,
                 widget_label_text: str = '',
                 default_extension: str = '',
                 title: str = '',
                 save: bool = True,
                 **kwargs):
        ttk.Frame.__init__(self, parent_frame, **kwargs)
        self.__path = path
        self.__widget_label_text = widget_label_text
        self.__default_extension = default_extension
        self.__save = save
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
        """Executed whenever __browse_file_button is pressed."""
        if self.__save:
            file_path = filedialog.asksaveasfilename(defaultextension=self.__default_extension,
                                                     filetypes=((f'{self.__default_extension} file', f'*{self.__default_extension}'), ALL_FILES_TYPE),
                                                     initialfile=self.__path, title=self.__title,
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
        """Returns the file path."""
        return self.__path

    def change_state(self, state):
        """Changes widgets' state.

        :param state: Desired state of the widgets (tk.NORMAL or tk.DISABLED).
        """
        self.__browse_file_button.config(state=state)


