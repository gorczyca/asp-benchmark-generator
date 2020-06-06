import json
from model.component import Component



def obj_dict(obj):
    return obj.__dict__


class Hierarchy:
    def __init__(self, hierarchy):   # TODO: renaming, confusing
        self.hierarchy = hierarchy

    @classmethod
    def from_json(cls, data):
        hierarchy = list(map(Component.from_json, data['hierarchy']))
        return cls(hierarchy)


def hierarchy_to_json(hierarchy):
    json_string = json.dumps(Hierarchy(hierarchy), default=obj_dict, sort_keys=True, indent=4)
    return json_string


def json_to_hierarchy(json_string):
    hierarchy = Hierarchy.from_json(json.loads(json_string))
    return hierarchy.hierarchy
