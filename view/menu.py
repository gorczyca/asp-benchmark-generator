import tkinter as tk
from tkinter import filedialog, messagebox

from pubsub import pub

import actions
from file_operations import JSON_EXTENSION, extract_file_name, open_project, JSON_FILE_TYPE, ALL_FILES_TYPE
import json_converter
from state import State
from view import style
from view.ask_string_window import AskStringWindow
from view.generate_and_solve_window import GenerateAndSolveWindow
from view.generate_window import GenerateWindow
from view.solve_window import SolveWindow


class Menu:
    def __init__(self, parent_frame):

        self.__menu = tk.Menu(parent_frame, bg=style.BACKGROUND_COLOR_PRIMARY)   # Cannot change it on Windows / OSX
        self.__state = State()
        self.__parent_frame = parent_frame

        file_menu = tk.Menu(tearoff=0, bg=style.BACKGROUND_COLOR_PRIMARY)
        file_menu.add_command(label='New', command=self.__on_new)
        file_menu.add_separator()
        file_menu.add_command(label='Open', command=self.__on_open)
        file_menu.add_command(label='Save', command=self.__on_save)
        file_menu.add_command(label='Save as...', command=self.__on_save_as)

        run_menu = tk.Menu(tearoff=0, bg=style.BACKGROUND_COLOR_PRIMARY)

        run_menu.add_command(label='Generate', command=self.__generate)
        run_menu.add_command(label='Solve', command=self.__on_solve)
        run_menu.add_separator()
        run_menu.add_command(label='Generate & solve', command=self.__generate_and_solve)

        edit_menu = tk.Menu(tearoff=0, bg=style.BACKGROUND_COLOR_PRIMARY)
        edit_menu.add_command(label='Change root name', command=self.__on_change_root_name)

        help_menu = tk.Menu(tearoff=0, bg=style.BACKGROUND_COLOR_PRIMARY)
        about_menu = tk.Menu(tearoff=0, bg=style.BACKGROUND_COLOR_PRIMARY)

        self.__menu.add_cascade(label='File', menu=file_menu)
        self.__menu.add_cascade(label='Edit', menu=edit_menu)
        self.__menu.add_cascade(label='Help', menu=help_menu)
        self.__menu.add_cascade(label='About', menu=about_menu)
        self.__menu.add_cascade(label='Run', menu=run_menu)

        parent_frame.config(menu=self.__menu)

    def __on_solve(self):
        SolveWindow(self.__parent_frame)

    def __generate_and_solve(self):
        GenerateAndSolveWindow(self.__parent_frame)

    def __change_root_name(self, root_name: str):
        self.__state.model.set_root_name(root_name)

    def __on_change_root_name(self):
        AskStringWindow(self.__parent_frame, self.__change_root_name, 'Set root name',
                        f'Set new root name:', string=self.__state.model.root_name)

    def __generate(self):
        GenerateWindow(self.__parent_frame, None)

    def __on_new(self):
        if not self.__state.is_saved:
            answer = messagebox.askyesnocancel('New', 'You have some unsaved changes, '
                                                      'would you like to save them?')
            if answer is None:
                return
            elif answer:
                self.__on_save_as()
        self.__new()

    def __new(self):
        AskStringWindow(self.__parent_frame, self.__reset, window_title='Set root name',
                        prompt_text='Enter name of the root component.')

    def __reset(self, root_name: str):
        self.__state.model.set_root_name(root_name)
        self.__state.is_saved = True
        self.__state.model.clear()
        self.__state.file = None
        pub.sendMessage(actions.RESET)

    def __on_open(self):
        if not self.__state.is_saved:
            answer = messagebox.askyesnocancel('Open', 'You have some unsaved changes, '
                                                       'would you like to save them?')
            if answer is None:
                return
            elif answer:
                self.__on_save_as()
        open_project(None)

    def __on_save(self):
        json_string = json_converter.get_json_string(self.__state.model)
        if self.__state.file:
            with open(self.__state.file.name, 'w') as file_:
                self.__save(file_, json_string)
        else:
            self.__on_save_as()

    def __on_save_as(self):
        json_string = json_converter.get_json_string(self.__state.model)
        file_name = filedialog.asksaveasfilename(defaultextension=JSON_EXTENSION,
                                                 filetypes=(JSON_FILE_TYPE, ALL_FILES_TYPE),
                                                 initialfile=self.__state.model.root_name)
        try:
            with open(file_name, 'w') as file:
                self.__save(file, json_string)
                self.__state.file = file
                messagebox.showinfo('Saved successfully', f'Saved succesfully to\n{file.name}.')
        except FileNotFoundError as e:
            messagebox.showerror('File not found.', str(e))

    def __save(self, file, json_string):
        file.write(json_string)
        file_name = extract_file_name(file.name)
        self.__state.is_saved = True
        self.__state.settings.add_recently_opened_project(self.__state.model.root_name, file.name)
        pub.sendMessage(actions.MODEL_SAVED, file_name=file_name)
