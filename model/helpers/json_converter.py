"""Provides helper functions for conversion between objects and JSON strings."""


import json

from model.hierarchy import Hierarchy


def hierarchy_to_json(hierarchy: Hierarchy) -> str:
    """Converts the Hierarchy object to JSON string."""
    return json.dumps(hierarchy, default=lambda obj: obj.__dict__, sort_keys=True, indent=4)


def json_to_hierarchy(json_string: str) -> Hierarchy:
    """Converts the JSON string to the Hierarchy object"""
    return Hierarchy.from_json(json.loads(json_string))

# TODO: usunąć jeżeli lambda zadziała
# def obj_dict(obj):
#     return obj.__dict__
