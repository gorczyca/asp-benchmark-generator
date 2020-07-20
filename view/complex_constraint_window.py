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
from view.common import change_controls_state
from view import style

SELECT_COMPONENTS_WINDOW_NAME = 'Complex constraint'

CONTROL_PAD_Y = 1.5
CONTROL_PAD_X = 1.5

FRAME_PAD_Y = 10
FRAME_PAD_X = 10

WINDOW_WIDTH_RATIO = 0.8
WINDOW_HEIGHT_RATIO = 0.8


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
        self.__set_geometry()

    # HasCommonSetup
    def _create_widgets(self) -> None:
        self.__window = tk.Toplevel(self.parent_frame, bg=style.BACKGROUND_COLOR_PRIMARY)
        self.__window.grab_set()
        self.__window.title(SELECT_COMPONENTS_WINDOW_NAME)
        # Name
        self.__data_frame = ttk.Frame(self.__window)
        self.__name_entry_var = tk.StringVar(value=self.__constraint.name)
        self.__name_entry_label = ttk.Label(self.__data_frame, text='Name:')
        self.__name_entry = ttk.Entry(self.__data_frame, textvariable=self.__name_entry_var)
        # Description
        self.__description_text_label = ttk.Label(self.__data_frame, text='Description:')
        self.__description_text = tk.Text(self.__data_frame, height=8, width=40)
        if self.__constraint.description:
            self.__description_text.insert(tk.INSERT, self.__constraint.description)

        self.__implication_frame = ttk.Frame(self.__window)

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

        self.__add_antecedent_button = ttk.Button(self.__antecedent_frame, text='Add', command=self.__add_antecedent)
        self.__edit_antecedent_button = ttk.Button(self.__antecedent_frame, text='Edit', command=self.__edit_antecedent,
                                                   state=tk.DISABLED)
        self.__remove_antecedent_button = ttk.Button(self.__antecedent_frame, text='Remove', state=tk.DISABLED,
                                                     command=self.__remove_antecedent)

        self.__add_consequent_button = ttk.Button(self.__consequent_frame, text='Add', command=self.__add_consequent)
        self.__edit_consequent_button = ttk.Button(self.__consequent_frame, text='Edit', command=self.__edit_consequent,
                                                   state=tk.DISABLED)
        self.__remove_consequent_button = ttk.Button(self.__consequent_frame, text='Remove', state=tk.DISABLED,
                                                     command=self.__remove_consequent)

        # Buttons frame
        self.__buttons_frame = ttk.Frame(self.__window)
        self.__ok_button = ttk.Button(self.__buttons_frame, text='Ok', command=self.__ok)
        self.__cancel_button = ttk.Button(self.__buttons_frame, text='Cancel', command=self.__window.destroy)

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

        self.__window.rowconfigure(1, weight=1)
        self.__window.columnconfigure(0, weight=1)
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

    def __ok(self):
        # Update constraint values
        name = self.__name_entry_var.get()
        if name in self.__check_name_with:
            messagebox.showerror('Add constraint error.', f'Constraint {name} already exists.')
            return
        # TODO: check required fields
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
        # Enable widgets
        change_controls_state([
            self.__edit_antecedent_button,
            self.__remove_antecedent_button
        ], tk.NORMAL)

    def __on_select_consequent(self, id_: int) -> None:
        self.__selected_consequent = next((c for c in self.__consequent if c.id_ == id_), None)
        # Enable widgets
        change_controls_state([
            self.__edit_consequent_button,
            self.__remove_consequent_button
        ], tk.NORMAL)

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
            # Disable widgets
            change_controls_state([
                self.__edit_antecedent_button,
                self.__remove_antecedent_button
            ], tk.DISABLED)

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
            change_controls_state([
                self.__edit_consequent_button,
                self.__remove_consequent_button
            ], tk.DISABLED)

    def __set_geometry(self):
        screen_width = self.__window.winfo_screenwidth()
        screen_height = self.__window.winfo_screenheight()
        window_width = round(screen_width * WINDOW_WIDTH_RATIO)
        window_height = round(screen_height * WINDOW_HEIGHT_RATIO)
        x_pos = round((screen_width - window_width) / 2)
        y_pos = round((screen_height - window_height) / 2)
        self.__window.geometry(f'{window_width}x{window_height}+{x_pos}+{y_pos}')






