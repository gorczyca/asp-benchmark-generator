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
from view.select_ports_window import SelectPortsWindow
from view.tree_view_column import Column
from view.style import FONT
from view.common import trim_string, change_controls_state

TAB_NAME = 'Ports'
SELECT_PORT = '(select port)'

CONTROL_PAD_Y = 3

FRAME_PAD_Y = 10
FRAME_PAD_X = 10


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

    # HasCommonSetup
    def _create_widgets(self) -> None:
        self.__left_frame = tk.Frame(self.frame)
        # self.__left_top_frame = tk.Frame(self.__left_frame)
        # self.__left_bottom_frame = tk.Frame(self.__left_frame)

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

        self.__cmp_label_var = tk.StringVar(value='COMPONENT')
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
        self.__left_frame.grid(row=0, column=0, sticky=tk.NSEW, pady=FRAME_PAD_Y, padx=FRAME_PAD_X)
        # Left top
        # self.__left_top_frame.grid(row=0, column=0, sticky=tk.NSEW, )

        self.__port_combobox.grid(row=0, column=0, columnspan=2, sticky=tk.NSEW, pady=CONTROL_PAD_Y)
        self.__add_port_button.grid(row=1, column=0, columnspan=2, sticky=tk.NSEW, pady=CONTROL_PAD_Y)
        self.__rename_port_button.grid(row=2, column=0, columnspan=2, sticky=tk.NSEW, pady=CONTROL_PAD_Y)
        self.__remove_port_button.grid(row=3, column=0, columnspan=2, sticky=tk.NSEW, pady=CONTROL_PAD_Y)
        self.__force_connection_checkbox_label.grid(row=4, column=0, sticky=tk.W, pady=CONTROL_PAD_Y)
        self.__force_connection_checkbox.grid(row=4, column=1, sticky=tk.E, pady=CONTROL_PAD_Y)
        self.__compatible_with_edit_button.grid(row=5, column=0, columnspan=2, sticky=tk.NSEW, pady=CONTROL_PAD_Y)
        self.__compatible_with_listbox.grid(row=6, column=0, columnspan=2, sticky=tk.NSEW, pady=CONTROL_PAD_Y)
        # Left bottom
        # self.__left_bottom_frame.grid(row=1, column=0,  sticky=tk.NSEW, pady=FRAME_PAD_Y, padx=FRAME_PAD_X)
        self.__cmp_label.grid(row=7, column=0, columnspan=2, pady=CONTROL_PAD_Y, sticky=tk.EW)
        self.__amount_spinbox_label.grid(row=8, column=0, pady=CONTROL_PAD_Y, sticky=tk.W)
        self.__amount_spinbox.grid(row=8, column=1, pady=CONTROL_PAD_Y, sticky=tk.NSEW)

        self.__all_children_amount_spinbox_label.grid(row=8, column=0, pady=CONTROL_PAD_Y, sticky=tk.W)
        self.__all_children_amount_spinbox.grid(row=8, column=1, pady=CONTROL_PAD_Y, sticky=tk.NSEW)
        self.__apply_to_all_children_button.grid(row=9, column=0, columnspan=2, sticky=tk.NSEW, pady=CONTROL_PAD_Y)

        self.frame.columnconfigure(1, weight=1)     # Give all the remaining space to hierarchy tree
        self.frame.rowconfigure(0, weight=1)

        # self.__left_frame.rowconfigure(0, weight=2, uniform='fred')
        # self.__left_frame.rowconfigure(1, weight=1, uniform='fred')
        self.__left_frame.columnconfigure(1, weight=1)

        # Hide widgets
        # self.__left_frame.grid_forget()
        # self.__left_top_frame.grid_forget()
        # self.__left_bottom_frame.grid_forget()
        # Hide specific widgets, not entire frames
        self.__cmp_label.grid_forget()
        self.__amount_spinbox_label.grid_forget()
        self.__amount_spinbox.grid_forget()
        self.__all_children_amount_spinbox_label.grid_forget()
        self.__all_children_amount_spinbox.grid_forget()
        self.__apply_to_all_children_button.grid_forget()

    # HasHierarchyTree
    def _on_select_tree_item(self, cmp_id: int) -> None:
        if self.__selected_port:    # TODO: should be unnecessary
            selected_cmp = self.controller.model.get_component_by_id(cmp_id)
            self._selected_component = selected_cmp

            self.__cmp_label.grid(row=7, column=0, columnspan=2, pady=CONTROL_PAD_Y, sticky=tk.EW)  # Show cmp label
            self.__cmp_label_var.set(trim_string(selected_cmp.name))    # Fill the label with component name

            if selected_cmp.is_leaf:
                self.__all_children_amount_spinbox_label.grid_forget()  # Hide widgets (changing all children)
                self.__all_children_amount_spinbox.grid_forget()
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
                                             extract_values=self._extract_values)
        self._hierarchy_tree.grid(row=0, column=1, sticky=tk.NSEW)  # Place tree in the layout
        if not self.__selected_port:    # If no port is selected
            self._hierarchy_tree.grid_forget()  # Hide the tree

    # TODO:
    def __on_model_loaded(self):
        ports_names = self.controller.model.get_all_ports_names()
        self.__port_combobox['values'] = sorted(ports_names)

    def _destroy_tree(self) -> None:
        pass

    def __on_combobox_changed(self, _1, _2, _3):
        # Hide component-specific widgets
        self.__cmp_label.grid_forget()
        self.__amount_spinbox_label.grid_forget()
        self.__amount_spinbox.grid_forget()
        self.__all_children_amount_spinbox_label.grid_forget()
        self.__all_children_amount_spinbox.grid_forget()
        self.__apply_to_all_children_button.grid_forget()

        prt_name = self.__port_combobox_var.get()
        port = self.controller.model.get_port_by_name(prt_name)
        buttons_to_change_state_of = [
            self.__rename_port_button,
            self.__remove_port_button,
            self.__force_connection_checkbox,
            self.__compatible_with_edit_button,
        ]
        if port:
            self.__selected_port = port
            change_controls_state(buttons_to_change_state_of, state=tk.NORMAL)
            compatible_ports = self.controller.model.get_ports_by_ids(port.compatible_with)
            self.__compatible_with_listbox.set_items(compatible_ports)  # Fill the 'compatible with' listbox
            self.__force_connection_checkbox_var.set(port.force_connection)
            if self._hierarchy_tree:    # If tree exists
                self.__update_tree()
                self._hierarchy_tree.grid(row=0, column=1, sticky=tk.NSEW)  # Show tree
        else:
            self.__selected_port = None
            self.__force_connection_checkbox_var.set(False)
            change_controls_state(buttons_to_change_state_of, state=tk.DISABLED)

    def __update_tree(self):
        leaf_cmps = self.controller.model.get_leaf_components()
        self._hierarchy_tree.update_values(leaf_cmps)

    # TODO: remove
    # def __on_select_ports_listbox_item(self, id_: int) -> None:
    #     prt = self.controller.model.get_port_by_id(id_)
    #     self.__selected_port = prt
    #     # self.__port_label_var.set(prt.name)
    #     self.__force_connection_checkbox_var.set(prt.force_connection)
    #     self.__enable_buttons()

    # def __build_ports_listbox(self) -> None:
    #     if self.__ports_listbox:
    #         pass    # TODO: destroy listbox
    #
    #     self.__ports_listbox = ScrollbarListbox(self.frame, self.controller.model.ports,
    #                                             columns=[Column('#0', 'Compatible with', stretch=tk.YES)],
    #                                             on_select_callback=self.__on_select_ports_listbox_item,
    #                                             extract_values=lambda prt: (),
    #                                             extract_id=lambda prt: prt.id_,
    #                                             extract_text=lambda prt: prt.name)
    # def __extract_values_occurs_in_listbox_item(self, cmp: Component) -> Any:
    #     amount = ''
    #     if self.__selected_port.id_ in cmp.ports:
    #         amount = cmp.ports[self.__selected_port.id_]
    #     return amount

    # SubscribesToListeners
    def _subscribe_to_listeners(self) -> None:
        pub.subscribe(self._build_tree, actions.HIERARCHY_CREATED)
        pub.subscribe(self._build_tree, actions.HIERARCHY_EDITED)   # TODO: are both necessary?
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
                port, _ = self.controller.model.add_port(name)
                self.__selected_port = port
                self.__port_combobox['values'] = sorted((*self.__port_combobox['values'], name))
                self.__port_combobox_var.set(name)
                buttons_to_enable = [
                    self.__rename_port_button,
                    self.__remove_port_button,
                    self.__force_connection_checkbox,
                    self.__compatible_with_edit_button,
                ]
                change_controls_state(buttons_to_enable, state=tk.NORMAL)
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
            self.__port_combobox_var.set(SELECT_PORT)
            controls_to_disable = [
                self.__rename_port_button,
                self.__remove_port_button,
                self.__force_connection_checkbox,
                self.__compatible_with_edit_button,
            ]
            change_controls_state(controls_to_disable, state=tk.DISABLED)

            # Hide component-specific widgets
            # TODO: maybe do it in a similar manner to disabling controls
            # TODO: and same with showing
            self.__cmp_label.grid_forget()
            self.__amount_spinbox_label.grid_forget()
            self.__amount_spinbox.grid_forget()
            self.__all_children_amount_spinbox_label.grid_forget()
            self.__all_children_amount_spinbox.grid_forget()
            self.__apply_to_all_children_button.grid_forget()

            if self._hierarchy_tree:
                self._hierarchy_tree.grid_forget()

    def __edit_compatible_with(self):
        if self.__selected_port:
            all_ports = self.controller.model.ports
            compatible_ports = [p for p in all_ports if p.id_ in self.__selected_port.compatible_with]
            ports_rest = [p for p in all_ports if p not in compatible_ports and p.id_ != self.__selected_port.id_]
            SelectPortsWindow(self, self.frame, self.__selected_port,  compatible_ports, ports_rest, callback=self.__compatible_with_edited)

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
