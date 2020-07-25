from typing import List, Optional
import tkinter as tk
from tkinter import ttk

from model.port import Port
from state import State
from view.abstract.has_common_setup import HasCommonSetup
from view.abstract.window import Window
from view.scrollbars_listbox import ScrollbarListbox
from view.tree_view_column import Column
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
        self.__ports_left_listbox = ScrollbarListbox(self._window,  values=self.__ports_left,
                                                     extract_id=lambda prt: prt.id_,
                                                     extract_text=lambda prt: prt.name,
                                                     on_select_callback=self.__on_select_listbox_left,
                                                     columns=[Column('#0', 'Port', stretch=tk.YES)])
        self.__mid_frame = ttk.Frame(self._window)

        self.__remove_port_button = ttk.Button(self.__mid_frame, text='<<', command=self.__remove_from_selected)
        self.__add_port_button = ttk.Button(self.__mid_frame, text='>>', command=self.__add_to_selected)

        self.__right_frame = ttk.Frame(self._window)
        # self.__selected_ports_label = ttk.Label(self.__right_frame, text='Selected ports:', style='Big.TLabel',
        #                                        anchor=tk.CENTER)
        self.__ports_right_listbox = ScrollbarListbox(self.__right_frame, values=self.__ports_right,
                                                      extract_id=lambda prt: prt.id_,
                                                      extract_text=lambda prt: prt.name,
                                                      on_select_callback=self.__on_select_listbox_right,
                                                      columns=[Column('#0', 'Selected ports', stretch=tk.YES)])
        self.__buttons_frame = ttk.Frame(self.__right_frame)
        self.__ok_button = ttk.Button(self.__buttons_frame, text='Ok', command=self.__ok)
        self.__cancel_button = ttk.Button(self.__buttons_frame, text='Cancel', command=self._window.destroy)

    def _setup_layout(self) -> None:
        self.__ports_left_listbox.grid(row=0, column=0, sticky=tk.NSEW, padx=FRAME_PAD_X, pady=FRAME_PAD_Y)
        self.__mid_frame.grid(row=0, column=1)
        self.__remove_port_button.grid(row=1, column=0, pady=CONTROL_PAD_Y)
        self.__add_port_button.grid(row=2, column=0, pady=CONTROL_PAD_Y)

        self.__right_frame.grid(row=0, column=2, sticky=tk.NSEW, padx=FRAME_PAD_X, pady=FRAME_PAD_Y)
        # self.__selected_ports_label.grid(row=0, column=0, sticky=tk.EW, pady=CONTROL_PAD_Y)
        self.__ports_right_listbox.grid(row=0, column=0, sticky=tk.NSEW, pady=CONTROL_PAD_Y)
        self.__buttons_frame.grid(row=2, column=0, sticky=tk.NSEW)
        self.__ok_button.grid(row=0, column=0, sticky=tk.NSEW, pady=CONTROL_PAD_Y)
        self.__cancel_button.grid(row=0, column=1, sticky=tk.NSEW, pady=CONTROL_PAD_Y)

        self.__right_frame.grid_columnconfigure(0, weight=1)
        self.__right_frame.grid_rowconfigure(0, weight=1)

        self._window.rowconfigure(0, weight=1)
        self._window.columnconfigure(0, weight=2, uniform='fred')
        self._window.columnconfigure(1, weight=1, uniform='fred')
        self._window.columnconfigure(2, weight=2, uniform='fred')

        self.__buttons_frame.columnconfigure(0, weight=1)
        self.__buttons_frame.columnconfigure(1, weight=1)

        self._set_geometry()

    def __on_select_listbox_left(self, id_: int) -> None:
        self.__selected_port_left = self.__state.model.get_port_by_id(id_)

    def __on_select_listbox_right(self, id_: int) -> None:
        self.__selected_port_right = self.__state.model.get_port_by_id(id_)

    def __add_to_selected(self):
        if self.__selected_port_left:
            prt = self.__selected_port_left
            self.__ports_left.remove(prt)
            self.__ports_left_listbox.remove_item(prt)
            self.__selected_port_left = None
            self.__ports_right.append(prt)
            # TODO: sort objects maybe?
            right_port_names = sorted([p.name for p in self.__ports_right])
            index = right_port_names.index(prt.name)
            self.__ports_right_listbox.add_item(prt, index=index)
            self.__ports_right_listbox.select_item(prt)

    def __remove_from_selected(self):
        if self.__selected_port_right:
            prt = self.__selected_port_right
            self.__ports_right.remove(prt)
            self.__ports_right_listbox.remove_item(prt)
            self.__selected_port_right = None
            self.__ports_left.append(prt)
            # TODO: sort objects maybe?
            left_port_names = sorted([p.name for p in self.__ports_left])
            index = left_port_names.index(prt.name)
            self.__ports_left_listbox.add_item(prt, index=index)
            self.__ports_left_listbox.select_item(prt)

    def __ok(self):
        self._window.grab_release()
        self.__callback(self.__ports_right)
        self._window.destroy()
