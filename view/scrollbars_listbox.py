import tkinter as tk
from tkinter import ttk
from typing import List, Callable, Any, Optional

from view.abstract.has_common_setup import HasCommonSetup
from view.tree_view_column import Column

ANCESTOR = ''


# TODO: cleanup the arguments -- which suppose to be default, annotated etc.
class ScrollbarListbox(ttk.Treeview,
                       HasCommonSetup):
    def __init__(self, parent_frame, values: List[Any] = None, columns: List[Column] = None, on_select_callback=None,
                 extract_id: Callable[[Any], int] = None,
                 extract_text: Callable[[Any], str] = None,
                 extract_values: Callable[[Any], Any] = None,  # TODO: ???
                 grid_row=0, grid_column=0, **kwargs):
        ttk.Treeview.__init__(self, parent_frame, **kwargs)

        self.parent_frame = parent_frame    # TODO:  necessary?
        self.__grid_row = grid_row
        self.__grid_column = grid_column
        self.__extract_id = extract_id
        self.__extract_text = extract_text
        self.__extract_values = extract_values
        self.__on_select_callback = on_select_callback

        HasCommonSetup.__init__(self)

        if columns is not None:
            column_ids = [c.id_ for c in columns]
            self.__listbox['columns'] = column_ids
            for c in columns:
                self.__listbox.column(c.id_, stretch=c.stretch)
                self.__listbox.heading(c.id_, text=c.name, anchor=c.anchor)    # TODO: better

        if values is not None:
            for v in values:
                self.add_item(v)

    # HasCommonSetup
    def _create_widgets(self) -> None:
        # TODO: create new widget from this
        self.__listbox_frame = tk.Frame(self.parent_frame)
        self.__listbox_x_scrollbar = ttk.Scrollbar(self.__listbox_frame, orient=tk.HORIZONTAL)
        self.__listbox_y_scrollbar = ttk.Scrollbar(self.__listbox_frame, orient=tk.VERTICAL)
        self.__listbox = ttk.Treeview(self.__listbox_frame,
                                      xscrollcommand=self.__listbox_x_scrollbar.set,
                                      yscrollcommand=self.__listbox_y_scrollbar.set)
        self.__listbox_y_scrollbar.config(command=self.__listbox.yview)
        self.__listbox_x_scrollbar.config(command=self.__listbox.xview)

        if self.__on_select_callback:
            self.__listbox.bind('<ButtonRelease-1>', self.__item_selected)

    def _setup_layout(self) -> None:
        self.__listbox_frame.grid(row=self.__grid_row, column=self.__grid_column, sticky=tk.NSEW)
        self.__listbox_frame.rowconfigure(0, weight=1)
        self.__listbox_frame.columnconfigure(0, weight=1)

        # TODO: check if necessary
        self.__listbox.grid(row=0, column=0, sticky=tk.NSEW)
        self.__listbox_x_scrollbar.grid(row=1, column=0, sticky=tk.EW + tk.W)
        self.__listbox_y_scrollbar.grid(row=0, column=1, sticky=tk.NS + tk.E)

    def add_item(self, item: Any, index: Optional[int] = None) -> None:
        id_ = None if self.__extract_id is None else self.__extract_id(item)
        text = None if self.__extract_text is None else self.__extract_text(item)
        values = None if self.__extract_values is None else self.__extract_values(item)
        index = index if index is not None else tk.END
        self.__listbox.insert(ANCESTOR, index, iid=id_, text=text, values=values)

    def rename_item(self, item: Any, index: Optional[int] = None):
        id_ = self.__extract_id(item)
        text = self.__extract_text(item)
        self.__listbox.item(id_, text=text)
        if index is not None:
            self.__listbox.move(id_, ANCESTOR, index)

    def remove_item(self, item: Any):
        index = self.__extract_id(item)
        self.__listbox.delete(index)

    def __item_selected(self, _):
        if self.__on_select_callback:
            selected_item_id_str: str = self.__listbox.focus()
            if selected_item_id_str:
                self.__on_select_callback(int(selected_item_id_str))

