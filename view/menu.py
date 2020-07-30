import tkinter as tk
from tkinter import filedialog, messagebox

from pubsub import pub

import actions
from exceptions import BGError
from file_operations import JSON_EXTENSION, extract_file_name, open_, LP_EXTENSION, CSV_EXTENSION, solve
from model.helpers import json_converter
from state import State
import code_generator.code_generator as gen
from view import style
from view.ask_string_window import AskStringWindow


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
        run_menu.add_command(label='Solve', command=solve)
        # run_menu.add_separator()
        # run_menu.add_command(label='Generate & solve', command=self.__generate_and_solve)

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

    def __generate_and_solve(self):
        pass

    def __change_root_name(self, root_name: str):
        try:
            self.__state.model.set_root_name(root_name)
        except BGError as e:
            messagebox.showerror('Error', e.message, parent=self.__parent_frame)

    def __on_change_root_name(self):
        AskStringWindow(self.__parent_frame, self.__change_root_name, 'Set root name', f'Set new root name (current is {self.__state.model.root_name}).')

    def __generate(self):
        code = gen.generate_code(self.__state.model)
        file = filedialog.asksaveasfile(mode='w', defaultextension=LP_EXTENSION)
        if file is not None:
            file.write(code)
            file.close()
            file_name = extract_file_name(file.name)
            messagebox.showinfo('Export successful.', f'Exported successfully to\n{file_name}.')

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
        pub.sendMessage(actions.RESET)

    def __on_open(self):
        if not self.__state.is_saved:
            answer = messagebox.askyesnocancel('Open', 'You have some unsaved changes, '
                                                       'would you like to save them?')
            if answer is None:
                return
            elif answer:
                self.__on_save_as()
        open_(self.__parent_frame)

    def __on_save(self):
        json_string = json_converter.model_to_json(self.__state.model)
        if self.__state.file:
            with open(self.__state.file.name, 'w') as file_:
                self.__save(file_, json_string)
        else:
            self.__on_save_as()

    def __on_save_as(self):
        json_string = json_converter.model_to_json(self.__state.model)
        file = filedialog.asksaveasfile(mode='w', defaultextension=JSON_EXTENSION)
        if file is not None:  # TODO: czy to potrzebne
            self.__save(file, json_string)
            self.__state.file = file
            messagebox.showinfo('Saved successfully', f'Saved succesfully to\n{file.name}.')

    def __save(self, file, json_string):
        file.write(json_string)
        file.close()
        file_name = extract_file_name(file.name)
        self.__state.is_saved = True
        pub.sendMessage(actions.MODEL_SAVED, file_name=file_name)
