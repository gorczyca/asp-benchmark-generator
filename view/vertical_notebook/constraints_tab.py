import tkinter as tk
from tkinter import ttk
from typing import Optional, Any

from pubsub import pub

import actions
from model import SimpleConstraint
from state import State
from view.scrollbars_listbox import ScrollbarListbox
from view.tree_view_column import Column
from view.abstract import HasCommonSetup, Resetable, SubscribesToEvents, Tab
from view.vertical_notebook.complex_constraint_window import ComplexConstraintWindow
from view.vertical_notebook.simple_constraint_window import SimpleConstraintWindow
from view.common import trim_string, change_controls_state

TAB_NAME = 'Constraints'
LABEL_LENGTH = 20

CONTROL_PAD_Y = 3

FRAME_PAD_Y = 10
FRAME_PAD_X = 10


class ConstraintsTab(Tab,
                     HasCommonSetup,
                     SubscribesToEvents,
                     Resetable):
    """Used to create, edit and remove constraints.

    Attributes:
        __selected_constraint: Currently selected constraint in the constraints list view.
    """
    def __init__(self, parent_notebook):

        self.__state = State()
        self.__selected_constraint: Optional[Any] = None    # can be either simple or complex constraint

        Tab.__init__(self, parent_notebook, TAB_NAME)
        HasCommonSetup.__init__(self)
        SubscribesToEvents.__init__(self)

    # HasCommonSetup
    def _create_widgets(self) -> None:
        self.__constraints_listbox = ScrollbarListbox(self, columns=[Column('Type')], heading='Constraint',
                                                      extract_id=lambda crt: crt.id_, extract_text=lambda crt: crt.name,
                                                      extract_values=lambda crt: 'Simple' if isinstance(crt, SimpleConstraint) else 'Complex',
                                                      on_select_callback=self.__on_select_callback,
                                                      values=self.__state.model.get_all_constraints())
        self.__right_frame = ttk.Frame(self)
        # Ctr label
        self.__ctr_label_var = tk.StringVar(value='')
        self.__ctr_label = ttk.Label(self.__right_frame, textvariable=self.__ctr_label_var, style='Big.TLabel', anchor=tk.CENTER)

        self.__add_simple_constraint_button = ttk.Button(self.__right_frame, text='Add simple constraint',
                                                         command=self.__on_add)
        self.__add_complex_constraint_button = ttk.Button(self.__right_frame, text='Add complex constraint',
                                                          command=lambda: self.__on_add(complex_=True))
        self.__edit_constraint_button = ttk.Button(self.__right_frame, text='Edit', state=tk.DISABLED,
                                                   command=self.__on_edit)
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

        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

    # SubscribesToEvents
    def _subscribe_to_events(self) -> None:
        pub.subscribe(self.__on_model_changed, actions.MODEL_LOADED)
        pub.subscribe(self.__on_model_changed, actions.TAXONOMY_EDITED)
        pub.subscribe(self._reset, actions.RESET)

    # Resetable
    def _reset(self) -> None:
        self.__constraints_listbox.set_items([])
        self.__selected_constraint = None
        self.__ctr_label_var.set('')
        change_controls_state(tk.DISABLED,
                              self.__edit_constraint_button,
                              self.__remove_constraint_button)

    def __on_select_callback(self, ctr_id: int):
        """Executed whenever a constraints listview item is selected (by mouse click).

        :param ctr_id: Id of the selected constraint.
        """
        selected_ctr = self.__state.model.get_constraint(id_=ctr_id)
        if selected_ctr:
            self.__selected_constraint = selected_ctr
            self.__ctr_label_var.set(trim_string(selected_ctr.name, length=LABEL_LENGTH))
            # Enable buttons
            change_controls_state(tk.NORMAL,
                                  self.__edit_constraint_button,
                                  self.__remove_constraint_button)

    def __add(self, ctr: Any) -> None:
        """Executed after adding a new constraint in SimpleConstraintWindow or ComplexConstraintWindow.

        :param ctr: New SimpleConstraint or ComplexConstraint obtained from SimpleConstraintWindow
            or ComplexConstraintWindow.
        """
        _, index = self.__state.model.add_constraint(ctr)
        self.__constraints_listbox.add_item(ctr, index=index)
        # Set selected constraint to the newly created constraint
        self.__selected_constraint = ctr
        self.__ctr_label_var.set(trim_string(ctr.name, length=LABEL_LENGTH))
        # Enable buttons
        change_controls_state(tk.NORMAL,
                              self.__edit_constraint_button,
                              self.__remove_constraint_button)

    def __edit(self, ctr: Any):
        """Executed after editing the constraint in SimpleConstraintWindow or ComplexConstraintWindow.

        :param ctr: Edited SimpleConstraint or ComplexConstraint obtained from SimpleConstraintWindow
            or ComplexConstraintWindow.
        """
        _, index = self.__state.model.edit_constraint(ctr)
        self.__selected_constraint = ctr
        # Just in case if the name has changed
        self.__constraints_listbox.rename_item(ctr, index=index)    # Update constraint name in treeview
        self.__ctr_label_var.set(trim_string(ctr.name, length=LABEL_LENGTH))  # Update constraint label

    def __on_add(self, complex_=False):
        """Executed whenever the __add_simple_constraint_button or __add_complex_constraint_button are pressed.

        :param complex_: If __add_complex_constraint_button is pressed then set to True; False otherwise.
        """
        if complex_:
            ComplexConstraintWindow(self, callback=self.__add)
        else:
            SimpleConstraintWindow(self, callback=self.__add)

    def __on_edit(self):
        """Executed whenever the __edit_constraint_button is pressed."""
        if self.__selected_constraint:
            if isinstance(self.__selected_constraint, SimpleConstraint):
                SimpleConstraintWindow(self, constraint=self.__selected_constraint, callback=self.__edit)
            else:
                ComplexConstraintWindow(self, constraint=self.__selected_constraint, callback=self.__edit)

    def __remove_constraint(self):
        """Executed whenever the __remove_constraint_button is pressed.
        Removes selected constraint from model.
        """
        if self.__selected_constraint:
            self.__state.model.remove_constraint(self.__selected_constraint)
            self.__constraints_listbox.remove_item_recursively(self.__selected_constraint)
            self.__selected_constraint = None
            # Hide widgets
            self.__ctr_label_var.set('')
            change_controls_state(tk.DISABLED,
                                  self.__edit_constraint_button,
                                  self.__remove_constraint_button)

    def __on_model_changed(self):
        """Executed whenever a model is loaded from file or taxonomy changes."""
        ctrs = self.__state.model.get_all_constraints()
        self.__constraints_listbox.set_items(ctrs)
        self.__selected_constraint = None
        self.__ctr_label_var.set('')
        change_controls_state(tk.DISABLED,
                              self.__edit_constraint_button,
                              self.__remove_constraint_button)
