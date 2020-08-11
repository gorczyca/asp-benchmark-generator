import os
import tkinter as tk
from typing import Optional, TextIO

STRING_MAX_LENGTH = 10
REST_SYMBOL = '...'

BOOLEAN_TO_STRING_DICT = {
    True: 'yes',
    False: 'no',
    None: ''
}

SELECT_PATH_STRING = '(Select output file path)'


def trim_string(string: str, length=STRING_MAX_LENGTH, rest_symbol=REST_SYMBOL) -> str:
    """Trims string to be maximally of 'length' length. The trimed-off part is replaced by 'rest_symbol'
    indicating that the string is not full

    :param string: string to trim
    :param length: maximal length of the string

    :returns trimmed string
    """
    if len(string) <= length:
        return string
    rest_symbol_length = len(rest_symbol)
    return f'{string[0:length-rest_symbol_length]}{rest_symbol}'


def change_controls_state(state=tk.NORMAL, *controls):
    for c in controls:
        c.config(state=state)


def get_target_file_location(file: Optional[TextIO], root_name: str, suffix: str = '', extension: str = '') -> str:
    if file is not None:
        dir_name = os.path.dirname(file.name)
        path = os.path.join(dir_name, f'{root_name}_{suffix}{extension}')
        return os.path.normpath(path)  # Normalize the back- & front-slashes
    else:
        return SELECT_PATH_STRING


