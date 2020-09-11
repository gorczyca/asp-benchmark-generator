"""Provides functionality for solving the ASP code and extraction of answer sets."""
from threading import Event
from typing import Dict, Any, Callable, Optional

import clingo
import csv
import re
from enum import IntEnum


from code_generator import DOMAIN_STRING, PRD_SYMBOL


class InstanceRepresentation(IntEnum):
    """Define instance representation in exported answer sets file.

    Id: Instance is represented by its id.
    Textual: Instance is represented by its component's name.
    Mixed: Instance is represented by <component's name>_<id>
    """
    Id = 0
    Textual = 1
    Mixed = 2


ANSWER_SET_DELIMITER = ' '
ARGUMENT_DELIMITER = ','

FACT_RE = r'\w+\(\d+\.\.\d+\)\.'

# Stores predicates and indexes of the arguments, where ints don't represent any instance of a component
PREDICATES_TO_PRESERVE_INTEGERS_IN = {
    PRD_SYMBOL: [2]
}


def inclusive_range(start, end):
    """Returns range that includes the upper bound."""
    return range(start, end + 1)


def get_instance_range_and_name(fact: str):
    """Extract from an instance fact the component's name and range of its instances.
    E.g. given a fact:
        "component1(13..18)"
    function will return a tuple:
        (inclusive_range(13, 18), "component1").

    :param fact: Instance fact to extract.
    :return: A tuple of the form (range, component's name).
    """
    fact_parts = re.split(r'\(|\)|\.\.', fact)
    # Remove the 'Domain' substring if that component has symmetry breaking
    name = fact_parts[0].replace(DOMAIN_STRING, '')
    return inclusive_range(int(fact_parts[1]), int(fact_parts[2])), name


class Solver:
    """Provides functionality to solve instances of configuration problem and extract answer sets into a csv file.

    Attributes:
         input_file_name: Input ASP encoding file path.
         output_file_name: Output csv file path.
         instance_representation: Desired instance representation.
         show_predicates_symbols: If set to True, then predicate symbols are exported to output file;
            Otherwise only the predicate's arguments are exported.
         answer_sets_count: Number of answer sets.
         shown_predicates_only: If set to True, then only the predicates that appear in the "#show" directive
            are exported; Otherwise all of them.
         on_progress: Callback, executed whenever a model is obtained.
         stop_event: Used to communicate with the solver thread (to terminate it from the outside).
    """
    def __init__(self,
                 output_file_name: str,
                 input_file_name: str,
                 instance_representation: InstanceRepresentation,
                 show_predicates_symbols: bool,
                 answer_sets_count: int,
                 shown_predicates_only: bool,
                 on_progress: Optional[Callable[[int], Any]],
                 stop_event: Event):
        self.__input_file_name: str = input_file_name
        self.__shown_atoms_only: bool = shown_predicates_only
        self.__stop_event: Event = stop_event
        self.__output_file_name: str = output_file_name
        self.__instance_representation: InstanceRepresentation = instance_representation
        self.__show_predicates_symbols: bool = show_predicates_symbols
        self.__answer_sets_count: int = answer_sets_count
        self.__on_progress: Optional[Callable[[int], Any]] = on_progress

        self.__completed: bool = True
        self.__control: clingo.Control = clingo.Control()
        self.__output_csv_file_writer = None
        self.__current_answer_set: int = 0
        self.__instances_dictionary: Dict[range, str] = {}

    def __get_instances_dictionary(self):
        """Traverses through input logic file looking for instance predicates
        and builds the instances dictionary out of them
        """
        fact_re = re.compile(FACT_RE)
        with open(self.__input_file_name, mode='r') as file:
            for line in file:
                if fact_re.match(line):
                    range_, name = get_instance_range_and_name(line)
                    self.__instances_dictionary[range_] = name

    def __get_arguments_representations(self, symbol: clingo.Symbol):
        """Extracts representation of predicates arguments.

        :param symbol: Symbol (predicate) to extract the argument's representation from.
        :return: List of representations of predicates arguments.
        """
        symbol_arguments = []
        for i, arg in enumerate(symbol.arguments):
            if arg.type == clingo.SymbolType.Number:
                if self.__instance_representation == InstanceRepresentation.Id:
                    symbol_arguments.append(arg.number)
                else:
                    if symbol.name in PREDICATES_TO_PRESERVE_INTEGERS_IN:
                        if i in PREDICATES_TO_PRESERVE_INTEGERS_IN[symbol.name]:
                            symbol_arguments.append(arg.number)
                            continue  # If number should be preserved, finish iteration here
                    inst_name = self.__get_instance_name(arg.number)
                    if self.__instance_representation == InstanceRepresentation.Mixed:
                        inst_name += f'_{arg.number}'
                    symbol_arguments.append(inst_name)
            else:
                symbol_arguments.append(arg.string)
        return symbol_arguments

    def __get_instance_name(self, id_: int):
        """Returns the component's name of an instance id.

        :param id_: Instance's id.
        :return: Component's name.
        """
        for range_, name in self.__instances_dictionary.items():
            if id_ in range_:
                return name
        return None

    def __extract_answer_set(self, answer_set: clingo.Model):
        """Extract the answer set (of type clingo.Model) into a list of predicates.

        :param answer_set: Answer set.
        :return: List of predicates in the answer set.
        """
        row = []
        symbols = answer_set.symbols(shown=True) if self.__shown_atoms_only else answer_set.symbols(atoms=True)
        for symbol in symbols:
            symbol_args = self.__get_arguments_representations(symbol)
            row_str = ARGUMENT_DELIMITER.join([str(sym) for sym in symbol_args])
            if self.__show_predicates_symbols:
                row_str = f'{symbol.name}({row_str})'
            row.append(row_str)
        return row

    def __on_answer_set(self, answer_set: clingo.Model):
        """Callback function, executed whenever an answer set is found.

        :param answer_set: Answer set.
        """
        if self.__stop_event is not None and self.__stop_event.is_set():
            self.__completed = False  # Notify that solving has not completed
            return False    # Interrupt the solver

        row = self.__extract_answer_set(answer_set)
        self.__output_csv_file_writer.writerow(row)
        if self.__on_progress is not None:
            self.__current_answer_set += 1
            self.__on_progress(self.__current_answer_set)

    def solve(self) -> bool:
        """Starts the solver.

        :return: True if solving is completed; False if interrupted.
        """

        self.__completed = True     # Reset "completed" variable
        self.__control.load(self.__input_file_name)
        self.__get_instances_dictionary()
        self.__control.ground([('base', [])])
        self.__control.configuration.solve.models = self.__answer_sets_count
        with open(self.__output_file_name, 'w', newline='') as output_csv_file:
            self.__output_csv_file_writer = csv.writer(output_csv_file, delimiter=ANSWER_SET_DELIMITER)
            self.__control.solve(on_model=self.__on_answer_set)
            return self.__completed


