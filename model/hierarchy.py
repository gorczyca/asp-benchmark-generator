from typing import List, Optional

from exceptions import HierarchyStringError
from model import Component


class Hierarchy:
    """Hierarchy representation.

    Hierarchy of components is naturally a tree structure. Because of complexity issues (to avoid recursion) it
    is implemented as a List with component having a pointer to its ancestor. Still, recursion could not be completely
    avoided (e.g. when removing a component recursively or creating a string from hierarchy)

    Attributes:
        __hierarchy_list: Actual list of components representing the hierarchy tree.
    """
    def __init__(self, hierarchy_list: List[Component]):
        self.__hierarchy_list = hierarchy_list
        self.__set_leaves()

    @property
    def hierarchy_list(self): return self.__hierarchy_list

    def __set_leaves(self) -> None:
        """Traverses through hierarchy and sets the property is_leaf of leaf components to True.

        Used when hierarchy is changed.
        """
        parents_ids = [cmp.parent_id for cmp in self.__hierarchy_list if cmp.parent_id is not None]
        parents_ids = set(parents_ids)

        for cmp in self.__hierarchy_list:
            if cmp.id not in parents_ids:
                cmp.is_leaf = True
                cmp.symmetry_breaking = True

    def add(self, cmp_name: str, level: int, parent_id: Optional[int], is_leaf: bool) -> Component:
        """Creates and adds new component to hierarchy.

        :param cmp_name: Name.
        :param level: Level.
        :param parent_id: Id of parent.
        :param is_leaf: True if component is a leaf-component; False otherwise.
        :returns: Created component
        """
        symmetry_breaking = True if is_leaf else None
        cmp = Component(cmp_name, level, parent_id=parent_id, is_leaf=is_leaf,
                        symmetry_breaking=symmetry_breaking)
        self.__hierarchy_list.append(cmp)
        if parent_id:
            parent = self.get_component_by_id(parent_id)
            parent.is_leaf = False      # Parent is not leaf anymore
            parent.count = None
            parent.symmetry_breaking = None
        return cmp

    def remove_component_recursively(self, cmp: Component) -> List[Component]:
        """Removes the component recursively (the component itself, its children, the children of the children...).

        :param cmp: Component to remove.
        :returns: List of components removed from the hierarchy.
        """
        def __remove_component(cmp_: Component, hierarchy_: List[Component], to_remove_: List[Component]) -> None:
            """Creates a list of components to remove by recursive calls to itself.

            :param cmp_: Current component to remove (and all its children recursively).
            :param hierarchy_: Components hierarchy.
            :param to_remove_: List of components to be removed.
            """
            to_remove_.append(cmp_)     # Add current element to list of elements to remove.
            for c in hierarchy_:
                if c.parent_id == cmp_.id:
                    __remove_component(c, hierarchy_, to_remove_)   # Recursively remove all the component's children

        to_remove = []
        __remove_component(cmp, self.__hierarchy_list, to_remove)
        self.__hierarchy_list = [cmp for cmp in self.__hierarchy_list if cmp not in to_remove]
        self.__set_leaves()
        return to_remove

    def remove_component_preserve_children(self, cmp: Component) -> List[Component]:
        """Removes the component from hierarchy, but preserves its children.

        The children of the removed component are placed on their ancestor's place; Their parent_id attribute is set
        to their actual parent's parent_id attribute.

        :param cmp: Component to remove.
        :returns: List of removed components children.
        """
        children = []
        for c in self.__hierarchy_list:
            if c.parent_id == cmp.id:
                c.parent_id = cmp.parent_id
                children.append(c)
        self.__hierarchy_list.remove(cmp)
        self.__set_leaves()
        return children

    def get_component_by_id(self, id_: int) -> Component:
        """Returns component, that has the specify id

        :param id_: Id of the parameter to return
        :returns: Component with the given id.
        """
        return next((cmp for cmp in self.__hierarchy_list if cmp.id == id_), None)

    def change_components_name(self, cmp: Component, new_name: str) -> Component:
        """Changes name for a specified component.

        Raises HierarchyStringError when a component with the new name already exists in the hierarchy.
        :param cmp: Component
        :param new_name: New name for component
        :returns: Component with its name changed
        """
        cmps_names = [c.name for c in self.__hierarchy_list]
        if new_name in cmps_names:
            raise HierarchyStringError(message=f'Component with name: "{new_name}" already exists in the hierarchy.')
        cmp.name = new_name
        return cmp

    def set_symmetry_breaking_for_all(self, symmetry_breaking) -> List[Component]:
        """Sets the value of symmetry breaking for all element in the hierarchy.

        :param symmetry_breaking: Value to set the symmetry breaking to.
        """
        edited_cmps = []
        for c in self.__hierarchy_list:
            if c.is_leaf:
                c.symmetry_breaking = symmetry_breaking
                edited_cmps.append(c)
        return edited_cmps

    @classmethod
    def from_json(cls, data):
        """Necessary to create an instance from JSON."""
        hierarchy = list(map(Component.from_json, data['hierarchy_list']))
        return cls(hierarchy)
