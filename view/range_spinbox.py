import tkinter as tk
from tkinter import ttk
import math

from view.abstract.has_common_setup import HasCommonSetup


class RangeSpinbox(ttk.Frame,
                   HasCommonSetup):
    def __init__(self, parent_frame):
        ttk.Frame.__init__(self, parent_frame)
        HasCommonSetup.__init__(self)

    def _create_widgets(self) -> None:
        self.__exact_value_radiobutton_var = tk.BooleanVar()
        self.__exact_value_radiobutton_var.trace('w', self.__on_radiobutton_changed)
        self.__exact_value_radiobutton = ttk.Radiobutton(self, text='Exact', variable=self.__exact_value_radiobutton_var, value=True)
        self.__range_radiobutton = ttk.Radiobutton(self, text='Range', variable=self.__exact_value_radiobutton_var, value=False)

        self.__exact_min_value_spinbox_var = tk.IntVar()
        self.__exact_min_value_spinbox_var.trace('w', self.__on_exact_min_value_changed)
        self.__exact_min_value_spinbox = ttk.Spinbox(self, from_=0, to=math.inf, textvariable=self.__exact_min_value_spinbox_var)
        self.__max_value_spinbox_var = tk.IntVar()
        self.__max_value_spinbox_var.trace('w', self.__on_max_value_changed)
        self.__max_value_spinbox = ttk.Spinbox(self, from_=0, to=math.inf, textvariable=self.__max_value_spinbox_var)

    def _setup_layout(self) -> None:
        self.__exact_value_radiobutton.grid(row=0, column=0)
        self.__range_radiobutton.grid(row=0, column=1)

        self.__exact_min_value_spinbox.grid(row=1, column=0)
        self.__max_value_spinbox.grid(row=1, column=1)

    def __on_radiobutton_changed(self, *_):
        value = self.__exact_value_radiobutton_var.get()
        if value:
            pass

    def __on_exact_min_value_changed(self, *_):
        min_value = self.__exact_min_value_spinbox_var.get()
        if not self.__exact_value_radiobutton_var.get():    # If there is also a 'max' spinbox
            max_value = self.__max_value_spinbox_var.get()
            if min_value > max_value:
                self.__max_value_spinbox_var.set(min_value)

    def __on_max_value_changed(self, *_):
        max_value = self.__max_value_spinbox_var.get()
        min_value = self.__exact_min_value_spinbox_var.get()
        if max_value < min_value:
            self.__exact_min_value_spinbox_var.set(max_value)

