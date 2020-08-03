import clingo
import csv
import re

from code_generator.code_generator import DOMAIN_STRING


ANSWER_SET_DELIMITER = ' '
ARGUMENT_DELIMITER = ','

FACT_RE = '\w+\(\d+\.\.\d+\)\.'


def inclusive_range(start, end):
    return range(start, end + 1)


def get_instance_range_and_name(fact: str):
    fact_parts = re.split('\(|\)|\.\.', fact)
    # Remove the 'Domain' substring if that component has symmetry breaking
    name = fact_parts[0].replace(DOMAIN_STRING, '')
    return inclusive_range(int(fact_parts[1]), int(fact_parts[2])), name


def get_instances_dictionary(*program_files_names):
    instances_dictionary = {}
    fact_re = re.compile(FACT_RE)
    for file_name in program_files_names:
        with open(file_name, mode='r') as file:
            for line in file:
                if fact_re.match(line):
                    range_, name = get_instance_range_and_name(line)
                    instances_dictionary[range_] = name
    return instances_dictionary


def get_instance_name(instances_dictionary, id_):
    for range_, name in instances_dictionary.items():
        if id_ in range_:
            return name


class Solver:
    def __init__(self, output_file_name, *program_files_names, id_representation=True, show_predicates=True,
                 answer_sets_count=0, shown_atoms_only=False, on_model_callback=None):
        self.__control = clingo.Control()
        self.__program_files_names = program_files_names
        self.__shown_atoms_only = shown_atoms_only

        self.__instances_dictionary = None

        self.__output_file_name = output_file_name
        self.__output_csv_file_writer = None

        self.__id_representation = id_representation
        self.__show_predicates = show_predicates
        self.__answer_sets_count = answer_sets_count
        self.__on_answer_set_callback = self.__on_answer_set if not on_model_callback else on_model_callback

        self.__output_csv_file_writer = None

    def __extract_answer_set(self, answer_set):
        if self.__shown_atoms_only:
            row = []
            for symbol in answer_set.symbols(shown=True):
                symbol_args = [sym.number for sym in symbol.arguments]
                if not self.__id_representation:
                    symbol_args = [get_instance_name(self.__instances_dictionary, id_) for id_ in symbol_args]
                symbol_args_str = ARGUMENT_DELIMITER.join([sym for sym in symbol_args])
                if not self.__show_predicates:
                    row.append(symbol_args_str)
                else:
                    row.append(f'{symbol.name}({symbol_args_str})')
            return row
        else:
            return answer_set.symbols(atoms=True)

    def __on_answer_set(self, answer_set):
        row = self.__extract_answer_set(answer_set)
        self.__output_csv_file_writer.writerow(row)

    def solve(self):
        for file in self.__program_files_names:
            self.__control.load(file)
        self.__instances_dictionary = get_instances_dictionary(*self.__program_files_names)
        self.__control.ground([('base', [])])
        self.__control.configuration.solve.models = self.__answer_sets_count
        with open(self.__output_file_name, 'w', newline='') as output_csv_file:
            self.__output_csv_file_writer = csv.writer(output_csv_file, delimiter=ANSWER_SET_DELIMITER)
            self.__control.solve(on_model=self.__on_answer_set_callback)
            output_csv_file.close()

