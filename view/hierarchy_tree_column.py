import tkinter as tk


class Column:
    def __init__(self, id, name, stretch=tk.NO, anchor=tk.W): # TODO: sprawdzić czy można jako *args / **kwargs przekazać minwidth / width
        self.id = id
        self.name = name
        self.stretch = stretch
        self.anchor = anchor
