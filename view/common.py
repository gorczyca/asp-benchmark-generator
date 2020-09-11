"""Common view functions."""

import os
import tkinter as tk
from typing import Optional, TextIO, Any, Tuple

STRING_MAX_LENGTH = 10
REST_SYMBOL = '...'

BOOLEAN_TO_STRING_DICT = {
    True: 'yes',
    False: 'no',
    None: ''
}


def trim_string(string: str, length=STRING_MAX_LENGTH, rest_symbol=REST_SYMBOL) -> str:
    """Trims string to be maximally of 'length' length. The trimmed-off part is replaced by 'rest_symbol'
    indicating that the string is not full.

    :param string: String to trim.
    :param length: Maximal length of the string.

    :returns Trimmed string.
    """
    if len(string) <= length:
        return string
    rest_symbol_length = len(rest_symbol)
    return f'{string[0:length-rest_symbol_length]}{rest_symbol}'


def change_controls_state(state=tk.NORMAL, *controls):
    """Changes all controls' states to state.

    :param state: Desired state.
    :param controls: Controls to change the state of.
    """
    for c in controls:
        c.config(state=state)


def get_target_file_location(file: Optional[TextIO], root_name: str, suffix: str = '', extension: str = '') -> \
        Tuple[Optional[str], Optional[str]]:
    """Creates file location.

    :param file: File, to extract the directory path from.
    :param root_name: Name of the root component.
    :param suffix: File name suffix.
    :param extension: Extension.
    :return: File location.
    """
    if file is not None and root_name:
        dir_name = os.path.dirname(file.name)
        file_name = f'{root_name}_{suffix}{extension}'
        path = os.path.join(dir_name, file_name)
        return os.path.normpath(path), file_name  # Normalize the back- & front-slashes
    return None, None


def set_spinbox_var_value(spinbox_var: tk.IntVar, value: Optional[int]):
    """Sets the spinboxes' values to value if it exists; Otherwise sets it to 0.

    :param spinbox_var: Spinbox's variable.
    :param value: Value.
    """
    if value is not None:
        spinbox_var.set(value)
    else:
        spinbox_var.set(0)
