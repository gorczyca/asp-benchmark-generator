import tkinter as tk
from tkinter import ttk
from typing import List, Callable, Any, Optional

from view.tree_view_column import Column
from view.abstract import HasCommonSetup
from view.style import BACKGROUND_COLOR_SECONDARY, FONT_COLOR_SECONDARY, HOVER_COLOR

NO_ANCESTOR = ''
COL_ID_MAIN = '#0'

DEFAULT_HEADING = ''
SELECTED_TAG = 'select'
HOVER_TAG = 'hover'


class ScrollbarListbox(HasCommonSetup,
                       ttk.Frame):
    """Scrollable listbox / Treeview widget with optional scrollbars.

    Attributes:
        __selected_item_id: Currently selected item.
        __hovered_item_id: Currently hovered over item.
    """
    def __init__(self,
                 parent_frame,
                 values: Optional[List[Any]] = None,
                 columns: Optional[List[Column]] = None,
                 on_select_callback: Optional[Callable[[int], Any]] = None,
                 heading: str = DEFAULT_HEADING,
                 extract_id: Optional[Callable[[Any], int]] = None,
                 extract_text: Optional[Callable[[Any], str]] = None,
                 extract_values: Optional[Callable[[Any], Any]] = None,
                 extract_ancestor: Optional[Callable[[Any], Any]] = None,
                 has_scrollbars: bool = True,
                 enable_hover: bool = True):
        """Creates ScrollbarListbox widget.

        :param parent_frame: Parent frame.
        :param values: Initial values to show in the ScrollbarListbox.
        :param columns: Columns of ScrollbarListbox to present its items' properties.
        :param on_select_callback: Callback function executed whenever an item is selected (by a mouse click).
        :param heading: Title of the main column.
        :param extract_id: Function determining how to extract the item's id.
        :param extract_text: Function determining how to extract item's text for the main column.
        :param extract_values: Function determining how to extract item's values to present them in
            the ScrollbarListbox columns.
        :param extract_ancestor: Function determining how to extract item's ancestor
            - useful in case of tree structure.
        :param has_scrollbars: Whether to show the scrollbars.
        :param enable_hover: Whether to enable the hover option.
        """

        self.__extract_id: Callable[[Any], int] = extract_id
        self.__extract_text: Optional[Callable[[Any], str]] = extract_text
        self.__extract_values: Optional[Callable[[Any], Any]] = extract_values
        self.__extract_ancestor: Optional[Callable[[Any], Any]] = extract_ancestor if extract_ancestor is not None \
            else lambda x: NO_ANCESTOR
        self.__on_select_callback: Optional[Callable[[int], Any]] = on_select_callback
        self.__has_scrollbars: bool = has_scrollbars

        self.__selected_item_id: Optional[int] = None
        self.__hovered_item_id: Optional[int] = None

        ttk.Frame.__init__(self, parent_frame)
        HasCommonSetup.__init__(self)

        self.__configure(heading, enable_hover, columns, values)

    # HasCommonSetup
    def _create_widgets(self) -> None:
        self.__listbox = ttk.Treeview(self, selectmode=tk.BROWSE, style='Custom.Treeview')

        self.__listbox.tag_configure(SELECTED_TAG, background=BACKGROUND_COLOR_SECONDARY,
                                     foreground=FONT_COLOR_SECONDARY)

        if self.__has_scrollbars:
            self.__listbox_x_scrollbar = ttk.Scrollbar(self, orient=tk.HORIZONTAL)
            self.__listbox_y_scrollbar = ttk.Scrollbar(self, orient=tk.VERTICAL)
            self.__listbox.config(xscrollcommand=self.__listbox_x_scrollbar.set,
                                  yscrollcommand=self.__listbox_y_scrollbar.set)
            self.__listbox_y_scrollbar.config(command=self.__listbox.yview)
            self.__listbox_x_scrollbar.config(command=self.__listbox.xview)

        if self.__on_select_callback:
            self.__listbox.bind('<ButtonRelease-1>', self.__item_selected)

    def _setup_layout(self) -> None:
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)

        self.__listbox.grid(row=0, column=0, sticky=tk.NSEW)
        if self.__has_scrollbars:
            self.__listbox_x_scrollbar.grid(row=1, column=0, sticky=tk.EW + tk.S)
            self.__listbox_y_scrollbar.grid(row=0, column=1, sticky=tk.NS + tk.E)

    def __configure(self, heading: str, enable_hover: bool, columns: List[Column], values: List[Any]) -> None:
        """Configures ScrollbarListbox options.

        :param heading: Title of the main column.
        :param values: Initial values to show in the ScrollbarListbox.
        :param columns: Columns of ScrollbarListbox to present its items' properties.
        :param enable_hover: Whether to enable the hover option.
        """
        self.__listbox.column(COL_ID_MAIN, stretch=tk.YES)
        self.__listbox.heading(COL_ID_MAIN, text=heading, anchor=tk.W)

        if enable_hover:
            self.__listbox.tag_configure(HOVER_TAG, background=HOVER_COLOR)
            self.__listbox.bind('<Motion>', self.__hover)

        if columns is not None:
            column_ids = [c.id_ for c in columns]
            self.__listbox['columns'] = column_ids
            for c in columns:
                self.__listbox.column(c.id_, stretch=c.stretch)
                self.__listbox.heading(c.id_, text=c.name, anchor=c.anchor)

        if values is not None:
            self.set_items(values)

    def set_items(self, items: List[Any]) -> None:
        """Fills the ScrollbarListbox with items.

        :param items: List of items to fill the ScrollbarListbox.
        """
        self.__listbox.delete(*self.__listbox.get_children())   # Clear current items
        for i in items:
            self.add_item(i, select_item=False)

    def add_item(self, item: Any, index: Optional[int] = None, expand=True, select_item=True) -> None:
        """Adds new item to ScrollbarListbox.

        :param item: Item to add.
        :param index: Item's index in ScrollbarListbox.
        :param expand: Whether to open the item's branch (and its parent's).
        :param select_item: Whether to highlight added item as selected.
        """
        id_ = None if self.__extract_id is None else self.__extract_id(item)
        text = '' if self.__extract_text is None else self.__extract_text(item)
        values = () if self.__extract_values is None else self.__extract_values(item)
        index = index if index is not None else tk.END
        ancestor = self.__extract_ancestor(item)
        self.__listbox.insert(ancestor, index, iid=id_, text=text, values=values)
        if expand:
            self.__listbox.item(id_, open=True)
            if ancestor:
                self.__listbox.item(ancestor, open=True)
        if select_item:
            self.select_item(item)

    def rename_item(self, item: Any, index: Optional[int] = None) -> None:
        """Updates item's text (name) in the ScrollbarListbox.

        :param item: Item to update.
        :param index: Index in the ScrollbarListbox (useful in case of listview)
        """
        id_ = self.__extract_id(item)
        text = self.__extract_text(item)
        self.__listbox.item(id_, text=text)
        if index is not None:
            ancestor = self.__extract_ancestor(item)
            self.__listbox.move(id_, ancestor, index)

    def remove_item_recursively(self, item: Any) -> None:
        """Removes item and all its children recursively.

        :param item: Item to remove.
        """
        id_ = self.__extract_id(item)
        self.__listbox.delete(id_)

    def remove_item_preserve_children(self, item: Any) -> None:
        """Removes item but preserves all its children by changing their parent_id to the parent id of the removed item.

        :param item: Item to remove.
        """
        ancestor = self.__extract_ancestor(item)
        id_ = self.__extract_id(item)
        children = self.__listbox.get_children(id_)
        for i, child in enumerate(children):
            self.__listbox.move(child, ancestor, i)
        self.__listbox.delete(id_)

    def select_item(self, item: Any) -> None:
        """Highlights item in the ScrollbarListbox as selected.

        :param item: Item to highlight.
        """
        id_ = self.__extract_id(item)
        if self.__selected_item_id is not None and self.__listbox.exists(self.__selected_item_id):
            tags_ = self.__listbox.item(self.__selected_item_id)['tags']
            if SELECTED_TAG in tags_:
                tags_.remove(SELECTED_TAG)
                self.__listbox.item(self.__selected_item_id, tags=tags_)    # Remove highlight
        self.__selected_item_id = id_
        self.__listbox.item(id_, tags=[SELECTED_TAG])

    def __hover(self, event) -> None:
        """Executed whenever mouse cursor hovers over ScrollbarListbox and enable_hover option is set to True.

        :param event:
        """
        identified_row_string = self.__listbox.identify_row(event.y)
        if identified_row_string == '':
            self.__remove_tag(HOVER_TAG, self.__hovered_item_id)
            self.__hovered_item_id = None
        else:
            id_ = int(identified_row_string)
            if id_ != self.__hovered_item_id:   # The hover changed
                self.__remove_tag(HOVER_TAG, self.__hovered_item_id)
                if id_ != self.__selected_item_id:
                    self.__add_tag(HOVER_TAG, id_)
                    self.__hovered_item_id = id_

    def __remove_tag(self, tag: str, item_id: int) -> None:
        """Removes tag from item.

        :param tag: Tag to remove.
        :param item_id: Id of an item to remove the tag from.
        """
        if item_id is not None and self.__listbox.exists(item_id):
            tags = self.__listbox.item(item_id)['tags']
            if tag in tags:
                tags.remove(HOVER_TAG)
            self.__listbox.item(item_id, tags=tags)

    def __add_tag(self, tag, item_id, remove_others: bool = False) -> None:
        """Adds tag to item.

        :param tag: Tag to add to item.
        :param item_id: Id of the item to add the tag to.
        :param remove_others: Whether to remove all other tags from the item.
        """
        tags = []
        if remove_others:
            tags.append(tag)
        else:
            tags = self.__listbox.item(item_id)['tags']
            if not tags:
                tags = []
            if tag not in tags:
                tags.append(tag)
        self.__listbox.item(item_id, tags=tags)

    def __item_selected(self, _) -> None:
        """Executed whenever a ScrollbarListbox's item is selected (by a mouse click).

        Highlights the selected item as selected and executes the __on_select_callback on it.
        """
        if self.__selected_item_id is not None and self.__listbox.exists(self.__selected_item_id):
            self.__listbox.item(self.__selected_item_id, tags=[])    # Remove highlight
        selected_item_id_str = self.__listbox.focus()
        if selected_item_id_str:
            selected_item_id = int(selected_item_id_str)
            self.__listbox.item(selected_item_id, tags=[SELECTED_TAG])
            self.__selected_item_id = selected_item_id
            if self.__on_select_callback:
                self.__on_select_callback(selected_item_id)

    def update_values(self, *items) -> None:
        """Updates given items' values in the ScrollbarListbox.

        :param items: Items to update.
        """
        for i in items:
            values = self.__extract_values(i)
            id_ = self.__extract_id(i)
            self.__listbox.item(id_, values=values)
