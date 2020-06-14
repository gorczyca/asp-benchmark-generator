"""Provides helper functions for conversion between objects and JSON strings."""


import json

from model.model import Model


def model_to_json(model: Model) -> str:
    """Converts the Hierarchy object to JSON string."""
    return json.dumps(model, default=lambda obj: obj.__dict__, sort_keys=True, indent=4)


def json_to_model(json_string: str) -> Model:
    """Converts the JSON string to the Hierarchy object"""
    return Model.from_json(json.loads(json_string))

