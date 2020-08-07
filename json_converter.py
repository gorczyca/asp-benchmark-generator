"""Provides helper functions for conversion between objects and JSON strings."""

import json
from typing import Any


def get_json_string(object_: Any, sort: bool = True) -> str:
    """Converts the Hierarchy object to JSON string."""
    return json.dumps(object_, default=lambda obj: obj.__dict__, sort_keys=sort, indent=4)

# TODO: move this from here



