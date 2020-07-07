import copy
from typing import List, Optional
import tkinter as tk
from tkinter import ttk, messagebox

from model.complex_constraint import ComplexConstraint
from model.simple_constraint import SimpleConstraint
from view.abstract.base_frame import BaseFrame
from view.abstract.has_common_setup import HasCommonSetup
from view.abstract.has_controller_access import HasControllerAccess
from view.scrollbars_listbox import ScrollbarListbox
from view.simple_constraint_window import SimpleConstraintWindow

SELECT_COMPONENTS_WINDOW_NAME = 'Complex constraint'
SELECT_COMPONENTS_WINDOW_SIZE = '1080x720'


class ComplexConstraintWindow(BaseFrame,
                              HasControllerAccess,
                              HasCommonSetup):
    def __init__(self, parent, parent_frame, callback, constraint: Optional[ComplexConstraint] = None,
                 check_name_with: List[str] = None):
        BaseFrame.__init__(self, parent_frame)
        HasControllerAccess.__init__(self, parent)

        self.__callback = callback
        self.__check_name_with = check_name_with if check_name_with is not None else []

        self.__constraint: ComplexConstraint = constraint if constraint is not None \
            else ComplexConstraint()

        self.__antecedent: List[SimpleConstraint] = [] if constraint is None else [copy.deepcopy(sc)
                                                                                   for sc in constraint.antecedent]
        self.__consequent: List[SimpleConstraint] = [] if constraint is None else [copy.deepcopy(sc)
                                                                                   for sc in constraint.consequent]

        self.__selected_antecedent: Optional[SimpleConstraint] = None
        self.__selected_constraint_consequent: Optional[SimpleConstraint] = None

        HasCommonSetup.__init__(self)

    # HasCommonSetup
    def _create_widgets(self) -> None:
        self.__window = tk.Toplevel(self.parent_frame)
        self.__window.grab_set()
        self.__window.title(SELECT_COMPONENTS_WINDOW_NAME)
        self.__window.geometry(SELECT_COMPONENTS_WINDOW_SIZE)

        # Name
        self.__data_frame = tk.Frame(self.__window)
        self.__name_entry_var = tk.StringVar(value=self.__constraint.name)
        self.__name_entry_label = ttk.Label(self.__data_frame, text='Name:')
        self.__name_entry = ttk.Entry(self.__data_frame, textvariable=self.__name_entry_var)
        # Description
        self.__description_text_label = ttk.Label(self.__data_frame, text='Description:')
        self.__description_text = tk.Text(self.__data_frame, height=8, width=40)
        if self.__constraint.description:
            self.__description_text.insert(tk.INSERT, self.__constraint.description)

        self.__implication_frame = tk.Frame(self.__window)

        self.__antecedent_frame = tk.Frame(self.__implication_frame)
        self.__consequent_frame = tk.Frame(self.__implication_frame)

        self.__antecedent_listbox = ScrollbarListbox(self.__antecedent_frame, values=self.__antecedent,
                                                     heading='Condition',
                                                     extract_id=lambda ctr: ctr.id_,
                                                     extract_text=lambda ctr: ctr.name,
                                                     on_select_callback=self.__on_select_antecedent,
                                                     grid_row=0, grid_column=0, column_span=2)
        self.__consequent_listbox = ScrollbarListbox(self.__consequent_frame, values=self.__consequent,
                                                     heading='Consequence',
                                                     extract_id=lambda ctr: ctr.id_,
                                                     extract_text=lambda ctr: ctr.name,
                                                     on_select_callback=self.__on_select_consequent,
                                                     grid_row=0, grid_column=0, column_span=2)

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

        self.__add_antecedent_button = ttk.Button(self.__antecedent_frame, text='Add', command=self.__add_antecedent)
        self.__edit_antecedent_button = ttk.Button(self.__antecedent_frame, text='Edit', command=self.__edit_antecedent)
        self.__remove_antecedent_button = ttk.Button(self.__antecedent_frame, text='Remove',
                                                     command=self.__remove_antecedent)

        self.__add_consequent_button = ttk.Button(self.__consequent_frame, text='Add', command=self.__add_consequent)
        self.__edit_consequent_button = ttk.Button(self.__consequent_frame, text='Edit', command=self.__edit_consequent)
        self.__remove_consequent_button = ttk.Button(self.__consequent_frame, text='Remove',
                                                     command=self.__remove_consequent)

        # Buttons frame
        self.__buttons_frame = tk.Frame(self.__window)
        self.__ok_button = ttk.Button(self.__buttons_frame, text='Ok', command=self.__ok)
        self.__cancel_button = ttk.Button(self.__buttons_frame, text='Cancel', command=self.__window.destroy)

    def _setup_layout(self) -> None:
        self.__data_frame.grid(row=0, column=0, sticky=tk.NSEW, pady=10)
        self.__name_entry_label.grid(row=0, column=0)
        self.__name_entry.grid(row=0, column=1)
        self.__description_text_label.grid(row=0, column=2)
        self.__description_text.grid(row=0, column=3)

        self.__implication_frame.grid(row=1, column=0, sticky=tk.NSEW)
        self.__antecedent_frame.grid(row=0, column=0, sticky=tk.NSEW)
        self.__consequent_frame.grid(row=0, column=1, sticky=tk.NSEW)

        self.__antecedent_all_radiobutton.grid(row=1, column=0, sticky=tk.E)
        self.__antecedent_any_radiobutton.grid(row=1, column=1, sticky=tk.W)
        self.__add_antecedent_button.grid(row=2, column=0, columnspan=2)
        self.__edit_antecedent_button.grid(row=3, column=0, columnspan=2)
        self.__remove_antecedent_button.grid(row=4, column=0, columnspan=2)

        self.__consequent_all_radiobutton.grid(row=1, column=0, sticky=tk.E)
        self.__consequent_any_radiobutton.grid(row=1, column=1, sticky=tk.W)
        self.__add_consequent_button.grid(row=2, column=0, columnspan=2)
        self.__edit_consequent_button.grid(row=3, column=0, columnspan=2)
        self.__remove_consequent_button.grid(row=4, column=0, columnspan=2)

        self.__buttons_frame.grid(row=2, column=0, sticky=tk.NSEW)
        self.__ok_button.grid(row=0, column=0, sticky=tk.E)
        self.__cancel_button.grid(row=0, column=1, sticky=tk.W)

        self.__window.rowconfigure(1, weight=1)
        self.__window.columnconfigure(0, weight=1)
        self.__implication_frame.columnconfigure(0, weight=1, uniform='fred')
        self.__implication_frame.columnconfigure(1, weight=1, uniform='fred')

        self.__implication_frame.rowconfigure(0, weight=1, uniform='fred')

        self.__antecedent_frame.rowconfigure(0, weight=1)
        self.__antecedent_frame.columnconfigure(0, weight=1)
        self.__antecedent_frame.columnconfigure(1, weight=1)
        self.__consequent_frame.rowconfigure(0, weight=1)
        self.__consequent_frame.columnconfigure(0, weight=1)
        self.__consequent_frame.columnconfigure(1, weight=1)

        self.__buttons_frame.columnconfigure(0, weight=1)
        self.__buttons_frame.columnconfigure(1, weight=1)

        # Hide widgets
        self.__edit_antecedent_button.grid_forget()
        self.__remove_antecedent_button.grid_forget()
        self.__edit_consequent_button.grid_forget()
        self.__remove_consequent_button.grid_forget()

    def __ok(self):
        # Update constraint values
        name = self.__name_entry_var.get()
        if name in self.__check_name_with:
            messagebox.showerror('Add constraint error.', f'Constraint {name} already exists.')
            return
        self.__constraint.name = name
        self.__constraint.description = self.__description_text.get(1.0, tk.END)
        self.__constraint.antecedent = self.__antecedent
        self.__constraint.antecedent_all = self.__antecedent_all_var.get()
        self.__constraint.consequent = self.__consequent
        self.__constraint.consequent_all = self.__consequent_all_var.get()

        self.__callback(self.__constraint)
        self.__window.destroy()

    def __on_select_antecedent(self, id_: int) -> None:
        self.__selected_antecedent = next((a for a in self.__antecedent if a.id_ == id_), None)
        # Show widgets
        self.__edit_antecedent_button.grid(row=3, column=0, columnspan=2)
        self.__remove_antecedent_button.grid(row=4, column=0, columnspan=2)

    def __on_select_consequent(self, id_: int) -> None:
        self.__selected_consequent = next((c for c in self.__consequent if c.id_ == id_), None)
        # Show widgets
        self.__edit_consequent_button.grid(row=3, column=0, columnspan=2)
        self.__remove_consequent_button.grid(row=4, column=0, columnspan=2)

    def __add_antecedent(self):
        ant_names = [a.name for a in self.__antecedent]
        SimpleConstraintWindow(self, self.__window, callback=self.__on_antecedent_added, check_name_with=ant_names)

    def __on_antecedent_added(self, ant: SimpleConstraint):
        self.__antecedent.append(ant)
        ants_sorted = sorted([a.name for a in self.__antecedent])
        self.__antecedent_listbox.add_item(ant, index=ants_sorted.index(ant.name))

    def __on_antecedent_edited(self, ant: SimpleConstraint):
        ant_names_sorted = sorted([a.name for a in self.__antecedent])
        self.__antecedent_listbox.rename_item(ant, index=ant_names_sorted.index(ant.name))

    def __edit_antecedent(self):
        if self.__selected_antecedent:
            ant_names = [a.name for a in self.__antecedent]
            SimpleConstraintWindow(self, self.__window, constraint=self.__selected_antecedent,
                                   callback=self.__on_antecedent_edited, check_name_with=ant_names)

    def __remove_antecedent(self):
        if self.__selected_antecedent:
            self.__antecedent.remove(self.__selected_antecedent)
            self.__antecedent_listbox.remove_item(self.__selected_antecedent)
            self.__selected_antecedent = None
            self.__edit_antecedent_button.grid_forget()
            self.__remove_antecedent_button.grid_forget()

    def __add_consequent(self):
        con_names = [c.name for c in self.__consequent]
        SimpleConstraintWindow(self, self.__window, callback=self.__on_consequent_added, check_name_with=con_names)

    def __on_consequent_added(self, con: SimpleConstraint):
        self.__consequent.append(con)
        cons_sorted = sorted([c.name for c in self.__consequent])
        self.__consequent_listbox.add_item(con, index=cons_sorted.index(con.name))

    def __edit_consequent(self):
        if self.__selected_consequent:
            con_names = [c.name for c in self.__consequent]
            SimpleConstraintWindow(self, self.__window, constraint=self.__selected_consequent,
                                   callback=self.__on_consequent_edited, check_name_with=con_names)

    def __on_consequent_edited(self, con: SimpleConstraint):
        con_names_sorted = sorted([c.name for c in self.__consequent])
        self.__consequent_listbox.rename_item(con, index=con_names_sorted.index(con.name))

    def __remove_consequent(self):
        if self.__selected_consequent:
            self.__consequent.remove(self.__selected_consequent)
            self.__consequent_listbox.remove_item(self.__selected_consequent)
            self.__selected_consequent = None
            self.__edit_consequent_button.grid_forget()
            self.__remove_consequent_button.grid_forget()





