"""Provides helper functions for conversion between objects and JSON strings."""

import json
from typing import Any, List, Dict


def get_json_string(object_: Any, sort: bool = True) -> str:
    """Converts the object to JSON string.

    :param object_: Object
    :param sort: Whether to sort the keys.
    :return: JSON string.
    """
    return json.dumps(object_, default=lambda obj: obj.__dict__, sort_keys=sort, indent=4)


def deserialize_list(class_, data) -> List[Any]:
    """Creates a list of type class_ from json.

    :param class_: Target class.
    :param data: List of JSON objects.
    :return: List of objects of type class_.
    """
    return [] if not data else list(map(class_.from_json, data))


def deserialize_dict(dict_) -> Dict[int, Any]:
    """Maps the dict's kay to int.

    :param dict_: Input dictionary.
    :return: Dictionary with its key mapped to int.
    """
    return {int(key): val for key, val in dict_.items()}




