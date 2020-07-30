import tkinter as tk


class Column:
    def __init__(self, id_, name, stretch=tk.NO, anchor=tk.W):
        self.id_ = id_
        self.name = name
        self.stretch = stretch
        self.anchor = anchor
