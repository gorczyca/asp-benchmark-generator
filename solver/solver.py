import clingo
import csv
import re
from enum import IntEnum

from code_generator import DOMAIN_STRING, PRD_SYMBOL


class InstanceRepresentation(IntEnum):
    Id = 0
    Textual = 1
    Mixed = 2


ANSWER_SET_DELIMITER = ' '
ARGUMENT_DELIMITER = ','

FACT_RE = '\w+\(\d+\.\.\d+\)\.'

# Stores predicates and indexes of the arguments, where ints don't represent any instance of a component
PREDICATES_TO_PRESERVE_INTEGERS_IN = {
    PRD_SYMBOL: [2]
}


def inclusive_range(start, end):
    return range(start, end + 1)


def get_instance_range_and_name(fact: str):
    fact_parts = re.split('\(|\)|\.\.', fact)
    # Remove the 'Domain' substring if that component has symmetry breaking
    name = fact_parts[0].replace(DOMAIN_STRING, '')
    return inclusive_range(int(fact_parts[1]), int(fact_parts[2])), name


class Solver:
    def __init__(self,
                 output_file_name,
                 input_file_name,
                 instance_representation: InstanceRepresentation,
                 show_predicates_symbols,
                 answer_sets_count,
                 shown_predicates_only,
                 on_progress,
                 stop_event):
        self.__control = clingo.Control()
        self.__input_file_name = input_file_name
        self.__shown_atoms_only = shown_predicates_only

        self.__stop_event = stop_event

        self.__instances_dictionary = {}

        self.__output_file_name = output_file_name
        self.__output_csv_file_writer = None

        self.__instance_representation = instance_representation
        self.__show_predicates_symbols = show_predicates_symbols
        self.__answer_sets_count = answer_sets_count

        self.__output_csv_file_writer = None
        self.__on_progress = on_progress
        self.__current_answer_set = 0

    def __get_instances_dictionary(self):
        fact_re = re.compile(FACT_RE)
        with open(self.__input_file_name, mode='r') as file:
            for line in file:
                if fact_re.match(line):
                    range_, name = get_instance_range_and_name(line)
                    self.__instances_dictionary[range_] = name

    def __get_arguments_representations(self, symbol):
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

    def __get_instance_name(self, id_):
        for range_, name in self.__instances_dictionary.items():
            if id_ in range_:
                return name
        return None

    def __extract_answer_set(self, answer_set):
        row = []
        symbols = answer_set.symbols(shown=True) if self.__shown_atoms_only else answer_set.symbols(atoms=True)
        for symbol in symbols:
            symbol_args = self.__get_arguments_representations(symbol)
            row_str = ARGUMENT_DELIMITER.join([str(sym) for sym in symbol_args])
            if self.__show_predicates_symbols:
                row_str = f'{symbol.name}({row_str})'
            row.append(row_str)
        return row

    def __on_answer_set(self, answer_set):
        # TODO: ???
        if self.__stop_event is not None and self.__stop_event.is_set():
            self.__control.interrupt()

        row = self.__extract_answer_set(answer_set)
        self.__output_csv_file_writer.writerow(row)
        if self.__on_progress is not None:
            self.__current_answer_set += 1
            self.__on_progress(self.__current_answer_set)

    def solve(self):
        self.__control.load(self.__input_file_name)
        self.__get_instances_dictionary()
        self.__control.ground([('base', [])])
        self.__control.configuration.solve.models = self.__answer_sets_count
        with open(self.__output_file_name, 'w', newline='') as output_csv_file:
            self.__output_csv_file_writer = csv.writer(output_csv_file, delimiter=ANSWER_SET_DELIMITER)
            self.__control.solve(on_model=self.__on_answer_set)

