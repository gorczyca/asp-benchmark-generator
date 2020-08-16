import ntpath
import sys
from tkinter import filedialog, messagebox
from typing import TextIO, Optional
from threading import Event

from pubsub import pub

import actions
from exceptions import BGError
from model.model import Model
from settings import Settings
from solver.solver import Solver, InstanceRepresentation
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
                                id_representation=False, show_predicates_symbols=True, shown_predicates_only=True)
                solver.solve()
                messagebox.showinfo('Solving complete', f'Answer set exported to {output_file_name}')
    except:
        messagebox.showerror('Error', f'Error while solving the file file.\n{sys.exc_info()[0]}')


def solve_(parent_frame, input_path: str, output_path: str, answer_sets_count: int = 1,
           instance_representation: InstanceRepresentation = InstanceRepresentation.Textual,
           shown_predicates_only: bool = True, show_predicates_symbols: bool = True,
           settings: Settings = None, on_progress=None, stop_event: Event = None):
    solver = Solver(output_path, input_path, answer_sets_count=answer_sets_count,
                    show_predicates_symbols=show_predicates_symbols, shown_predicates_only=shown_predicates_only,
                    instance_representation=instance_representation, on_progress=on_progress, stop_event=stop_event)
    solver.solve(parent_frame)
    # TODO:
    # messagebox.showinfo('Solving complete', f'Answer set exported to {output_path}', parent=parent_frame)
    # TODO:
    if not settings:
        settings = Settings.get_settings()
    settings.save_changes(program_to_solve_path=input_path, answer_sets_count=answer_sets_count,
                          show_predicates_symbols=show_predicates_symbols, shown_predicates_only=shown_predicates_only,
                          instance_representation=instance_representation)


