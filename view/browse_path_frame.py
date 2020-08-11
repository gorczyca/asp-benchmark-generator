import os
import tkinter as tk
from tkinter import ttk, filedialog

from view.abstract.has_common_setup import HasCommonSetup
from view.style import CONTROL_PAD_Y, CONTROL_PAD_X


class BrowsePathFrame(ttk.Frame,
                      HasCommonSetup):
    def __init__(self, parent_frame, path: str = '', widget_label_text: str = '', default_extension: str = '', **kwargs):
        ttk.Frame.__init__(self, parent_frame, **kwargs)

        self.__path = path
        self.__widget_label_text = widget_label_text
        self.__default_extension = default_extension

        HasCommonSetup.__init__(self)

    def _create_widgets(self) -> None:
        self.__widget_label = ttk.Label(self, text=self.__widget_label_text)
        self.__browse_file_button = ttk.Button(self, text='Browse...', command=self.__on_browse_path)
        self.__generate_to_path_label_var = tk.StringVar(value=self.__path)
        self.__generate_to_path_label = ttk.Label(self, textvariable=self.__generate_to_path_label_var,
                                                  style='Bold.TLabel')

    def _setup_layout(self) -> None:
        self.__widget_label.grid(row=0, column=0, sticky=tk.W, pady=CONTROL_PAD_Y, padx=CONTROL_PAD_X)
        self.__browse_file_button.grid(row=0, column=1, sticky=tk.E, pady=CONTROL_PAD_Y, padx=CONTROL_PAD_X)
        self.__generate_to_path_label.grid(row=1, column=0, columnspan=2, sticky=tk.EW, pady=CONTROL_PAD_Y, padx=CONTROL_PAD_X)

        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)

    def __on_browse_path(self):
        # TODO:
        # filename = tkFileDialog.asksaveasfilename(defaultextension=".espace",
        #                                           filetypes=(("espace file", "*.espace"), ("All Files", "*.*")))
        file_path = filedialog.asksaveasfilename(defaultextension=self.__default_extension, parent=self)
        if file_path:
            file_path = os.path.normpath(file_path)
            self.__generate_to_path_label_var.set(file_path)


