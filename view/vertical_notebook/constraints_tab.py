import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional, Any

from pubsub import pub

from exceptions import ConstraintError
from model.simple_constraint import SimpleConstraint
from view.abstract.has_common_setup import HasCommonSetup
from view.abstract.has_controller_access import HasControllerAccess
from view.abstract.resetable import Resetable
from view.abstract.subscribes_to_listeners import SubscribesToListeners
from view.abstract.tab import Tab
from view.complex_constraint_window import ComplexConstraintWindow
from view.scrollbars_listbox import ScrollbarListbox
from view.simple_constraint_window import SimpleConstraintWindow
from view.tree_view_column import Column
from view.common import trim_string, change_controls_state
import actions

TAB_NAME = 'Constraints'
LABEL_LENGTH = 15

CONTROL_PAD_Y = 3

FRAME_PAD_Y = 10
FRAME_PAD_X = 10


class ConstraintsTab(Tab,
                     HasControllerAccess,
                     HasCommonSetup,
                     SubscribesToListeners,
                     Resetable):
    def __init__(self, parent, parent_notebook, *args, **kwargs):
        Tab.__init__(self, parent_notebook, TAB_NAME, *args, **kwargs)
        HasControllerAccess.__init__(self, parent)

        self.__constraints_listbox: Optional[ScrollbarListbox] = None
        self.__selected_constraint: Optional[Any] = None    # can be either simple or complex constraint

        HasCommonSetup.__init__(self)
        SubscribesToListeners.__init__(self)

    # HasCommonSetup
    def _create_widgets(self) -> None:
        self.__constraints_listbox = ScrollbarListbox(self.frame, columns=[Column('type', 'Type')], heading='Constraint',
                                                      extract_id=lambda crt: crt.id_, extract_text=lambda crt: crt.name,
                                                      extract_values=lambda crt: 'Simple' if isinstance(crt, SimpleConstraint) else 'Complex',
                                                      on_select_callback=self.__on_select_callback)
        self.__right_frame = ttk.Frame(self.frame)
        # Ctr label
        self.__ctr_label_var = tk.StringVar(value='')
        self.__ctr_label = ttk.Label(self.__right_frame, textvariable=self.__ctr_label_var, style='Big.TLabel', anchor=tk.CENTER)

        self.__add_simple_constraint_button = ttk.Button(self.__right_frame, text='Add simple constraint',
                                                         command=self.__add_constraint)
        self.__add_complex_constraint_button = ttk.Button(self.__right_frame, text='Add complex constraint',
                                                          command=lambda: self.__add_constraint(complex_=True))
        self.__edit_constraint_button = ttk.Button(self.__right_frame, text='Edit', state=tk.DISABLED,
                                                   command=self.__edit_constraint)
        self.__remove_constraint_button = ttk.Button(self.__right_frame, text='Remove', state=tk.DISABLED,
                                                     command=self.__remove_constraint)

    def _setup_layout(self) -> None:
        self.__constraints_listbox.grid(row=0, column=0, sticky=tk.NSEW)
        self.__right_frame.grid(row=0, column=1, sticky=tk.NSEW, pady=FRAME_PAD_Y, padx=FRAME_PAD_X)

        self.__ctr_label.grid(row=0, column=0, pady=CONTROL_PAD_Y, sticky=tk.EW)
        self.__add_simple_constraint_button.grid(row=1, column=0, sticky=tk.NSEW, pady=CONTROL_PAD_Y)
        self.__add_complex_constraint_button.grid(row=2, column=0, sticky=tk.NSEW, pady=CONTROL_PAD_Y)
        self.__edit_constraint_button.grid(row=3, column=0, sticky=tk.NSEW, pady=CONTROL_PAD_Y)
        self.__remove_constraint_button.grid(row=4, column=0, sticky=tk.NSEW, pady=CONTROL_PAD_Y)

        self.frame.columnconfigure(0, weight=1)
        self.frame.rowconfigure(0, weight=1)

    def _subscribe_to_listeners(self) -> None:
        pub.subscribe(self.__on_model_loaded, actions.MODEL_LOADED)

    def _reset(self) -> None:
        pass

    def __on_select_callback(self, ctr_id: int):
        selected_ctr: Any = self.controller.model.get_constraint_by_id(ctr_id)
        if selected_ctr:    # TODO: should be unnecesary
            self.__selected_constraint = selected_ctr
            self.__ctr_label_var.set(trim_string(selected_ctr.name, length=LABEL_LENGTH))
            # Enable buttons
            change_controls_state([
                self.__edit_constraint_button,
                self.__remove_constraint_button
            ], state=tk.NORMAL)

    def __on_constraint_created(self, ctr: Any):
        # TODO: make it sorted alphabetically
        try:
            _, index = self.controller.model.add_constraint(ctr)
            self.__constraints_listbox.add_item(ctr, index=index)
            # Set selected constraint to the newly created constraint
            self.__selected_constraint = ctr
            self.__ctr_label_var.set(trim_string(ctr.name, length=LABEL_LENGTH))
            # Enable buttons
            change_controls_state([
                self.__edit_constraint_button,
                self.__remove_constraint_button
            ], state=tk.NORMAL)

        except ConstraintError as e:
            messagebox.showerror('Add constraint error.', e.message)

    def __on_constraint_edited(self, ctr: Any):
        index = self.controller.model.get_constraint_index(ctr)     # TODO: check, does it work?
        self.__constraints_listbox.rename_item(ctr, index=index)    # If name has changed
        # Update constraint label
        self.__ctr_label_var.set(trim_string(ctr.name, length=LABEL_LENGTH))

    def __add_constraint(self, complex_=False):
        ctr_names = [c.name for c in self.controller.model.get_all_constraints()]
        if complex_:
            ComplexConstraintWindow(self, self.frame, callback=self.__on_constraint_created, check_name_with=ctr_names)
        else:
            SimpleConstraintWindow(self, self.frame, callback=self.__on_constraint_created, check_name_with=ctr_names)

    def __edit_constraint(self):
        if self.__selected_constraint:
            ctr_names = [c.name for c in self.controller.model.get_all_constraints()]
            if isinstance(self.__selected_constraint, SimpleConstraint):
                SimpleConstraintWindow(self, self.frame, constraint=self.__selected_constraint,
                                       callback=self.__on_constraint_edited, check_name_with=ctr_names)
            else:
                ComplexConstraintWindow(self, self.frame, constraint=self.__selected_constraint,
                                        callback=self.__on_constraint_edited, check_name_with=ctr_names)

    def __remove_constraint(self):
        if self.__selected_constraint:
            self.controller.model.remove_constraint(self.__selected_constraint)
            self.__constraints_listbox.remove_item(self.__selected_constraint)
            self.__selected_constraint = None
            # Hide widgets
            self.__ctr_label_var.set('')
            change_controls_state([
                self.__edit_constraint_button,
                self.__remove_constraint_button
            ], state=tk.DISABLED)

    def __on_model_loaded(self):
        ctrs = self.controller.model.get_all_constraints()
        self.__constraints_listbox.set_items(ctrs)
