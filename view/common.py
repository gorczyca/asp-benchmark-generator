import tkinter as tk

STRING_MAX_LENGTH = 10
REST_SYMBOL = '...'

BOOLEAN_TO_STRING_DICT = {
    True: 'yes',
    False: 'no',
    None: ''
}


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


