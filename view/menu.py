import ntpath
import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog, ttk

from pubsub import pub

import actions
from model.helpers import json_converter
from state import State
from view.abstract.base_frame import BaseFrame
import code_generator.code_generator as gen
from solver.solver import Solver
from view import style

JSON_EXTENSION = '.json'
LP_EXTENSION = '.lp'
CSV_EXTENSION = '.csv'


class Menu(BaseFrame):
    def __init__(self, parent, parent_frame, *args, **kwargs):
        BaseFrame.__init__(self, parent_frame)

        self.__menu = tk.Menu(parent_frame, bg=style.BACKGROUND_COLOR_PRIMARY, *args, **kwargs)   # Cannot change it on Windows / OSX
        self.__state = State()

        file_menu = tk.Menu(tearoff=0, bg=style.BACKGROUND_COLOR_PRIMARY)
        file_menu.add_command(label='New', command=self.__new)
        file_menu.add_separator()
        file_menu.add_command(label='Open', command=self.__open)
        file_menu.add_command(label='Save', command=self.__save)
        file_menu.add_command(label='Save as...', command=self.__save_as)

        # TODO: finish the rest
        run_menu = tk.Menu(tearoff=0, bg=style.BACKGROUND_COLOR_PRIMARY)

        run_menu.add_command(label='Generate', command=self.__generate)
        run_menu.add_command(label='Solve', command=self.__solve)
        run_menu.add_separator()
        run_menu.add_command(label='Generate & solve', command=self.__generate_and_solve)

        edit_menu = tk.Menu(tearoff=0, bg=style.BACKGROUND_COLOR_PRIMARY)
        help_menu = tk.Menu(tearoff=0, bg=style.BACKGROUND_COLOR_PRIMARY)
        about_menu = tk.Menu(tearoff=0, bg=style.BACKGROUND_COLOR_PRIMARY)

        self.__menu.add_cascade(label='File', menu=file_menu)
        self.__menu.add_cascade(label='Edit', menu=edit_menu)
        self.__menu.add_cascade(label='Help', menu=help_menu)
        self.__menu.add_cascade(label='About', menu=about_menu)
        self.__menu.add_cascade(label='Run', menu=run_menu)

        self.parent_frame.config(menu=self.__menu)

    def __solve(self):
        program_files_names = filedialog.askopenfilenames(defaultextension=LP_EXTENSION, title='Select ASP program files to solve.')
        if program_files_names:
            output_file_name = filedialog.asksaveasfilename(defaultextension=CSV_EXTENSION, title='Save output .csv file as...')
            solver = Solver(output_file_name, *program_files_names, answer_sets_count=100, id_representation=False, show_predicates=False)
            solver.solve()

    def __generate_and_solve(self):
        pass

    def __generate(self):
        # TODO:
        root_name = simpledialog.askstring('Enter root name', f'Enter name for root component.')
        if root_name:
            code, instances_dictionary = gen.generate_code(self.__state.model, root_name)
            self.__state.instances_dictionary = instances_dictionary
            file = filedialog.asksaveasfile(mode='w', defaultextension=LP_EXTENSION)
            if file is not None:  # TODO: czy to potrzebne
                file.write(code)
                file.close()
                file_name = Menu.__extract_file_name(file.name)
                messagebox.showinfo('Export successful.', f'Exported successfully to\n{file_name}.')

    def __new(self):
        if not self.__state.saved:
            answer = messagebox.askyesnocancel('New', 'You have some unsaved changes, '
                                                      'would you like to save them?')
            if answer is None:
                return
            elif answer:
                self.__save_as()
        self.__new_()

    def __new_(self):
        self.__state.saved = True
        self.__state.model.clear()
        pub.sendMessage(actions.RESET)

    def __open(self):
        if not self.__state.saved:
            answer = messagebox.askyesnocancel('Open', 'You have some unsaved changes, '
                                                       'would you like to save them?')
            if answer is None:
                return
            elif answer:
                self.__save_as()
        self.__open_()

    def __open_(self):
        file = filedialog.askopenfile(mode='r', defaultextension=JSON_EXTENSION)
        if file:
            self.__state.file = file
            json = file.read()
            model = json_converter.json_to_model(json)
            self.__state.model = model
            file_name = Menu.__extract_file_name(file.name)
            pub.sendMessage(actions.MODEL_SAVED, file_name=file_name)
            pub.sendMessage(actions.MODEL_LOADED)

    def __save(self):
        json_string = json_converter.model_to_json(self.__state.model)
        if self.__state.file:
            with open(self.__state.file.name, 'w') as file_:
                self.__save_(file_, json_string)
        else:
            self.__save_as()

    def __save_as(self):
        json_string = json_converter.model_to_json(self.__state.model)
        file = filedialog.asksaveasfile(mode='w', defaultextension=JSON_EXTENSION)
        if file is not None:  # TODO: czy to potrzebne
            self.__save_(file, json_string)
            self.__state.file = file
            messagebox.showinfo('Saved successfully', f'Saved succesfully to\n{file.name}.')

    def __save_(self, file, json_string):
        file.write(json_string)
        file.close()
        file_name = Menu.__extract_file_name(file.name)
        self.__state.saved = True
        pub.sendMessage(actions.MODEL_SAVED, file_name=file_name)

    @staticmethod
    def __extract_file_name(path):
        head, tail = ntpath.split(path)
        return tail or ntpath.basename(head)



