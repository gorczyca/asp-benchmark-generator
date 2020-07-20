from typing import List, Optional
import tkinter as tk
from tkinter import ttk

from model.port import Port
from view.abstract.base_frame import BaseFrame
from view.abstract.has_common_setup import HasCommonSetup
from view.abstract.has_controller_access import HasControllerAccess
from view.scrollbars_listbox import ScrollbarListbox
from view.tree_view_column import Column
from view import style

SELECT_PORTS_WINDOW_NAME = 'Select ports to be compatible with {0}'
SELECT_PORTS_WINDOW_SIZE = '1080x720'

WINDOW_WIDTH_RATIO = 0.75
WINDOW_HEIGHT_RATIO = 0.75

CONTROL_PAD_Y = 3

FRAME_PAD_Y = 10
FRAME_PAD_X = 10


class SelectPortsWindow(BaseFrame,
                        HasControllerAccess,
                        HasCommonSetup):    # TODO: remove these stupid abstract methods
    def __init__(self, parent, parent_frame, selected_port: Port, ports_right, ports_left, callback):
        BaseFrame.__init__(self, parent_frame)
        HasControllerAccess.__init__(self, parent)

        self.__ports_right: List[Port] = ports_right
        self.__ports_left: List[Port] = ports_left
        self.__callback = callback

        self.__selected_port_left: Optional[Port] = None
        self.__selected_port_right: Optional[Port] = None

        self.__window = tk.Toplevel(self.parent_frame, bg=style.BACKGROUND_COLOR_PRIMARY)
        self.__window.grab_set()
        self.__window.title(SELECT_PORTS_WINDOW_NAME.format(selected_port.name))
        self.__set_geometry()
        HasCommonSetup.__init__(self)

    # HasCommonSetup
    def _create_widgets(self) -> None:
        self.__ports_left_listbox = ScrollbarListbox(self.__window,  values=self.__ports_left,
                                                     extract_id=lambda prt: prt.id_,
                                                     extract_text=lambda prt: prt.name,
                                                     on_select_callback=self.__on_select_listbox_left,
                                                     columns=[Column('#0', 'Port', stretch=tk.YES)])
        self.__mid_frame = ttk.Frame(self.__window)

        self.__remove_port_button = ttk.Button(self.__mid_frame, text='<<', command=self.__remove_from_selected)
        self.__add_port_button = ttk.Button(self.__mid_frame, text='>>', command=self.__add_to_selected)

        self.__right_frame = ttk.Frame(self.__window)
        # self.__selected_ports_label = ttk.Label(self.__right_frame, text='Selected ports:', style='Big.TLabel',
        #                                        anchor=tk.CENTER)
        self.__ports_right_listbox = ScrollbarListbox(self.__right_frame, values=self.__ports_right,
                                                      extract_id=lambda prt: prt.id_,
                                                      extract_text=lambda prt: prt.name,
                                                      on_select_callback=self.__on_select_listbox_right,
                                                      columns=[Column('#0', 'Selected ports', stretch=tk.YES)])
        self.__buttons_frame = ttk.Frame(self.__right_frame)
        self.__ok_button = ttk.Button(self.__buttons_frame, text='Ok', command=self.__ok)
        self.__cancel_button = ttk.Button(self.__buttons_frame, text='Cancel', command=self.__window.destroy)

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

        self.__window.rowconfigure(0, weight=1)
        self.__window.columnconfigure(0, weight=2, uniform='fred')
        self.__window.columnconfigure(1, weight=1, uniform='fred')
        self.__window.columnconfigure(2, weight=2, uniform='fred')

        self.__buttons_frame.columnconfigure(0, weight=1)
        self.__buttons_frame.columnconfigure(1, weight=1)

    def __on_select_listbox_left(self, id_: int) -> None:
        self.__selected_port_left = self.controller.model.get_port_by_id(id_)

    def __on_select_listbox_right(self, id_: int) -> None:
        self.__selected_port_right = self.controller.model.get_port_by_id(id_)

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
        self.__window.grab_release()
        self.__callback(self.__ports_right)
        self.__window.destroy()

    # TODO: make a base class for all windows
    def __set_geometry(self):
        screen_width = self.__window.winfo_screenwidth()
        screen_height = self.__window.winfo_screenheight()
        window_width = round(screen_width * WINDOW_WIDTH_RATIO)
        window_height = round(screen_height * WINDOW_HEIGHT_RATIO)
        x_pos = round((screen_width - window_width) / 2)
        y_pos = round((screen_height - window_height) / 2)
        self.__window.geometry(f'{window_width}x{window_height}+{x_pos}+{y_pos}')
