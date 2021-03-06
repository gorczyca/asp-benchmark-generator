"""Stores program's default settings."""

import json
from collections import deque
from json import JSONDecodeError
from typing import Deque, Optional, Dict
import os
import copy

from code_generator import SYMBOLS, CN_SYMBOL, IN_SYMBOL, INSTANCES_FACTS
from misc.json_converter import get_json_string
from solver import InstanceRepresentation

CONFIGURATION_FILE_NAME = '../.settings.json'
MAX_RECENTLY_OPENED_PROJECTS_COUNT = 15


class ProjectInfo:
    """Stores project's information.

    Attributes:
        root_name: Name of the root component in the project's model
        path: Project's file path.
    """
    def __init__(self, root_name: str, path: str):
        self.root_name = root_name
        self.path = path

    @classmethod
    def from_json(cls, data):
        """Necessary to create an instance from JSON"""
        return cls(**data)


class Settings:
    """Stores program's default settings.

    Attributes:
        recently_opened_projects: Queue of recently opened project files.
        shown_predicates_dict: Dictionary of predicate symbols to show by the "#show" directive.
        answer_sets_count: Desired number of answer sets.
        shown_predicates_only: Whether to export only the literals present in "#show" directives
            or all of them in while solving.
        show_predicates_symbols: Whether to show only predicates' arguments or their symbols too.
        program_to_solve_path: Path of input file for the solver.
        show_all_predicates: Whether to include the "#show" directives in the generated logic program file
            at all.
        instance_representation: Default instance representation.
    """
    def __init__(self,
                 recently_opened_projects: Deque[ProjectInfo] = None,
                 shown_predicates_dict: Dict[str, bool] = None,
                 answer_sets_count: int = 1,
                 shown_predicates_only: bool = True,
                 show_predicates_symbols: bool = True,
                 program_to_solve_path: str = None,
                 show_all_predicates: bool = False,
                 instance_representation: InstanceRepresentation = InstanceRepresentation.Mixed):
        self.recently_opened_projects: Deque[ProjectInfo] = recently_opened_projects if recently_opened_projects is not None \
            else deque([], maxlen=MAX_RECENTLY_OPENED_PROJECTS_COUNT)
        # By default show only IN and CN predicates
        self.shown_predicates_dict: Dict[str, bool] = shown_predicates_dict if shown_predicates_dict is not None \
            else {s: (s == IN_SYMBOL or s == CN_SYMBOL) for s in [INSTANCES_FACTS] + SYMBOLS}
        self.answer_sets_count: int = answer_sets_count
        self.shown_predicates_only: bool = shown_predicates_only
        self.show_all_predicates: bool = show_all_predicates
        self.show_predicates_symbols: bool = show_predicates_symbols
        self.instance_representation: InstanceRepresentation = instance_representation
        self.program_to_solve_path: str = program_to_solve_path

    @classmethod
    def get_settings(cls):
        """Factory method to obtain settings from file."""
        try:
            if os.path.exists(CONFIGURATION_FILE_NAME):
                with open(CONFIGURATION_FILE_NAME, 'r') as file:
                    json_string = file.read()
                    data = json.loads(json_string)
                    recent_projects_list = list(map(ProjectInfo.from_json, data['recently_opened_projects']))
                    data['instance_representation'] = InstanceRepresentation(data['instance_representation'])
                    data['recently_opened_projects'] = deque(recent_projects_list,
                                                             maxlen=MAX_RECENTLY_OPENED_PROJECTS_COUNT)
                    return cls(**data)

        except JSONDecodeError as e:
            print(f'Error: {str(e)}')

        open(CONFIGURATION_FILE_NAME, 'w').close()  # Create new settings file.
        return cls()

    def __save_changes(self) -> None:
        """Saves the instance of Settings to a file."""
        with open(CONFIGURATION_FILE_NAME, 'w') as file:
            self_copy = copy.deepcopy(self)
            self_copy.recently_opened_projects = list(self.recently_opened_projects)
            json_string = get_json_string(self_copy, sort=False)
            file.write(json_string)

    def add_recently_opened_project(self, root_name: str, path: str) -> None:
        """Add recently opened project to recently_opened_projects queue.

        :param root_name: Name of the root component in opened project.
        :param path: Opened project's file path.
        """
        project = self.__find_project(path)
        if project:
            self.recently_opened_projects.remove(project)
            project.root_name = root_name
        else:
            project = ProjectInfo(root_name, path)
        self.recently_opened_projects.appendleft(project)
        self.__save_changes()

    def save_changes(self, **kwargs):
        """Sets settings instance arguments.

        :param kwargs: Arguments to set.
        """
        for key, val in kwargs.items():
            self.__setattr__(key, val)
        self.__save_changes()

    def __find_project(self, path: str) -> Optional[ProjectInfo]:
        """Looks for a project with a given path in the recently_opened_projects list.

        :param path: Project's file path.
        :return: Project's info if found; None otherwise.
        """
        for project in self.recently_opened_projects:
            if project.path == path:
                return project
        return None

