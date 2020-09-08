import tkinter as tk


MAIN_COLUMN_ID = '#0'


class Column:
    def __init__(self, name, main=False, stretch=tk.NO, anchor=tk.W):
        self.id_ = MAIN_COLUMN_ID if main else name
        self.name = name
        self.stretch = stretch
        self.anchor = anchor
