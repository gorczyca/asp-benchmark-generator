import json


def obj_dict(obj):
    return obj.__dict__


class Hierarchy:
    def __init__(self, hierarchy):   # TODO: renaming, confusing
        self.hierarchy = hierarchy


def hierarchy_to_json(cmp_list):
    json_string = json.dumps(Hierarchy(cmp_list), default=obj_dict, sort_keys=True, indent=4)
    return json_string
