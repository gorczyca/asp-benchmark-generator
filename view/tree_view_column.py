import tkinter as tk


MAIN_COLUMN_ID = '#0'


class Column:
    """Stores treeview's column information.

    Attributes:
        name: Column's name.
        main: Whether it is the treeview's main column (primary column).
        stretch: Whether to stretch.
        anchor: Anchoring direction.
    """
    def __init__(self,
                 name: str,
                 main: bool = False,
                 stretch: str = tk.NO,
                 anchor: str = tk.W):
        self.id_: str = MAIN_COLUMN_ID if main else name
        self.name: str = name
        self.stretch: str = stretch
        self.anchor: str = anchor
