import copy
from typing import List, Optional, Tuple
import tkinter as tk
from tkinter import ttk, messagebox

from exceptions import BGError
from model import ComplexConstraint, SimpleConstraint
from state import State
from view.scrollbars_listbox import ScrollbarListbox
from view.abstract import HasCommonSetup, Window
from view.vertical_notebook.simple_constraint_window import SimpleConstraintWindow
from view.common import change_controls_state
from model.helpers import normalize_name
from view.style import FRAME_PAD_Y, FRAME_PAD_X, CONTROL_PAD_Y

WINDOW_TITLE = 'Complex constraint'


WINDOW_WIDTH_RATIO = 0.8
WINDOW_HEIGHT_RATIO = 0.8


class ComplexConstraintWindow(HasCommonSetup,
                              Window):
    """Used to create/edit complex constraint.

    Attributes:
        __callback: Function to be executed when the 'OK' button is pressed, before destroying the window.
        __constraint: New constraint / deep copy of the edited constraint.
        __antecedent: List of SimpleConstraints forming an antecedent.
        __consequent: List of SimpleConstraints forming a consequent.
        __selected_antecedent: Currently selected simple constraint in the antecedent list view.
        __selected_consequent: Currently selected simple constraint in the consequent list view.
    """
    def __init__(self, parent_frame, callback, constraint: Optional[ComplexConstraint] = None):
        self.__state = State()
        self.__callback = callback

        self.__constraint: ComplexConstraint = copy.deepcopy(constraint) if constraint is not None \
            else ComplexConstraint()

        self.__antecedent: List[SimpleConstraint] = [] if constraint is None else [copy.deepcopy(sc)
                                                                                   for sc in constraint.antecedent]
        self.__consequent: List[SimpleConstraint] = [] if constraint is None else [copy.deepcopy(sc)
                                                                                   for sc in constraint.consequent]
        self.__selected_antecedent: Optional[SimpleConstraint] = None
        self.__selected_consequent: Optional[SimpleConstraint] = None

        Window.__init__(self, parent_frame, WINDOW_TITLE)
        HasCommonSetup.__init__(self)

    # HasCommonSetup
    def _create_widgets(self) -> None:
        # Name
        self.__data_frame = ttk.Frame(self)
        self.__name_entry_var = tk.StringVar(value=self.__constraint.name)
        self.__name_entry_label = ttk.Label(self.__data_frame, text='Name:')
        self.__name_entry = ttk.Entry(self.__data_frame, textvariable=self.__name_entry_var)
        # Description
        self.__description_text_label = ttk.Label(self.__data_frame, text='Description:')
        self.__description_text = tk.Text(self.__data_frame, height=8, width=40)
        if self.__constraint.description:
            self.__description_text.insert(tk.INSERT, self.__constraint.description)

        self.__implication_frame = ttk.Frame(self)

        self.__antecedent_frame = ttk.Frame(self.__implication_frame)
        self.__consequent_frame = ttk.Frame(self.__implication_frame)

        self.__antecedent_listbox = ScrollbarListbox(self.__antecedent_frame, values=self.__antecedent,
                                                     heading='Condition',
                                                     extract_id=lambda ctr: ctr.id_,
                                                     extract_text=lambda ctr: ctr.name,
                                                     on_select_callback=self.__on_select_antecedent)
        self.__consequent_listbox = ScrollbarListbox(self.__consequent_frame, values=self.__consequent,
                                                     heading='Consequence',
                                                     extract_id=lambda ctr: ctr.id_,
                                                     extract_text=lambda ctr: ctr.name,
                                                     on_select_callback=self.__on_select_consequent)

        # Antecedent all/any
        self.__antecedent_all_var = tk.BooleanVar(value=self.__constraint.antecedent_all)
        self.__antecedent_all_radiobutton = ttk.Radiobutton(self.__antecedent_frame, text='All', value=True,
                                                            variable=self.__antecedent_all_var)
        self.__antecedent_any_radiobutton = ttk.Radiobutton(self.__antecedent_frame, text='Any',
                                                            value=False, variable=self.__antecedent_all_var)

        # Consequent all/any
        self.__consequent_all_var = tk.BooleanVar(value=self.__constraint.consequent_all)
        self.__consequent_all_radiobutton = ttk.Radiobutton(self.__consequent_frame, text='All', value=True,
                                                            variable=self.__consequent_all_var)
        self.__consequent_any_radiobutton = ttk.Radiobutton(self.__consequent_frame, text='Any',
                                                            value=False, variable=self.__consequent_all_var)

        self.__add_antecedent_button = ttk.Button(self.__antecedent_frame, text='Add', command=self.__on_add_antecedent)
        self.__edit_antecedent_button = ttk.Button(self.__antecedent_frame, text='Edit', command=self.__on_edit_antecedent,
                                                   state=tk.DISABLED)
        self.__remove_antecedent_button = ttk.Button(self.__antecedent_frame, text='Remove', state=tk.DISABLED,
                                                     command=self.__remove_antecedent)

        self.__add_consequent_button = ttk.Button(self.__consequent_frame, text='Add', command=self.__on_add_consequent)
        self.__edit_consequent_button = ttk.Button(self.__consequent_frame, text='Edit', command=self.__on_edit_consequent,
                                                   state=tk.DISABLED)
        self.__remove_consequent_button = ttk.Button(self.__consequent_frame, text='Remove', state=tk.DISABLED,
                                                     command=self.__remove_consequent)

        # Buttons frame
        self.__buttons_frame = ttk.Frame(self)
        self.__ok_button = ttk.Button(self.__buttons_frame, text='Ok', command=self.__ok)
        self.__cancel_button = ttk.Button(self.__buttons_frame, text='Cancel', command=self.destroy)

    def _setup_layout(self) -> None:
        self.__data_frame.grid(row=0, column=0, sticky=tk.NSEW, padx=FRAME_PAD_X, pady=FRAME_PAD_Y)
        self.__name_entry_label.grid(row=0, column=0, sticky=tk.W, pady=CONTROL_PAD_Y)
        self.__name_entry.grid(row=0, column=1, sticky=tk.EW, pady=CONTROL_PAD_Y)
        self.__description_text_label.grid(row=1, column=0, sticky=tk.W, pady=CONTROL_PAD_Y)
        self.__description_text.grid(row=1, column=1, sticky=tk.EW, pady=CONTROL_PAD_Y)

        self.__implication_frame.grid(row=1, column=0, sticky=tk.NSEW)
        self.__antecedent_frame.grid(row=0, column=0, sticky=tk.NSEW, padx=FRAME_PAD_X, pady=FRAME_PAD_Y)
        self.__consequent_frame.grid(row=0, column=1, sticky=tk.NSEW, padx=FRAME_PAD_X, pady=FRAME_PAD_Y)

        self.__antecedent_listbox.grid(row=0, column=0, columnspan=4, sticky=tk.NSEW)
        self.__antecedent_all_radiobutton.grid(row=1, column=1, sticky=tk.W, pady=CONTROL_PAD_Y)
        self.__antecedent_any_radiobutton.grid(row=1, column=2, sticky=tk.W, pady=CONTROL_PAD_Y)
        self.__add_antecedent_button.grid(row=2, column=1, columnspan=2, pady=CONTROL_PAD_Y, sticky=tk.NSEW)
        self.__edit_antecedent_button.grid(row=3, column=1, columnspan=2, pady=CONTROL_PAD_Y, sticky=tk.NSEW)
        self.__remove_antecedent_button.grid(row=4, column=1, columnspan=2, pady=CONTROL_PAD_Y, sticky=tk.NSEW)

        self.__consequent_listbox.grid(row=0, column=0, columnspan=4, sticky=tk.NSEW)
        self.__consequent_all_radiobutton.grid(row=1, column=1, sticky=tk.W, pady=CONTROL_PAD_Y)
        self.__consequent_any_radiobutton.grid(row=1, column=2, sticky=tk.W, pady=CONTROL_PAD_Y)
        self.__add_consequent_button.grid(row=2, column=1, columnspan=2, pady=CONTROL_PAD_Y, sticky=tk.NSEW)
        self.__edit_consequent_button.grid(row=3, column=1, columnspan=2, pady=CONTROL_PAD_Y, sticky=tk.NSEW)
        self.__remove_consequent_button.grid(row=4, column=1, columnspan=2, pady=CONTROL_PAD_Y, sticky=tk.NSEW)

        self.__buttons_frame.grid(row=2, column=0, sticky=tk.NSEW, padx=FRAME_PAD_X, pady=FRAME_PAD_Y)
        self.__ok_button.grid(row=0, column=0, sticky=tk.E)
        self.__cancel_button.grid(row=0, column=1, sticky=tk.W)

        self.rowconfigure(1, weight=1)
        self.columnconfigure(0, weight=1)
        self.__implication_frame.columnconfigure(0, weight=1, uniform='fred')
        self.__implication_frame.columnconfigure(1, weight=1, uniform='fred')

        self.__implication_frame.rowconfigure(0, weight=1, uniform='fred')

        self.__antecedent_frame.rowconfigure(0, weight=1)
        self.__antecedent_frame.columnconfigure(0, weight=1)
        self.__antecedent_frame.columnconfigure(1, weight=1)
        self.__antecedent_frame.columnconfigure(2, weight=1)
        self.__antecedent_frame.columnconfigure(3, weight=1)
        self.__consequent_frame.rowconfigure(0, weight=1)
        self.__consequent_frame.columnconfigure(0, weight=1)
        self.__consequent_frame.columnconfigure(1, weight=1)
        self.__consequent_frame.columnconfigure(2, weight=1)
        self.__consequent_frame.columnconfigure(3, weight=1)

        self.__buttons_frame.columnconfigure(0, weight=1)
        self.__buttons_frame.columnconfigure(1, weight=1)

        self._set_geometry(width_ratio=WINDOW_WIDTH_RATIO, height_ratio=WINDOW_HEIGHT_RATIO)

    def __ok(self):
        """

        :return:
        """
        try:
            self.__constraint.name = self.__name_entry_var.get()
            self.__constraint.description = self.__description_text.get(1.0, tk.END)
            self.__constraint.antecedent = self.__antecedent
            self.__constraint.antecedent_all = self.__antecedent_all_var.get()
            self.__constraint.consequent = self.__consequent
            self.__constraint.consequent_all = self.__consequent_all_var.get()

            self.__callback(self.__constraint)
            self.grab_release()
            self.destroy()
        except BGError as e:
            messagebox.showerror('Error', e.message, parent=self)

    def __on_select_antecedent(self, id_: int) -> None:
        self.__selected_antecedent = next((a for a in self.__antecedent if a.id_ == id_), None)
        # Enable widgets
        change_controls_state(tk.NORMAL,
                              self.__edit_antecedent_button,
                              self.__remove_antecedent_button)

    def __on_select_consequent(self, id_: int) -> None:
        self.__selected_consequent = next((c for c in self.__consequent if c.id_ == id_), None)
        # Enable widgets
        change_controls_state(tk.NORMAL,
                              self.__edit_consequent_button,
                              self.__remove_consequent_button)

    def __on_add_antecedent(self):
        SimpleConstraintWindow(self, callback=self.__add_antecedent)

    def __add_antecedent(self, ant: SimpleConstraint):
        ant, index = self.__validate_constraint(ant, antecedent=True, added=True)
        self.__antecedent.append(ant)
        self.__antecedent_listbox.add_item(ant, index=index)
        self.__selected_antecedent = ant
        # Enable controls
        change_controls_state(tk.NORMAL,
                              self.__edit_antecedent_button,
                              self.__remove_antecedent_button)

    def __on_edit_antecedent(self):
        if self.__selected_antecedent:
            SimpleConstraintWindow(self, constraint=self.__selected_antecedent, callback=self.__edit_antecedent)

    def __edit_antecedent(self, ant: SimpleConstraint):
        ant, index = self.__validate_constraint(ant, antecedent=True, added=False)
        self.__antecedent_listbox.rename_item(ant, index=index)
        # Replace selected antecedent with edited
        self.__antecedent.remove(self.__selected_antecedent)
        self.__antecedent.append(ant)
        self.__antecedent_listbox.select_item(ant)
        self.__selected_antecedent = ant

    def __remove_antecedent(self):
        if self.__selected_antecedent:
            self.__antecedent.remove(self.__selected_antecedent)
            self.__antecedent_listbox.remove_item_recursively(self.__selected_antecedent)
            self.__selected_antecedent = None
            # Disable widgets
            change_controls_state(tk.DISABLED,
                                  self.__edit_antecedent_button,
                                  self.__remove_antecedent_button)

    def __on_add_consequent(self):
        SimpleConstraintWindow(self, callback=self.__add_consequent)

    def __add_consequent(self, con: SimpleConstraint):
        con, index = self.__validate_constraint(con, antecedent=False, added=True)
        self.__consequent.append(con)
        self.__consequent_listbox.add_item(con, index=index)
        self.__selected_consequent = con
        # Enable controls
        change_controls_state(tk.NORMAL,
                              self.__edit_consequent_button,
                              self.__remove_consequent_button)

    def __on_edit_consequent(self):
        if self.__selected_consequent:
            SimpleConstraintWindow(self, constraint=self.__selected_consequent, callback=self.__edit_consequent)

    def __edit_consequent(self, con: SimpleConstraint):
        con, index = self.__validate_constraint(con, antecedent=False, added=True)
        self.__consequent_listbox.rename_item(con, index=index)
        # Replace selected antecedent with edited
        self.__consequent.remove(self.__selected_consequent)
        self.__consequent.append(con)
        self.__consequent_listbox.select_item(con)
        self.__selected_consequent = con

    def __remove_consequent(self):
        if self.__selected_consequent:
            self.__consequent.remove(self.__selected_consequent)
            self.__consequent_listbox.remove_item_recursively(self.__selected_consequent)
            self.__selected_consequent = None
            change_controls_state(tk.DISABLED,
                                  self.__edit_consequent_button,
                                  self.__remove_consequent_button)

    def __get_antecedent_names(self) -> List[str]:
        return [a.name for a in self.__antecedent]

    def __get_consequent_names(self) -> List[str]:
        return [c.name for c in self.__consequent]

    @staticmethod
    def __get_element_index(str_list: List[str], name: str):
        if name not in str_list:
            str_list.append(name)
        return sorted(str_list).index(name)

    def __validate_constraint(self, ctr: SimpleConstraint, antecedent: bool, added: bool) -> \
            Tuple[SimpleConstraint, int]:
        """

        :param ctr:
        :param antecedent:
        :param added:
        :return:
        """
        ctr.name = normalize_name(ctr.name)
        selected_ctr = None if added else self.__selected_antecedent if antecedent else self.__selected_consequent
        names = [a.name for a in self.__antecedent] if antecedent else [c.name for c in self.__consequent]
        if ctr.name in names and not (selected_ctr is not None and selected_ctr.id_ == ctr.id_):
            # If the name is contained in "names", and it's not because the constraint is edited
            ctr_type_string = 'Antecedent' if antecedent else 'Consequent'
            raise BGError(f'{ctr_type_string} already exists in complex constraint.')

        if not ctr.components_ids:
            raise BGError('Constraint must contain components.')
        elif ctr.max_ is None and ctr.min_ is None:
            raise BGError('Constraint has to have at least 1 bound.')

        return ctr, self.__get_element_index(names, ctr.name)


