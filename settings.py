import json
from collections import deque
from json import JSONDecodeError
from typing import Deque, Optional, Dict
import os
import copy

from code_generator.code_generator import SYMBOLS, CN_SYMBOL, IN_SYMBOL, INSTANCES_FACTS
from json_converter import get_json_string

CONFIGURATION_FILE_NAME = './.settings.json'
MAX_RECENTLY_OPENED_PROJECTS_COUNT = 15


class ProjectInfo:
    def __init__(self, root_name: str, path: str):
        self.root_name = root_name
        self.path = path

    @classmethod
    def from_json(cls, data):
        """Necessary to create an instance from JSON"""
        return cls(**data)


class Settings:
    def __init__(self, recently_opened_projects: Deque[ProjectInfo] = None, theme_id: str = 'light',
                 shown_predicates_dict: Dict[str, bool] = None):
        self.recently_opened_projects: Deque[ProjectInfo] = recently_opened_projects if recently_opened_projects is not None \
            else deque([], maxlen=MAX_RECENTLY_OPENED_PROJECTS_COUNT)
        self.theme_id: str = theme_id
        # By default show only IN and CN predicates
        self.shown_predicates_dict: Dict[str, bool] = shown_predicates_dict if shown_predicates_dict is not None \
            else {s: (s == IN_SYMBOL or s == CN_SYMBOL) for s in [INSTANCES_FACTS] + SYMBOLS}

    @classmethod
    def get_settings(cls):
        try:
            if os.path.exists(CONFIGURATION_FILE_NAME):
                with open(CONFIGURATION_FILE_NAME, 'r') as file:
                    json_string = file.read()
                    data = json.loads(json_string)
                    recent_projects_list = list(map(ProjectInfo.from_json, data['recently_opened_projects']))
                    data['recently_opened_projects'] = deque(recent_projects_list,
                                                             maxlen=MAX_RECENTLY_OPENED_PROJECTS_COUNT)
                    return cls(**data)

        except JSONDecodeError as e:
            print(f'Error: {str(e)}')
            file.close()

        open(CONFIGURATION_FILE_NAME, 'w').close()
        return cls()

    def __save_changes(self) -> None:
        with open(CONFIGURATION_FILE_NAME, 'w') as file:
            self_copy = copy.deepcopy(self)
            self_copy.recently_opened_projects = list(self.recently_opened_projects)
            json_string = get_json_string(self_copy, sort=False)
            file.write(json_string)
            file.close()

    def add_recently_opened_project(self, root_name, path) -> None:
        project = self.__find_project(path)
        if project:
            self.recently_opened_projects.remove(project)
            project.root_name = root_name
        else:
            project = ProjectInfo(root_name, path)
        self.recently_opened_projects.appendleft(project)
        self.__save_changes()

    def change_theme(self, theme_id):
        self.theme_id = theme_id
        self.__save_changes()

    def __find_project(self, path) -> Optional[ProjectInfo]:
        for project in self.recently_opened_projects:
            if project.path == path:
                return project
        return None

