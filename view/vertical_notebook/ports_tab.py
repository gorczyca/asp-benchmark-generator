import math
import tkinter as tk
from typing import Optional, Any, Tuple, List
from tkinter import ttk, simpledialog, messagebox

from pubsub import pub

import actions
from exceptions import BGError
from model.port import Port
from model.component import Component
from state import State
from view.abstract.has_common_setup import HasCommonSetup
from view.abstract.resetable import Resetable
from view.abstract.subscribes_to_events import SubscribesToEvents
from view.abstract.tab import Tab
from view.scrollbars_listbox import ScrollbarListbox
from view.select_ports_window import SelectPortsWindow
from view.tree_view_column import Column
from view.style import FONT
from view.common import trim_string, change_controls_state

TAB_NAME = 'Ports'
SELECT_PORT = '(select port)'
TREEVIEW_HEADING = 'Component'

CONTROL_PAD_Y = 3

FRAME_PAD_Y = 10
FRAME_PAD_X = 10


class PortsTab(Tab,
               HasCommonSetup,
               SubscribesToEvents,
               Resetable):
    def __init__(self, parent_notebook):
        self.__state = State()

        self.__ports_listbox: Optional[ScrollbarListbox] = None
        self.__selected_port: Optional[Port] = None
        self.__selected_component: Optional[Component] = None

        Tab.__init__(self, parent_notebook, TAB_NAME)
        HasCommonSetup.__init__(self)
        SubscribesToEvents.__init__(self)

    # HasCommonSetup
    def _create_widgets(self) -> None:
        self.__hierarchy_tree = ScrollbarListbox(self._frame,
                                                 on_select_callback=self.__on_select_tree_item,
                                                 heading=TREEVIEW_HEADING,
                                                 extract_id=lambda x: x.id_,
                                                 extract_text=lambda x: x.name,
                                                 extract_ancestor=lambda x: '' if x.parent_id is None else x.parent_id,
                                                 extract_values=self.__extract_values,
                                                 columns=[Column('amount', 'Amount')]
                                                 )
        self.__left_frame = ttk.Frame(self._frame)

        # Ports combobox
        self.__port_combobox_var = tk.StringVar(value=SELECT_PORT)
        self.__port_combobox_var.trace('w', self.__on_combobox_changed)
        # state='readonly' means you cannot write freely in the combobox
        self.__port_combobox = ttk.Combobox(self.__left_frame, state='readonly',
                                            textvariable=self.__port_combobox_var, font=FONT)
        # C(r)ud Buttons
        self.__add_port_button = ttk.Button(self.__left_frame, text='Add', state=tk.NORMAL,
                                            command=self.__add_port)
        self.__rename_port_button = ttk.Button(self.__left_frame, text='Rename', state=tk.DISABLED,
                                               command=self.__rename_port)
        self.__remove_port_button = ttk.Button(self.__left_frame, text='Remove', state=tk.DISABLED,
                                               command=self.__remove_port)
        # Force connection
        self.__force_connection_checkbox_var = tk.BooleanVar(value=False)
        self.__force_connection_checkbox_var.trace('w', self.__on_force_connection_toggled)
        self.__force_connection_checkbox_label = ttk.Label(self.__left_frame,
                                                           text='Force connection:')
        self.__force_connection_checkbox = ttk.Checkbutton(self.__left_frame, state=tk.DISABLED,
                                                           variable=self.__force_connection_checkbox_var)
        # Force connection checkbox
        self.__compatible_with_edit_button = ttk.Button(self.__left_frame, text='Edit compatibility',
                                                        command=self.__edit_compatible_with, state=tk.DISABLED)
        self.__compatible_with_listbox = ScrollbarListbox(self.__left_frame,
                                                          # grid_row=6, grid_column=0, column_span=2,
                                                          extract_text=lambda prt: prt.name,
                                                          extract_id=lambda prt: prt.id_,
                                                          columns=[Column('#0', 'Compatible with', stretch=tk.YES)])
        self.__cmp_label_var = tk.StringVar(value='')
        self.__cmp_label = ttk.Label(self.__left_frame, textvariable=self.__cmp_label_var, style='Big.TLabel', anchor=tk.CENTER)

        self.__amount_spinbox_label = ttk.Label(self.__left_frame, text='Has:')
        self.__amount_spinbox_var = tk.IntVar(value='')
        self.__amount_spinbox_var.trace('w', self.__on_amount_changed)
        self.__amount_spinbox = ttk.Spinbox(self.__left_frame, from_=0, to=math.inf,
                                            textvariable=self.__amount_spinbox_var)

        self.__all_children_amount_spinbox_label = ttk.Label(self.__left_frame, text='Children have:')
        self.__all_children_amount_spinbox_var = tk.IntVar(value='')
        self.__all_children_amount_spinbox = ttk.Spinbox(self.__left_frame, from_=0, to=math.inf,
                                                         textvariable=self.__all_children_amount_spinbox_var)
        self.__apply_to_all_children_button = ttk.Button(self.__left_frame, text='Apply to all children',
                                                         command=self.__apply_to_all_children)

    def _setup_layout(self) -> None:
        self.__hierarchy_tree.grid(row=0, column=1, sticky=tk.NSEW)
        self.__left_frame.grid(row=0, column=0, sticky=tk.NSEW, pady=FRAME_PAD_Y, padx=FRAME_PAD_X)

        self.__port_combobox.grid(row=0, column=0, columnspan=2, sticky=tk.NSEW, pady=CONTROL_PAD_Y)
        self.__add_port_button.grid(row=1, column=0, columnspan=2, sticky=tk.NSEW, pady=CONTROL_PAD_Y)
        self.__rename_port_button.grid(row=2, column=0, columnspan=2, sticky=tk.NSEW, pady=CONTROL_PAD_Y)
        self.__remove_port_button.grid(row=3, column=0, columnspan=2, sticky=tk.NSEW, pady=CONTROL_PAD_Y)
        self.__force_connection_checkbox_label.grid(row=4, column=0, sticky=tk.W, pady=CONTROL_PAD_Y)
        self.__force_connection_checkbox.grid(row=4, column=1, sticky=tk.E, pady=CONTROL_PAD_Y)
        self.__compatible_with_edit_button.grid(row=5, column=0, columnspan=2, sticky=tk.NSEW, pady=CONTROL_PAD_Y)
        self.__compatible_with_listbox.grid(row=6, column=0, columnspan=2, sticky=tk.NSEW, pady=CONTROL_PAD_Y)

        self.__cmp_label.grid(row=7, column=0, columnspan=2, pady=CONTROL_PAD_Y, sticky=tk.EW)
        self.__amount_spinbox_label.grid(row=8, column=0, pady=CONTROL_PAD_Y, sticky=tk.W)
        self.__amount_spinbox.grid(row=8, column=1, pady=CONTROL_PAD_Y, sticky=tk.NSEW)

        self.__all_children_amount_spinbox_label.grid(row=8, column=0, pady=CONTROL_PAD_Y, sticky=tk.W)
        self.__all_children_amount_spinbox.grid(row=8, column=1, pady=CONTROL_PAD_Y, sticky=tk.NSEW)
        self.__apply_to_all_children_button.grid(row=9, column=0, columnspan=2, sticky=tk.NSEW, pady=CONTROL_PAD_Y)

        self._frame.columnconfigure(1, weight=1)     # Give all the remaining space to hierarchy tree
        self._frame.rowconfigure(0, weight=1)

        self.__left_frame.columnconfigure(1, weight=1)

        # Hide widgets
        self.__cmp_label.grid_forget()
        self.__amount_spinbox_label.grid_forget()
        self.__amount_spinbox.grid_forget()
        self.__all_children_amount_spinbox_label.grid_forget()
        self.__all_children_amount_spinbox.grid_forget()
        self.__apply_to_all_children_button.grid_forget()

    # HasHierarchyTree
    def __on_select_tree_item(self, cmp_id: int) -> None:
        if self.__selected_port:
            selected_cmp = self.__state.model.get_component_by_id(cmp_id)
            self.__selected_component = selected_cmp

            self.__cmp_label.grid(row=7, column=0, columnspan=2, pady=CONTROL_PAD_Y, sticky=tk.EW)  # Show cmp label
            self.__cmp_label_var.set(trim_string(selected_cmp.name))    # Fill the label with component name

            if selected_cmp.is_leaf:
                self.__all_children_amount_spinbox_label.grid_forget()  # Hide widgets (changing all children)
                self.__all_children_amount_spinbox.grid_forget()
                self.__apply_to_all_children_button.grid_forget()
                self.__all_children_amount_spinbox_var.set(0)
                amount = 0
                if self.__selected_port.id_ in selected_cmp.ports:
                    amount = selected_cmp.ports[self.__selected_port.id_]
                self.__amount_spinbox_var.set(amount)
                self.__amount_spinbox_label.grid(row=8, column=0, pady=CONTROL_PAD_Y, sticky=tk.W)  # Show widgets for leaves
                self.__amount_spinbox.grid(row=8, column=1, pady=CONTROL_PAD_Y, sticky=tk.NSEW)
            else:
                self.__amount_spinbox_label.grid_forget()   # Hide widgets for leaves
                self.__amount_spinbox.grid_forget()

                self.__all_children_amount_spinbox_label.grid(row=8, column=0, pady=CONTROL_PAD_Y, sticky=tk.W) # Show widgets (changing all children)
                self.__all_children_amount_spinbox.grid(row=8, column=1, pady=CONTROL_PAD_Y, sticky=tk.NSEW)
                self.__apply_to_all_children_button.grid(row=9, column=0, columnspan=2, sticky=tk.NSEW,
                                                         pady=CONTROL_PAD_Y)

    def __extract_values(self, cmp: Component) -> Tuple[Any, ...]:
        amount = ''
        if self.__selected_port:
            if self.__selected_port.id_ in cmp.ports:
                amount = cmp.ports[self.__selected_port.id_]
        return amount,

    def __build_tree(self) -> None:
        self.__hierarchy_tree.set_items(self.__state.model.hierarchy)

    def __on_hierarchy_changed(self):
        self._reset()
        self.__build_tree()

    def __on_combobox_changed(self, _1, _2, _3):
        # Hide component-specific widgets
        self.__cmp_label.grid_forget()
        self.__amount_spinbox_label.grid_forget()
        self.__amount_spinbox.grid_forget()
        self.__all_children_amount_spinbox_label.grid_forget()
        self.__all_children_amount_spinbox.grid_forget()
        self.__apply_to_all_children_button.grid_forget()

        prt_name = self.__port_combobox_var.get()
        port = self.__state.model.get_port_by_name(prt_name)
        buttons_to_change_state_of = [
            self.__rename_port_button,
            self.__remove_port_button,
            self.__force_connection_checkbox,
            self.__compatible_with_edit_button,
        ]
        if port:
            self.__selected_port = port
            change_controls_state(tk.NORMAL, *buttons_to_change_state_of)
            compatible_ports = self.__state.model.get_ports_by_ids(port.compatible_with)
            self.__compatible_with_listbox.set_items(compatible_ports)  # Fill the 'compatible with' listbox
            self.__force_connection_checkbox_var.set(port.force_connection)
            if self.__hierarchy_tree:    # If tree exists
                self.__update_tree()
                self.__hierarchy_tree.grid(row=0, column=1, sticky=tk.NSEW)  # Show tree
        else:
            self.__selected_port = None
            self.__force_connection_checkbox_var.set(False)
            change_controls_state(tk.DISABLED,
                                  *buttons_to_change_state_of)

    def __update_tree(self):
        leaf_cmps = self.__state.model.get_leaf_components()
        self.__hierarchy_tree.update_values(*leaf_cmps)

    # SubscribesToListeners
    def _subscribe_to_events(self) -> None:
        pub.subscribe(self.__on_model_loaded, actions.MODEL_LOADED)
        pub.subscribe(self.__on_hierarchy_edited, actions.HIERARCHY_EDITED)
        pub.subscribe(self._reset, actions.RESET)

    def __on_hierarchy_edited(self):
        self.__build_tree()
        self.__selected_component = None
        self.__cmp_label_var.set('')
        self.__cmp_label.grid_forget()
        self.__amount_spinbox_label.grid_forget()
        self.__amount_spinbox.grid_forget()
        self.__all_children_amount_spinbox_label.grid_forget()
        self.__all_children_amount_spinbox.grid_forget()
        self.__apply_to_all_children_button.grid_forget()

    def __on_model_loaded(self):
        self._reset()
        self.__build_tree()
        ports_names = self.__state.model.get_all_ports_names()
        self.__port_combobox['values'] = sorted(ports_names)

    # Resetable
    def _reset(self) -> None:
        self.__selected_port = None
        self.__selected_component = None
        self.__hierarchy_tree.set_items([])
        self.__port_combobox_var.set(SELECT_PORT)
        self.__port_combobox['values'] = []

    # Class-specific
    # Ports
    def __add_port(self):
        name = simpledialog.askstring('Add port', f'Enter name of the new port.')
        if name:
            try:
                port, _ = self.__state.model.add_port(name)
                self.__selected_port = port
                self.__port_combobox['values'] = sorted((*self.__port_combobox['values'], name))
                self.__port_combobox_var.set(name)
                change_controls_state(tk.NORMAL,
                                      self.__rename_port_button,
                                      self.__remove_port_button,
                                      self.__force_connection_checkbox,
                                      self.__compatible_with_edit_button)
            except BGError as e:
                messagebox.showerror('Add port error.', e.message)

    def __rename_port(self) -> None:
        new_name = simpledialog.askstring('Rename', f'Enter new name for "{self.__selected_port.name}" port.')
        if new_name:
            try:
                old_name = self.__selected_port.name
                self.__state.model.change_port_name(self.__selected_port, new_name)
                updated_combobox_values = [val if val != old_name else new_name for val in
                                           [*self.__port_combobox['values']]]
                self.__port_combobox['values'] = sorted(updated_combobox_values)
                self.__port_combobox_var.set(new_name)
            except BGError as e:
                messagebox.showerror('Rename error.', e.message)

    def __remove_port(self) -> None:
        if self.__selected_port:
            removed_prt = self.__state.model.remove_port(self.__selected_port)
            updated_combobox_values = [val for val in [*self.__port_combobox['values']] if val != removed_prt.name]
            self.__port_combobox['values'] = updated_combobox_values
            self.__selected_port = None
            self.__port_combobox_var.set(SELECT_PORT)
            change_controls_state(tk.DISABLED,
                                  self.__rename_port_button,
                                  self.__remove_port_button,
                                  self.__force_connection_checkbox,
                                  self.__compatible_with_edit_button)

            # Hide component-specific widgets
            # TODO: maybe do it in a similar manner to disabling controls
            # TODO: and same with showing
            self.__cmp_label.grid_forget()
            self.__amount_spinbox_label.grid_forget()
            self.__amount_spinbox.grid_forget()
            self.__all_children_amount_spinbox_label.grid_forget()
            self.__all_children_amount_spinbox.grid_forget()
            self.__apply_to_all_children_button.grid_forget()

            if self.__hierarchy_tree:
                self.__hierarchy_tree.grid_forget()

    def __edit_compatible_with(self):
        if self.__selected_port:
            all_ports = self.__state.model.ports
            compatible_ports = [p for p in all_ports if p.id_ in self.__selected_port.compatible_with]
            ports_rest = [p for p in all_ports if p not in compatible_ports and p.id_ != self.__selected_port.id_]
            SelectPortsWindow(self._frame, self.__selected_port, compatible_ports, ports_rest, callback=self.__compatible_with_edited)

    def __compatible_with_edited(self, ports: List[Port]):
        if self.__selected_port:
            ports.sort(key=lambda x: x.name)
            self.__compatible_with_listbox.set_items(ports)
            self.__state.model.update_ports_compatibility(self.__selected_port, ports)

    def __on_force_connection_toggled(self, _1, _2, _3):
        if self.__selected_port:
            value = self.__force_connection_checkbox_var.get()
            self.__selected_port.force_connection = value

    def __on_amount_changed(self, _1, _2, _3):
        if self.__selected_component and self.__selected_port:
            value = None
            try:
                value = self.__amount_spinbox_var.get()
            except tk.TclError as e:
                print(e)
            finally:
                if value:
                    self.__selected_component.ports[self.__selected_port.id_] = value
                elif self.__selected_port.id_ in self.__selected_component.ports:
                    del self.__selected_component.ports[self.__selected_port.id_]

                self.__hierarchy_tree.update_values(self.__selected_component)

    def __apply_to_all_children(self):
        if self.__selected_component and self.__selected_port:
            value = None
            try:
                value = self.__all_children_amount_spinbox_var.get()
            except tk.TclError as e:
                print(e)
            finally:
                updated_components = self.__state.model.set_ports_amount_to_all_components_children(
                    self.__selected_component, self.__selected_port, value)
                self.__hierarchy_tree.update_values(*updated_components)
