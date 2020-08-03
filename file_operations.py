import ntpath
import sys
from tkinter import filedialog, messagebox

from pubsub import pub

import actions
from exceptions import BGError
from model.helpers import json_converter
from solver.solver import Solver
from state import State

JSON_EXTENSION = '.json'
LP_EXTENSION = '.lp'
CSV_EXTENSION = '.csv'


def extract_file_name(path):
    head, tail = ntpath.split(path)
    return tail or ntpath.basename(head)


def open_(parent_frame):
    file = filedialog.askopenfile(mode='r', defaultextension=JSON_EXTENSION)
    if file:
        state = State()
        state.file = file
        json = file.read()
        model = json_converter.json_to_model(json)
        state.model = model
        file_name = extract_file_name(file.name)
        pub.sendMessage(actions.MODEL_SAVED, file_name=file_name)
        pub.sendMessage(actions.MODEL_LOADED)
    else:
        raise BGError('Error while opening the file.')


def solve():
    try:
        program_files_names = filedialog.askopenfilenames(defaultextension=LP_EXTENSION, title='Select ASP program files to solve.')
        if program_files_names:
            output_file_name = filedialog.asksaveasfilename(defaultextension=CSV_EXTENSION, title='Save output .csv file as...')
            if output_file_name:
                solver = Solver(output_file_name, *program_files_names, answer_sets_count=100,
                                id_representation=False, show_predicates=True, shown_atoms_only=True)
                solver.solve()
                messagebox.showinfo('Solving complete', f'Answer set exported to {output_file_name}')
    except:
        messagebox.showerror('Error', f'Error while solving the file file.\n{sys.exc_info()[0]}')

