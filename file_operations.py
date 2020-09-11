"""Common file operations."""

import ntpath
from json import JSONDecodeError
from tkinter import filedialog, messagebox
from typing import Dict, Optional, Callable, Any
from threading import Event

from pubsub import pub

import actions
from code_generator import generate_code
from exceptions import BGError
from model import Model
from settings import Settings
from solver import Solver, InstanceRepresentation
from state import State

JSON_EXTENSION = '.json'
LP_EXTENSION = '.lp'
CSV_EXTENSION = '.csv'

LP_FILE_TYPE = ('ASP Logic Program file', f'*{LP_EXTENSION}')
JSON_FILE_TYPE = ('JSON file', f'*{JSON_EXTENSION}')
ALL_FILES_TYPE = ("All Files", "*.*")


def extract_file_name(path: str):
    """Extracts the file name from path.

    :param path: Path.
    :return: File name.
    """
    head, tail = ntpath.split(path)
    return tail or ntpath.basename(head)


def open_project(callback: Optional[Callable] = None) -> None:
    """Allows user to open the project by selecting from file exporer.

    :param callback: Callback function, to be executed after opening the project.
    """
    file_name = filedialog.askopenfilename(filetypes=(JSON_FILE_TYPE, ALL_FILES_TYPE))
    if file_name:
        load_from_file(file_name, callback)


def load_from_file(file_name: str, callback: Optional[Callable]):
    """Loads model from file.

    :param file_name: File path.
    :param callback: Callback function, to be executed after loading model from file.
    """
    try:
        with open(file_name, mode='r') as file:
            state = State()
            json = file.read()
            model = Model.from_json(json)

            state.file = file
            state.model = model
            Settings.get_settings().add_recently_opened_project(model.root_name, file_name)

            if callback is not None:
                callback()

            pub.sendMessage(actions.MODEL_SAVED, file_name=file_name)
            pub.sendMessage(actions.MODEL_LOADED)

    except JSONDecodeError as e:
        messagebox.showerror('Error', f'Error while opening the project file.\n{e}')
    except BGError as e:
        messagebox.showerror('Error', e)
    except FileNotFoundError as e:
        messagebox.showerror('File not found.', str(e))


def solve(input_path: str,
          output_path: str,
          answer_sets_count: int = 1,
          instance_representation: InstanceRepresentation = InstanceRepresentation.Textual,
          shown_predicates_only: bool = True,
          show_predicates_symbols: bool = True,
          on_progress: Optional[Callable[[int], Any]] = None,
          stop_event: Event = None) -> bool:
    """Solves the input logic program and exports answer sets to the output file.

    :param input_path: Input ASP encoding file path.
    :param output_path: Output csv file path.
    :param answer_sets_count: Number of answer sets.
    :param instance_representation: Desired instance representation.
    :param shown_predicates_only: If set to True, then only the predicates that appear in the "#show" directive
            are exported; Otherwise all of them.
    :param show_predicates_symbols: If set to True, then predicate symbols are exported to output file;
            Otherwise only the predicate's arguments are exported.
    :param on_progress: Callback, executed whenever a model is obtained.
    :param stop_event: Used to communicate with the solver thread (to terminate it from the outside).
    :return: True if solving completed; False if interrupted.
    """
    solver = Solver(output_path,
                    input_path,
                    instance_representation,
                    show_predicates_symbols,
                    answer_sets_count,
                    shown_predicates_only,
                    on_progress,
                    stop_event)

    solving_complete = solver.solve()

    Settings.get_settings().save_changes(program_to_solve_path=input_path, answer_sets_count=answer_sets_count,
                                         show_predicates_symbols=show_predicates_symbols, shown_predicates_only=shown_predicates_only,
                                         instance_representation=instance_representation)
    return solving_complete


def generate(output_path: Optional[str],
             model: Model,
             show_all_predicates: bool,
             shown_predicates_dict: Dict[str, bool]):
    """Generates output logic program based on model.

    :param output_path: Output file path.
    :param model: Model to encode in output logic program.
    :param show_all_predicates: If True, then no "#show" directive is generated;
    :param shown_predicates_dict: Predicates to generate the "#show" directives for.
    """
    if not output_path:
        raise BGError('Logic program output path must be specified.')

    code = generate_code(model, show_all_predicates, shown_predicates_dict)
    with open(output_path, 'w') as output_file:
        output_file.write(code)
        Settings.get_settings().save_changes(shown_predicates_dict=shown_predicates_dict)
