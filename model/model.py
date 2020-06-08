from view.vertical_notebook.create_hierarchy_window import CreateHierarchyWindow # TODO: to tak nie może byc
from model.component import Component

class Model:
    def __init__(self, hierarchy=None):
        self.__hierarchy = hierarchy

    def set_hierarchy(self, hierarchy):
        self.__hierarchy = hierarchy

    def get_hierarchy(self):
        return self.__hierarchy

    def clear(self):
        self.__hierarchy = None

    # TODO: rozwiązać problem UUID
    def add_to_hierarchy(self, cmp_name, level, parent_id, is_leaf):
        ids = [cmp.id_ for cmp in self.__hierarchy]
        max_id = max(ids)
        next_id = max_id + 1
        symmetry_breaking = True if is_leaf else None
        cmp = Component(next_id, cmp_name, level, parent_id=parent_id, is_leaf=is_leaf,
                        symmetry_breaking=symmetry_breaking)
        self.__hierarchy.append(cmp)
        return cmp

    def remove_component_recursively(self, cmp):
        def __remove_component(cmp_, hierarchy_, to_remove_):
            to_remove_.append(cmp_)
            for c in hierarchy_:
                if c.parent_id == cmp_.id_:
                    __remove_component(c, hierarchy_, to_remove_)

        to_remove = []
        __remove_component(cmp, self.__hierarchy, to_remove)
        self.__hierarchy = [cmp for cmp in self.__hierarchy if cmp not in to_remove]
        # TODO: DO NOT IMPORT IT FROM THE VIEW CLASS
        CreateHierarchyWindow.set_leaves(self.__hierarchy)
        return to_remove

    def remove_component_preserve_children(self, cmp):
        children = []
        for c in self.__hierarchy:
            if c.parent_id == cmp.id_:
                c.parent_id = cmp.parent_id
                children.append(c)
        self.__hierarchy.remove(cmp)
        CreateHierarchyWindow.set_leaves(self.__hierarchy)
        return children

    def get_component_by_name(self, name):
        for cmp in self.__hierarchy:
            if cmp.name == name:
                return cmp






