"""Provides helper functions for model."""

from typing import Any
import re

from misc.exceptions import BGError
import code_generator

SPACE_REPLACEMENT = '_'
VALID_NAME_REGEX = r'[a-z][a-zA-Z0-9_]*$'


def normalize_name(name: str) -> str:
    """Normalizes name and checks if it's legal.

    :param name: Name to normalize and check.
    :return: Normalized name.
    """
    if not name:
        raise BGError('Name cannot be empty.')
    name = name.replace(' ', SPACE_REPLACEMENT).lower()
    if name in code_generator.KEYWORDS:
        raise BGError(f'{name} is a keyword.')
    if not re.match(VALID_NAME_REGEX, name):
        raise BGError(f'{name} is an invalid name.\nYou may only use alphanumeric symbols and "_" '
                      f'and the first character must be a letter.')
    return name


def matches(obj: Any, **kwargs):
    """Checks if object's attributes match all the kwargs.

    :param obj: Object.
    :param kwargs: Attributes to check.
    :return: True if object matches kwargs, False, otherwise.
    """
    for key, val in kwargs.items():
        if getattr(obj, key) != val:
            return False
    return True
