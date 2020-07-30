import tkinter as tk
from tkinter import ttk
from typing import List, Callable, Any, Optional

from view.abstract.has_common_setup import HasCommonSetup
from view.tree_view_column import Column

NO_ANCESTOR = ''
COL_ID_MAIN = '#0'

DEFAULT_HEADING = 'HEADING'




# TODO: cleanup the arguments -- which suppose to be default, annotated etc.
class ScrollbarListbox(ttk.Treeview,
                       HasCommonSetup):
    def __init__(self, parent_frame,
                 values: List[Any] = None,
                 columns: List[Column] = None,
                 on_select_callback = None,
                 heading: str = DEFAULT_HEADING,
                 extract_id: Callable[[Any], int] = None,
                 extract_text: Callable[[Any], str] = None,
                 extract_values: Callable[[Any], Any] = None,
                 extract_ancestor: Callable[[Any], Any] = None,
                 **kwargs):

        ttk.Treeview.__init__(self, parent_frame, **kwargs) # TODO: necessary

        self.parent_frame = parent_frame    # TODO:  necessary?
        self.__extract_id = extract_id
        self.__extract_text = extract_text
        self.__extract_values = extract_values
        self.__extract_ancestor = extract_ancestor if extract_ancestor is not None else lambda x: NO_ANCESTOR
        self.__on_select_callback = on_select_callback

        HasCommonSetup.__init__(self)

        self.__listbox.column(COL_ID_MAIN, stretch=tk.YES)  # TODO: find values for width, minwidth
        self.__listbox.heading(COL_ID_MAIN, text=heading, anchor=tk.W)

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
        self.__listbox_frame = ttk.Frame(self.parent_frame)
        self.__listbox_x_scrollbar = ttk.Scrollbar(self.__listbox_frame, orient=tk.HORIZONTAL)
        self.__listbox_y_scrollbar = ttk.Scrollbar(self.__listbox_frame, orient=tk.VERTICAL)
        self.__listbox = ttk.Treeview(self.__listbox_frame, selectmode=tk.BROWSE, style='Custom.Treeview',
                                      xscrollcommand=self.__listbox_x_scrollbar.set,
                                      yscrollcommand=self.__listbox_y_scrollbar.set)
        self.__listbox_y_scrollbar.config(command=self.__listbox.yview)
        self.__listbox_x_scrollbar.config(command=self.__listbox.xview)

        if self.__on_select_callback:
            self.__listbox.bind('<ButtonRelease-1>', self.__item_selected)

    def _setup_layout(self) -> None:
        # TODO:
        # self.__listbox_frame.grid(row=self.__grid_row, column=self.__grid_column, sticky=tk.NSEW,
        #                          columnspan=self.__column_span)
        self.__listbox_frame.rowconfigure(0, weight=1)
        self.__listbox_frame.columnconfigure(0, weight=1)

        # TODO: check if necessary
        self.__listbox.grid(row=0, column=0, sticky=tk.NSEW)
        self.__listbox_x_scrollbar.grid(row=1, column=0, sticky=tk.EW + tk.W)
        self.__listbox_y_scrollbar.grid(row=0, column=1, sticky=tk.NS + tk.E)

    def set_items(self, items: Any):
        self.__listbox.delete(*self.__listbox.get_children())   # Clear current items
        for i in items:
            self.add_item(i)

    def add_item(self, item: Any, index: Optional[int] = None, expand=True) -> None:
        id_ = None if self.__extract_id is None else self.__extract_id(item)
        text = '' if self.__extract_text is None else self.__extract_text(item)
        values = () if self.__extract_values is None else self.__extract_values(item)
        index = index if index is not None else tk.END
        ancestor = self.__extract_ancestor(item)    # TODO: make all like this
        self.__listbox.insert(ancestor, index, iid=id_, text=text, values=values)
        if expand:
            self.__listbox.item(id_, open=True)

    def rename_item(self, item: Any, index: Optional[int] = None):
        id_ = self.__extract_id(item)
        text = self.__extract_text(item)
        self.__listbox.item(id_, text=text)
        if index is not None:
            ancestor = self.__extract_ancestor(item)
            self.__listbox.move(id_, ancestor, index)

    def remove_item_recursively(self, item: Any):
        id_ = self.__extract_id(item)
        self.__listbox.delete(id_)

    def remove_item_preserve_children(self, item: Any):
        # TODO: requires testing
        ancestor = self.__extract_ancestor(item)
        id_ = self.__extract_id(item)
        children = self.__listbox.get_children(id_)
        for i, child in enumerate(children):
            self.__listbox.move(child, ancestor, i)
        self.__listbox.delete(id_)

    # TODO: update values

    def select_item(self, item: Any):
        # TODO: it does not work MAKE IT WORK!
        id_ = self.__extract_id(item)
        self.__listbox.focus(str(id_))
        self.__listbox.selection_set(str(id_))

    def __item_selected(self, _):
        if self.__on_select_callback:
            selected_item_id_str: str = self.__listbox.focus()
            if selected_item_id_str:
                self.__on_select_callback(int(selected_item_id_str))

    def update_values(self, *items):
        for i in items:
            values = self.__extract_values(i)
            id_ = self.__extract_id(i)
            self.__listbox.item(id_, values=values)

    # TODO: test these both methods
    def grid_forget(self):
        # self.grid_forget()  # TODO?
        self.__listbox_frame.grid_forget()

    def grid(self, **kwargs):
        self.__listbox_frame.grid(**kwargs)




