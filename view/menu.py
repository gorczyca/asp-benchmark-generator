import ntpath
import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog

from pubsub import pub

import actions
from model.helpers import json_converter
from view.abstract.has_controller_access import HasControllerAccess
from view.abstract.base_frame import BaseFrame
import code_generator.code_generator as gen

JSON_EXTENSION = '.json'
LP_EXTENSION = '.lp'


class Menu(BaseFrame, HasControllerAccess):
    def __init__(self, parent, parent_frame, *args, **kwargs):
        BaseFrame.__init__(self, parent_frame)
        HasControllerAccess.__init__(self, parent)

        self.__menu = tk.Menu(parent_frame, *args, **kwargs)

        file_menu = tk.Menu(tearoff=0)
        file_menu.add_command(label='New', command=self.__new)
        file_menu.add_separator()
        file_menu.add_command(label='Open', command=self.__open)
        file_menu.add_command(label='Save', command=self.__save)
        file_menu.add_command(label='Save as...', command=self.__save_as)

        # TODO: finish the rest
        edit_menu = tk.Menu(tearoff=0)
        help_menu = tk.Menu(tearoff=0)
        about_menu = tk.Menu(tearoff=0)

        self.__menu.add_cascade(label='File', menu=file_menu)
        self.__menu.add_cascade(label='Edit', menu=edit_menu)
        self.__menu.add_cascade(label='Help', menu=help_menu)
        self.__menu.add_cascade(label='About', menu=about_menu)
        self.__menu.add_command(label='Generate', command=self.__generate)

        self.parent_frame.config(menu=self.__menu)

    def __generate(self):
        # TODO:
        root_name = simpledialog.askstring('Enter root name', f'Enter name for root component.')
        if root_name:
            code = gen.generate_code(self.controller.model, root_name)
            file = filedialog.asksaveasfile(mode='w', defaultextension=LP_EXTENSION)
            if file is not None:  # TODO: czy to potrzebne
                file.write(code)
                file.close()
                file_name = Menu.__extract_file_name(file.name)
                messagebox.showinfo('Export successful.', f'Exported successfully to\n{file_name}.')

    def __new(self):
        if not self.controller.saved:
            answer = messagebox.askyesnocancel('New', 'You have some unsaved changes, '
                                                      'would you like to save them?')
            if answer is None:
                return
            elif answer:
                self.__save_as()
        self.__new_()

    def __new_(self):
        self.controller.saved = True
        self.controller.model.clear()
        pub.sendMessage(actions.RESET)

    def __open(self):
        if not self.controller.saved:
            answer = messagebox.askyesnocancel('Open', 'You have some unsaved changes, '
                                                       'would you like to save them?')
            if answer is None:
                return
            elif answer:
                self.__save_as()
        self.__open_()

    def __open_(self):
        file = filedialog.askopenfile(mode='r', defaultextension=JSON_EXTENSION)
        if file is not None:
            self.controller.file = file
            json = file.read()
            model = json_converter.json_to_model(json)
            self.controller.model = model
            file_name = Menu.__extract_file_name(file.name)
            pub.sendMessage(actions.MODEL_SAVED, file_name=file_name)
            pub.sendMessage(actions.HIERARCHY_CREATED)

    def __save(self):
        json_string = json_converter.model_to_json(self.controller.model)
        if self.controller.file:
            with open(self.controller.file.name, 'w') as file_:
                self.__save_(file_, json_string)
        else:
            self.__save_as()

    def __save_as(self):
        json_string = json_converter.model_to_json(self.controller.model)
        file = filedialog.asksaveasfile(mode='w', defaultextension=JSON_EXTENSION)
        if file is not None:  # TODO: czy to potrzebne
            self.__save_(file, json_string)
            self.controller.file = file
            messagebox.showinfo('Saved successfully', f'Saved succesfully to\n{file.name}.')

    def __save_(self, file, json_string):
        file.write(json_string)
        file.close()
        file_name = Menu.__extract_file_name(file.name)
        self.controller.saved = True
        pub.sendMessage(actions.MODEL_SAVED, file_name=file_name)

    @staticmethod
    def __extract_file_name(path):
        head, tail = ntpath.split(path)
        return tail or ntpath.basename(head)



