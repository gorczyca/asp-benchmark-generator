"""Provides helper functions for conversion between objects and JSON strings."""

import json
from typing import Any, List, Dict


def get_json_string(object_: Any, sort: bool = True) -> str:
    """Converts the Hierarchy object to JSON string."""
    return json.dumps(object_, default=lambda obj: obj.__dict__, sort_keys=sort, indent=4)


def deserialize_list(class_, data) -> List[Any]:
    return [] if not data else list(map(class_.from_json, data))


def deserialize_dict(dict_) -> Dict[int, Any]:
    return {int(key): val for key, val in dict_.items()}




