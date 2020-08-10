import ntpath
import sys
from tkinter import filedialog, messagebox
from typing import TextIO, Optional

from pubsub import pub

import actions
from exceptions import BGError
from model.model import Model
from solver.solver import Solver
from state import State

JSON_EXTENSION = '.json'
LP_EXTENSION = '.lp'
CSV_EXTENSION = '.csv'


def extract_file_name(path):
    head, tail = ntpath.split(path)
    return tail or ntpath.basename(head)


def open_():
    file = filedialog.askopenfile(mode='r', defaultextension=JSON_EXTENSION)
    load_from_file(file)


def load_from_file(file: Optional[TextIO]) -> None:
    # TODO: mess with closing & opening the file!!!
    # TODO: also with throwing and catching exceptionss
    if file:
        state = State()
        state.file = file
        json = file.read()
        model = Model.from_json(json)
        state.model = model
        state.settings.add_recently_opened_project(model.root_name, file.name)
        file_name = extract_file_name(file.name)
        file.close()
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

