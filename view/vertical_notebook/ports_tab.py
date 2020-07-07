import math
import tkinter as tk
from typing import Optional, Any, Tuple, List
from tkinter import ttk, simpledialog, messagebox

from pubsub import pub

import actions
from exceptions import PortError
from model.port import Port
from model.component import Component
from view.abstract.has_common_setup import HasCommonSetup
from view.abstract.has_controller_access import HasControllerAccess
from view.abstract.has_hierarchy_tree import HasHierarchyTree
from view.abstract.resetable import Resetable
from view.abstract.subscribes_to_listeners import SubscribesToListeners
from view.abstract.tab import Tab
from view.hierarchy_tree import HierarchyTree
from view.scrollbars_listbox import ScrollbarListbox
from view.simple_constraint_window import SimpleConstraintWindow
from view.select_ports_window import SelectPortsWindow
from view.tree_view_column import Column

TAB_NAME = 'Ports'
SELECT_PORT = '(select port)'


class PortsTab(Tab,
               HasControllerAccess,
               HasCommonSetup,
               SubscribesToListeners,
               HasHierarchyTree,
               Resetable):
    def __init__(self, parent, parent_notebook, *args, **kwargs):
        Tab.__init__(self, parent_notebook, TAB_NAME, *args, **kwargs)
        HasControllerAccess.__init__(self, parent)

        HasCommonSetup.__init__(self)
        SubscribesToListeners.__init__(self)
        HasHierarchyTree.__init__(self)     # TODO: merge lisbox with treeview

        self.__ports_listbox: Optional[ScrollbarListbox] = None
        self.__selected_port: Optional[Port] = None
        # self.__build_ports_listbox()

    # HasCommonSetup
    def _create_widgets(self) -> None:
        self.__left_frame = tk.Frame(self.frame)
        self.__left_top_frame = tk.Frame(self.__left_frame)
        self.__left_mid_frame_1 = tk.Frame(self.__left_frame)
        self.__left_mid_frame_2 = tk.Frame(self.__left_frame)
        self.__left_bot_frame = tk.Frame(self.__left_frame)
        # Ports combobox
        self.__port_combobox_var = tk.StringVar(value=SELECT_PORT)
        self.__port_combobox_var.trace('w', self.__on_combobox_changed)
        self.__port_combobox = ttk.Combobox(self.__left_top_frame, state='readonly',
                                            textvariable=self.__port_combobox_var)

        # Port label
        # TODO: remove!!!
        # self.__port_label_var = tk.StringVar(value='PORT')
        # self.__port_label = ttk.Label(self.__right_top_frame, textvariable=self.__port_label_var, style='Big.TLabel')

        # C(r)ud Buttons
        self.__add_port_button = ttk.Button(self.__left_top_frame, text='Add', state=tk.NORMAL, command=self.__add_port)
        self.__rename_port_button = ttk.Button(self.__left_top_frame, text='Rename', state=tk.DISABLED,
                                               command=self.__rename_port)
        self.__remove_port_button = ttk.Button(self.__left_top_frame, text='Remove', state=tk.DISABLED,
                                               command=self.__remove_port)
        # Force connection checkbox
        self.__force_connection_checkbox_var = tk.BooleanVar(value=False)
        self.__force_connection_checkbox_var.trace('w', self.__on_force_connection_toggled)
        self.__force_connection_checkbox_label = ttk.Label(self.__left_top_frame,
                                                           text='Force connection:')
        self.__force_connection_checkbox = ttk.Checkbutton(self.__left_top_frame, state=tk.DISABLED,
                                                           variable=self.__force_connection_checkbox_var)

        self.__cmp_label_var = tk.StringVar(value='COMPONENT')
        self.__cmp_label = ttk.Label(self.__left_frame, textvariable=self.__cmp_label_var, style='Big.TLabel')

        self.__left_mid_frame_1 = tk.Frame(self.__left_frame)
        self.__amount_spinbox_label = ttk.Label(self.__left_mid_frame_1, text='Has:', style='Big.TLabel')
        self.__amount_spinbox_var = tk.IntVar(value='')
        self.__amount_spinbox_var.trace('w', self.__on_amount_changed)
        self.__amount_spinbox = ttk.Spinbox(self.__left_mid_frame_1, from_=-math.inf, to=math.inf,
                                            textvariable=self.__amount_spinbox_var)

        self.__all_children_amount_spinbox_label = ttk.Label(self.__left_mid_frame_2, text='Children have:')
        self.__all_children_amount_spinbox_var = tk.IntVar(value='')
        self.__all_children_amount_spinbox = ttk.Spinbox(self.__left_mid_frame_2, from_=-math.inf, to=math.inf,
                                                         textvariable=self.__all_children_amount_spinbox_var)
        self.__apply_to_all_children_button = ttk.Button(self.__left_mid_frame_2, text='Apply to all children',
                                                         command=self.__apply_to_all_children)

        # self.__occurs_in_edit_button = ttk.Button(self.__right_mid_left_frame, text='Edit', command=self.__edit_occurs_in)
        # Occurs in
        # self.__occurs_in_listbox = ScrollbarListbox(self.__right_mid_left_frame,
        #                                             columns=[Column('#0', 'Port', stretch=tk.YES),
        #                                                      Column('amount', 'Amount')],
        #                                             on_select_callback=self.__on_select_ports_listbox_item,
        #                                             extract_values=self.__extract_values_occurs_in_listbox_item,
        #                                             extract_id=lambda cmp: cmp.id_,
        #                                             extract_text=lambda cmp: cmp.name)
        # self.__selected_component_label = ttk.Label(self.__right_mid_right_frame, text='COMPONENT', style='Big.TLabel')
        # Compatible with
        self.__left_bot_frame = tk.Frame(self.__left_frame)
        self.__compatible_with_label = ttk.Label(self.__left_bot_frame, text='Compatible with:', style='Big.TLabel')
        self.__compatible_with_listbox = ScrollbarListbox(self.__left_bot_frame, grid_row=1, grid_column=0,
                                                          extract_text=lambda prt: prt.name,
                                                          extract_id=lambda prt: prt.id_,
                                                          columns=[Column('#0', 'Port', stretch=tk.YES)])
        self.__compatible_with_edit_button = ttk.Button(self.__left_bot_frame, text='Edit',
                                                        command=self.__edit_compatible_with)

    def _setup_layout(self) -> None:
        self.__left_frame.grid(row=0, column=0, sticky=tk.NSEW)

        # Right top
        self.__left_top_frame.grid(row=0, column=0)
        self.__port_combobox.grid(row=0, column=0, columnspan=3)

        self.__add_port_button.grid(row=1, column=0)
        self.__rename_port_button.grid(row=1, column=1)
        self.__remove_port_button.grid(row=1, column=2)
        self.__force_connection_checkbox_label.grid(row=2, column=0, sticky=tk.E, columnspan=2)
        self.__force_connection_checkbox.grid(row=2, column=2, sticky=tk.W)

        # self.__port_label.grid(row=0, column=0)
        self.__cmp_label.grid(row=1, column=0)
        self.__left_mid_frame_1.grid(row=2, column=0)
        self.__amount_spinbox_label.grid(row=0, column=0)
        self.__amount_spinbox.grid(row=0, column=1, columnspan=2)
        # self.__right_mid_left_frame.grid(row=1, column=0)
        # self.__occurs_in_edit_button.grid(row=2, column=0)

        # self.__right_mid_right_frame.grid(row=1, column=1)
        # self.__selected_component_label.grid(row=0, column=0)

        self.__left_mid_frame_2.grid(row=3, column=0)
        self.__all_children_amount_spinbox_label.grid(row=0, column=0)
        self.__all_children_amount_spinbox.grid(row=0, column=1, columnspan=2)
        self.__apply_to_all_children_button.grid(row=1, column=0, columnspan=3)

        self.__left_bot_frame.grid(row=4, column=0)
        self.__compatible_with_label.grid(row=0, column=0)
        self.__compatible_with_edit_button.grid(row=2, column=0)

        self.frame.columnconfigure(0, weight=1, uniform='fred')
        self.frame.columnconfigure(1, weight=2, uniform='fred')
        self.frame.rowconfigure(0, weight=1)

        # self.__right_frame.rowconfigure(0, weight=1, uniform='fred')
        # self.__right_frame.rowconfigure(1, weight=1, uniform='fred')
        # self.__right_frame.rowconfigure(2, weight=1, uniform='fred')
        # self.__right_frame.rowconfigure(3, weight=1, uniform='fred')
        # self.__right_frame.rowconfigure(4, weight=1, uniform='fred')

        # Hide widgets
        self.__left_frame.grid_forget()
        self.__left_top_frame.grid_forget()
        self.__cmp_label.grid_forget()
        self.__left_mid_frame_1.grid_forget()
        self.__left_mid_frame_2.grid_forget()
        self.__left_bot_frame.grid_forget()

        # TODO: forgets
    # HasHierarchyTree
    def _on_select_tree_item(self, cmp_id: int) -> None:
        if self.__selected_port:
            selected_cmp: Component = self.controller.model.get_component_by_id(cmp_id)
            self._selected_component = selected_cmp

            self.__cmp_label.grid(row=1, column=0)
            self.__cmp_label_var.set(selected_cmp.name)

            if selected_cmp.is_leaf:
                self.__left_mid_frame_2.grid_forget()
                amount = 0
                if self.__selected_port.id_ in selected_cmp.ports:
                    amount = selected_cmp.ports[self.__selected_port.id_]
                self.__amount_spinbox_var.set(amount)
                self.__left_mid_frame_1.grid(row=2, column=0)
            else:
                self.__left_mid_frame_1.grid_forget()
                self.__left_mid_frame_2.grid(row=3, column=0)

    @property
    def _columns(self) -> List[Column]:
        return [Column('amount', 'Amount')]

    def _extract_values(self, cmp: Component) -> Tuple[Any, ...]:
        amount = ''
        if self.__selected_port:
            if self.__selected_port.id_ in cmp.ports:
                amount = cmp.ports[self.__selected_port.id_]
        return amount,

    def _build_tree(self) -> None:
        if self._hierarchy_tree:
            self._destroy_tree()

        self._hierarchy_tree = HierarchyTree(self.frame, self.controller.model.hierarchy, columns=self._columns,
                                             on_select_callback=self._on_select_tree_item,
                                             extract_values=self._extract_values, grid_column=1)

        ports_names = self.controller.model.get_all_ports_names()
        self.__port_combobox['values'] = sorted(ports_names)
        # TODO:
        self.__left_frame.grid(row=0, column=0)  # Show left frame
        self.__left_top_frame.grid(row=0, column=0)  # Show the combobox

    def _destroy_tree(self) -> None:
        pass

    def __on_combobox_changed(self, _1, _2, _3):    # TODO: consider creating widget with ID?
        if self._hierarchy_tree:
            prt_name = self.__port_combobox_var.get()
            port = self.controller.model.get_port_by_name(prt_name)
            self.__enable_rename_remove_buttons()
            if port:
                self.__selected_port = port
                self.__left_bot_frame.grid(row=4, column=0)
                compatible_ports = self.controller.model.get_ports_by_ids(port.compatible_with)
                self.__compatible_with_listbox.set_items(compatible_ports)
                self.__force_connection_checkbox_var.set(port.force_connection)
            else:
                self.__selected_port = None
                self.__left_bot_frame.grid_forget()
                self.__force_connection_checkbox_var.set(False)
            self.__update_tree()

    def __update_tree(self):
        leaf_cmps = self.controller.model.get_leaf_components()
        self._hierarchy_tree.update_values(leaf_cmps)

    def __on_select_ports_listbox_item(self, id_: int) -> None:
        prt = self.controller.model.get_port_by_id(id_)
        self.__selected_port = prt
        # self.__port_label_var.set(prt.name)
        self.__force_connection_checkbox_var.set(prt.force_connection)
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
        pub.subscribe(self._build_tree, actions.HIERARCHY_CREATED)
        pub.subscribe(self._build_tree, actions.HIERARCHY_EDITED)
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
                # TODO: remove the index
                port, _ = self.controller.model.add_port(name)
                self.__selected_port = port
                self.__port_combobox['values'] = sorted((*self.__port_combobox['values'], name))
                self.__port_combobox_var.set(name)
                self.__enable_rename_remove_buttons()
            except PortError as e:
                messagebox.showerror('Add port error.', e.message)

    def __rename_port(self) -> None:
        new_name = simpledialog.askstring('Rename', f'Enter new name for "{self.__selected_port.name}" port.')
        if new_name:
            try:
                old_name = self.__selected_port.name
                self.controller.model.change_port_name(self.__selected_port, new_name)
                updated_combobox_values = [val if val != old_name else new_name for val in
                                           [*self.__port_combobox['values']]]
                self.__port_combobox['values'] = sorted(updated_combobox_values)
                self.__port_combobox_var.set(new_name)
            except PortError as e:
                messagebox.showerror('Rename error.', e.message)

    def __remove_port(self) -> None:
        if self.__selected_port:
            removed_prt = self.controller.model.remove_port(self.__selected_port)
            updated_combobox_values = [val for val in [*self.__port_combobox['values']] if val != removed_prt.name]
            self.__port_combobox['values'] = updated_combobox_values
            self.__selected_port = None
            self.__update_tree()
            self.__port_combobox_var.set(SELECT_PORT)
            self.__disable_rename_remove_buttons()

            self.__cmp_label.grid_forget()
            self.__left_mid_frame_1.grid_forget()
            self.__left_mid_frame_2.grid_forget()
            self.__left_bot_frame.grid_forget()

    def __enable_rename_remove_buttons(self):
        self.__rename_port_button.config(state=tk.NORMAL)
        self.__remove_port_button.config(state=tk.NORMAL)
        self.__force_connection_checkbox.config(state=tk.NORMAL)

    def __disable_rename_remove_buttons(self):
        self.__rename_port_button.config(state=tk.DISABLED)
        self.__remove_port_button.config(state=tk.DISABLED)
        self.__force_connection_checkbox.config(state=tk.DISABLED)

    # Occurs in
    def __on_select_component_listbox_item(self, id_: int) -> None:
        # TODO: ?
        pass

    def __extract_values_occurs_in_listbox_item(self, cmp: Component) -> Any:
        amount = ''
        if self.__selected_port.id_ in cmp.ports:
            amount = cmp.ports[self.__selected_port.id_]
        return amount

    def __edit_compatible_with(self):
        if self.__selected_port:
            all_ports = self.controller.model.ports
            compatible_ports = [p for p in all_ports if p.id_ in self.__selected_port.compatible_with]
            ports_rest = [p for p in all_ports if p not in compatible_ports and p.id_ != self.__selected_port.id_]
            SelectPortsWindow(self, self.frame, compatible_ports, ports_rest, callback=self.__compatible_with_edited)

    def __compatible_with_edited(self, ports: List[Port]):
        if self.__selected_port:
            ports.sort(key=lambda x: x.name)
            self.__compatible_with_listbox.set_items(ports)
            self.controller.model.update_ports_compatibility(self.__selected_port, ports)

    def __on_force_connection_toggled(self, _1, _2, _3):
        if self.__selected_port:
            value = self.__force_connection_checkbox_var.get()
            self.__selected_port.force_connection = value

    def __on_amount_changed(self, _1, _2, _3):
        if self._selected_component and self.__selected_port:
            value = None
            try:
                value = self.__amount_spinbox_var.get()
            except tk.TclError as e:
                print(e)
            finally:
                if value:
                    self._selected_component.ports[self.__selected_port.id_] = value
                elif self.__selected_port.id_ in self._selected_component.ports:
                    del self._selected_component.ports[self.__selected_port.id_]

                self._hierarchy_tree.update_values([self._selected_component])

    def __apply_to_all_children(self):
        if self._selected_component and self.__selected_port:
            value = None
            try:
                value = self.__all_children_amount_spinbox_var.get()
            except tk.TclError as e:
                print(e)
            finally:
                updated_components = self.controller.model.set_ports_amount_to_all_components_children(
                    self._selected_component, self.__selected_port, value)
                self._hierarchy_tree.update_values(updated_components)