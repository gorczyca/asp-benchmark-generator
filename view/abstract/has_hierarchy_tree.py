from abc import ABC, abstractmethod
from typing import Optional, List, Any, Tuple

from model.component import Component
from view.hierarchy_tree import HierarchyTree
from view.tree_view_column import Column


# TODO: consider if that makes sense
class HasHierarchyTree(ABC):
    @abstractmethod
    def __init__(self):
        self._hierarchy_tree: Optional[HierarchyTree] = None
        self._selected_component: Optional[Component] = None

    @abstractmethod
    def _on_select_tree_item(self, cmp_id: int) -> None: pass

    @property
    @abstractmethod
    def _columns(self) -> List[Column]: pass

    @abstractmethod
    def _extract_values(self, cmp: Component) -> Tuple[Any, ...]: pass

    @abstractmethod
    def _build_tree(self) -> None: pass

    @abstractmethod
    def _destroy_tree(self) -> None: pass
