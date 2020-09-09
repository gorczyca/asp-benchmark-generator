from typing import List, Optional
import tkinter as tk
from tkinter import ttk

from model import Port
from state import State
from view import ScrollbarListbox, Column
from view.abstract import HasCommonSetup, Window
from view.style import FRAME_PAD_X, FRAME_PAD_Y, CONTROL_PAD_Y

WINDOW_TITLE = 'Select ports to be compatible with {0}'


class SelectPortsWindow(HasCommonSetup,
                        Window):
    def __init__(self, parent_frame, selected_port: Port, ports_right, ports_left, callback):
        self.__state = State()
        self.__callback = callback

        self.__ports_right: List[Port] = ports_right
        self.__ports_left: List[Port] = ports_left

        self.__selected_port_left: Optional[Port] = None
        self.__selected_port_right: Optional[Port] = None

        Window.__init__(self, parent_frame, WINDOW_TITLE.format(selected_port.name))
        HasCommonSetup.__init__(self)

    # HasCommonSetup
    def _create_widgets(self) -> None:
        self.__ports_left_listbox = ScrollbarListbox(self, values=self.__ports_left,
                                                     extract_id=lambda prt: prt.id_,
                                                     extract_text=lambda prt: prt.name,
                                                     on_select_callback=self.__on_select_listbox_left,
                                                     columns=[Column('Port', main=True, stretch=tk.YES)])
        self.__mid_frame = ttk.Frame(self)

        self.__remove_port_button = ttk.Button(self.__mid_frame, text='<<', command=self.__remove_from_selected)
        self.__add_port_button = ttk.Button(self.__mid_frame, text='>>', command=self.__add_to_selected)

        self.__right_frame = ttk.Frame(self)
        self.__ports_right_listbox = ScrollbarListbox(self.__right_frame, values=self.__ports_right,
                                                      extract_id=lambda prt: prt.id_,
                                                      extract_text=lambda prt: prt.name,
                                                      on_select_callback=self.__on_select_listbox_right,
                                                      columns=[Column('Selected ports', main=True, stretch=tk.YES)])
        self.__buttons_frame = ttk.Frame(self.__right_frame)
        self.__ok_button = ttk.Button(self.__buttons_frame, text='Ok', command=self.__ok)
        self.__cancel_button = ttk.Button(self.__buttons_frame, text='Cancel', command=self.destroy)

    def _setup_layout(self) -> None:
        self.__ports_left_listbox.grid(row=0, column=0, sticky=tk.NSEW, padx=FRAME_PAD_X, pady=FRAME_PAD_Y)
        self.__mid_frame.grid(row=0, column=1)
        self.__remove_port_button.grid(row=1, column=0, pady=CONTROL_PAD_Y)
        self.__add_port_button.grid(row=2, column=0, pady=CONTROL_PAD_Y)

        self.__right_frame.grid(row=0, column=2, sticky=tk.NSEW, padx=FRAME_PAD_X, pady=FRAME_PAD_Y)
        self.__ports_right_listbox.grid(row=0, column=0, sticky=tk.NSEW, pady=CONTROL_PAD_Y)
        self.__buttons_frame.grid(row=2, column=0, sticky=tk.NSEW)
        self.__ok_button.grid(row=0, column=0, sticky=tk.NSEW, pady=CONTROL_PAD_Y)
        self.__cancel_button.grid(row=0, column=1, sticky=tk.NSEW, pady=CONTROL_PAD_Y)

        self.__right_frame.grid_columnconfigure(0, weight=1)
        self.__right_frame.grid_rowconfigure(0, weight=1)

        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=2, uniform='fred')
        self.columnconfigure(1, weight=1, uniform='fred')
        self.columnconfigure(2, weight=2, uniform='fred')

        self.__buttons_frame.columnconfigure(0, weight=1)
        self.__buttons_frame.columnconfigure(1, weight=1)

        self._set_geometry()

    def __on_select_listbox_left(self, prt_id: int) -> None:
        self.__selected_port_left = self.__state.model.get_port(id_=prt_id)

    def __on_select_listbox_right(self, prt_id: int) -> None:
        self.__selected_port_right = self.__state.model.get_port(id_=prt_id)

    def __add_to_selected(self):
        if self.__selected_port_left:
            prt = self.__selected_port_left
            self.__ports_left.remove(prt)
            self.__ports_left_listbox.remove_item_recursively(prt)
            self.__selected_port_left = None
            self.__ports_right.append(prt)
            self.__selected_port_right = prt
            right_port_names = sorted([p.name for p in self.__ports_right])
            index = right_port_names.index(prt.name)
            self.__ports_right_listbox.add_item(prt, index=index)

    def __remove_from_selected(self):
        if self.__selected_port_right:
            prt = self.__selected_port_right
            self.__ports_right.remove(prt)
            self.__ports_right_listbox.remove_item_recursively(prt)
            self.__selected_port_right = None
            self.__ports_left.append(prt)
            self.__selected_port_left = prt
            left_port_names = sorted([p.name for p in self.__ports_left])
            index = left_port_names.index(prt.name)
            self.__ports_left_listbox.add_item(prt, index=index)

    def __ok(self):
        self.grab_release()
        self.__callback(self.__ports_right)
        self.destroy()
