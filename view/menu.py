import tkinter as tk
from view.c_frame import CFrame
from model import json_converter
from tkinter import filedialog, messagebox
import ntpath
from pubsub import pub
from controller import actions

DEFAULT_FILE_EXTENSION = '.json'


class Menu(CFrame):
    def __init__(self, parent, parent_frame, *args, **kwargs):
        CFrame.__init__(self, parent, parent_frame, *args, **kwargs)

        self.menu = tk.Menu(parent_frame, *args, **kwargs)

        file_menu = tk.Menu(tearoff=0)
        file_menu.add_command(label='New')
        file_menu.add_separator()
        file_menu.add_command(label='Open')
        file_menu.add_command(label='Save', command=self.__save)
        file_menu.add_command(label='Save as...', command=self.__save_as)

        #TODO: finish the rest
        edit_menu = tk.Menu(tearoff=0)
        help_menu = tk.Menu(tearoff=0)
        about_menu = tk.Menu(tearoff=0)

        self.menu.add_cascade(label='File', menu=file_menu)
        self.menu.add_cascade(label='Edit', menu=edit_menu)
        self.menu.add_cascade(label='Help', menu=help_menu)
        self.menu.add_cascade(label='About', menu=about_menu)

        self.parent_frame.config(menu=self.menu)

    def __new(self):
        pass

    def __open(self):
        pass

    def __save(self):
        hierarchy = self.controller.model.get_hierarchy()
        json_string = json_converter.hierarchy_to_json(hierarchy)
        file = self.controller.file
        if file:
            with open(file.name, 'w') as file_:
                self.__save_(file_, json_string)
        else:
            self.__save_as()

    def __save_as(self):
        hierarchy = self.controller.model.get_hierarchy()
        json_string = json_converter.hierarchy_to_json(hierarchy)
        file = filedialog.asksaveasfile(mode='w', defaultextension=DEFAULT_FILE_EXTENSION)
        if file is not None: # TODO: czy to potrzebne
            self.__save_(file, json_string)
            self.controller.file = file
            messagebox.showinfo('Saved successfully', f'Saved succesfully to\n{file.name}.')

    def __save_(self, file, json_string):
        file.write(json_string)
        file.close()
        file_name = Menu.__extract_file_name(file.name)
        pub.sendMessage(actions.MODEL_SAVED, file_name=file_name)

    @staticmethod
    def __extract_file_name(path):
        head, tail = ntpath.split(path)
        return tail or ntpath.basename(head)



