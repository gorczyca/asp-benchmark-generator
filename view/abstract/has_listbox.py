from abc import ABC, abstractmethod
from typing import Optional, List, Any, Tuple

from view.scrollbars_listbox import ScrollbarListbox
from view.tree_view_column import Column


class HasListbox(ABC):
    @abstractmethod
    def __init__(self):
        self._listbox: Optional[ScrollbarListbox] = None

    @abstractmethod
    def _on_select_listbox_item(self, id_: int) -> None: pass

    @property
    @abstractmethod
    def _listbox_columns(self) -> List[Column]: pass

    @abstractmethod
    def _extract_listbox_item_id(self, item: Any) -> int: pass

    @abstractmethod
    def _extract_listbox_item_text(self, item: Any) -> str: pass

    @abstractmethod
    def _extract_listbox_item_values(self, item: Any) -> Tuple[Any, ...]: pass

    @abstractmethod
    def _build_listbox(self) -> None: pass

    @abstractmethod
    def _destroy_listbox(self) -> None: pass
