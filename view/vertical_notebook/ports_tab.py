from typing import Optional, Any, Tuple, List
import tkinter as tk
from tkinter import ttk, simpledialog, messagebox

from pubsub import pub

import actions
from exceptions import PortError
from model.port import Port
from model.component import Component
from view.abstract.has_common_setup import HasCommonSetup
from view.abstract.has_controller_access import HasControllerAccess
from view.abstract.resetable import Resetable
from view.abstract.subscribes_to_listeners import SubscribesToListeners
from view.abstract.tab import Tab
from view.scrollbars_listbox import ScrollbarListbox
from view.select_components_window import SelectComponentsWindow
from view.tree_view_column import Column

TAB_NAME = 'Ports'


class PortsTab(Tab,
               HasControllerAccess,
               HasCommonSetup,
               SubscribesToListeners,
               Resetable):
    def __init__(self, parent, parent_notebook, *args, **kwargs):
        Tab.__init__(self, parent_notebook, TAB_NAME, *args, **kwargs)
        HasControllerAccess.__init__(self, parent)

        HasCommonSetup.__init__(self)
        SubscribesToListeners.__init__(self)

        self.__ports_listbox: Optional[ScrollbarListbox] = None
        self.__selected_port: Optional[Port] = None
        self.__build_ports_listbox()

    # HasCommonSetup
    def _create_widgets(self) -> None:
        self.__right_frame = tk.Frame(self.frame)
        self.__right_top_frame = tk.Frame(self.__right_frame)
        # Port label
        self.__port_label_var = tk.StringVar(value='PORT')
        self.__port_label = ttk.Label(self.__right_top_frame, textvariable=self.__port_label_var, style='Big.TLabel')
        # C(r)ud Buttons
        self.__add_port_button = ttk.Button(self.__right_top_frame, text='Add', state=tk.NORMAL, command=self.__add_port)
        self.__rename_port_button = ttk.Button(self.__right_top_frame, text='Rename', state=tk.DISABLED,
                                               command=self.__rename_port)
        self.__remove_port_button = ttk.Button(self.__right_top_frame, text='Remove', state=tk.DISABLED,
                                               command=self.__remove_port)

        self.__right_mid_frame = tk.Frame(self.__right_frame)
        self.__right_mid_left_frame = tk.Frame(self.__right_mid_frame)
        self.__right_mid_right_frame = tk.Frame(self.__right_mid_frame)

        self.__occurs_in_label = ttk.Label(self.__right_mid_frame, text='Occurs in:', style='Big.TLabel')
        self.__occurs_in_edit_button = ttk.Button(self.__right_mid_left_frame, text='Edit', command=self.__edit_occurs_in)

        # Occurs in
        self.__occurs_in_listbox = ScrollbarListbox(self.__right_mid_left_frame,
                                                    columns=[Column('#0', 'Port', stretch=tk.YES),
                                                             Column('amount', 'Amount')],
                                                    on_select_callback=self.__on_select_ports_listbox_item,
                                                    extract_values=self.__extract_values_occurs_in_listbox_item,
                                                    extract_id=lambda cmp: cmp.id_,
                                                    extract_text=lambda cmp: cmp.name)
        self.__selected_component_label = ttk.Label(self.__right_mid_right_frame, text='COMPONENT', style='Big.TLabel')
        # Compatible with
        self.__right_bot_frame = tk.Frame(self.__right_frame)
        self.__compatible_with_label = ttk.Label(self.__right_bot_frame, text='Compatible with:', style='Big.TLabel')
        self.__compatible_with_listbox = ScrollbarListbox(self.__right_bot_frame, grid_row=1, grid_column=0,
                                                          columns=[Column('#0', 'Port', stretch=tk.YES)])
        self.__compatible_with_edit_button = ttk.Button(self.__right_bot_frame, text='Edit',
                                                        command=self.__edit_compatible_with)

    def _setup_layout(self) -> None:
        self.__right_frame.grid(row=0, column=1, sticky=tk.NSEW)
        self.__right_top_frame.grid(row=0, column=0, sticky=tk.NSEW)

        self.__port_label.grid(row=0, column=0)

        self.__add_port_button.grid(row=1, column=0)
        self.__rename_port_button.grid(row=1, column=1)
        self.__remove_port_button.grid(row=1, column=2)

        self.__right_mid_frame.grid(row=1, column=0)
        self.__occurs_in_label.grid(row=0, column=0, columnspan=2)
        self.__right_mid_left_frame.grid(row=1, column=0)
        self.__occurs_in_edit_button.grid(row=2, column=0)

        self.__right_mid_right_frame.grid(row=1, column=1)
        self.__selected_component_label.grid(row=0, column=0)

        self.__right_bot_frame.grid(row=2, column=0)
        self.__compatible_with_label.grid(row=0, column=0)
        self.__compatible_with_edit_button.grid(row=2, column=0)

        self.frame.columnconfigure(0, weight=1, uniform='fred')
        self.frame.columnconfigure(1, weight=2, uniform='fred')
        self.frame.rowconfigure(0, weight=1)

    def __on_select_ports_listbox_item(self, id_: int) -> None:
        prt = self.controller.model.get_port_by_id(id_)
        self.__selected_port = prt
        self.__port_label_var.set(prt.name)
        self.__enable_rename_remove_buttons()

    def __build_ports_listbox(self) -> None:
        if self.__ports_listbox:
            pass    # TODO: destroy listbox

        self.__ports_listbox = ScrollbarListbox(self.frame, self.controller.model.ports,
                                                columns=[Column('#0', 'Port', stretch=tk.YES)],
                                                on_select_callback=self.__on_select_ports_listbox_item,
                                                extract_values=lambda prt: (),
                                                extract_id=lambda prt: prt.id_,
                                                extract_text=lambda prt: prt.name)

    # SubscribesToListeners
    def _subscribe_to_listeners(self) -> None:
        pub.subscribe(self._reset, actions.RESET)

    # Resetable
    def _reset(self) -> None:
        pass

    # Class-specific
    # Ports
    def __add_port(self):
        name = simpledialog.askstring('Add port', f'Enter name of the new port.')
        if name:
            try:
                port, index = self.controller.model.add_port(name)
                self.__selected_port = port
                # TODO: consider selecting the port in listbox programmatically
                self.__ports_listbox.add_item(port, index=index)
                self.__port_label_var.set(name)
                self.__enable_rename_remove_buttons()
            except PortError as e:
                messagebox.showerror('Add port error.', e.message)

    def __rename_port(self) -> None:
        new_name = simpledialog.askstring('Rename', f'Enter new name for "{self.__selected_port.name}" port.')
        if new_name:
            try:
                _, index = self.controller.model.change_port_name(self.__selected_port, new_name)
                self.__port_label_var.set(new_name)
                self.__ports_listbox.rename_item(self.__selected_port, index=index)
            except PortError as e:
                messagebox.showerror('Rename error.', e.message)

    def __remove_port(self) -> None:
        if self.__selected_port:
            self.controller.model.remove_port(self.__selected_port)
            self.__disable_rename_remove_buttons()
            self.__right_frame.grid_forget()
            self.__ports_listbox.remove_item(self.__selected_port)

    def __enable_rename_remove_buttons(self):
        self.__rename_port_button.config(state=tk.NORMAL)
        self.__remove_port_button.config(state=tk.NORMAL)

    def __disable_rename_remove_buttons(self):
        self.__rename_port_button.config(state=tk.DISABLED)
        self.__remove_port_button.config(state=tk.DISABLED)

    # Occurs in

    def __on_select_component_listbox_item(self, id_: int) -> None:
        pass

    def __extract_values_occurs_in_listbox_item(self, cmp: Component) -> Any:
        amount = ''
        if self.__selected_port.id_ in cmp.ports:
            amount = cmp.ports[self.__selected_port.id_]
        return amount

    def __edit_occurs_in(self):
        SelectComponentsWindow(self, self.frame, self.controller.model.hierarchy, self.__occurs_in_edited,
                               select_leaf_components_only=True)

    def __edit_compatible_with(self):
        SelectComponentsWindow(self, self.frame, self.controller.model.hierarchy, self.__occurs_in_edited,
                               select_leaf_components_only=True)

    def __occurs_in_edited(self, components: List[Component]):
        pass
