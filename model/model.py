class Model:
    def __init__(self, hierarchy=None):
        self.__hierarchy = hierarchy

    def set_hierarchy(self, hierarchy):
        self.__hierarchy = hierarchy

    def get_hierarchy(self):
        return self.__hierarchy

    def clear(self):
        self.__hierarchy = None

    def remove_component_recursively(self, cmp):
        def __remove_component(cmp_, hierarchy_, to_remove_):
            to_remove_.append(cmp_)
            for c in hierarchy_:
                if c.parent_id == cmp_.id_:
                    __remove_component(c, hierarchy_, to_remove_)

        to_remove = []
        __remove_component(cmp, self.__hierarchy, to_remove)
        self.__hierarchy = [cmp for cmp in self.__hierarchy if cmp not in to_remove]
        return to_remove

    def remove_component_preserve_children(self, cmp):
        children = []
        for c in self.__hierarchy:
            if c.parent_id == cmp.id_:
                c.parent_id = cmp.parent_id
                children.append(c)
        self.__hierarchy.remove(cmp)
        return children

    def get_component_by_name(self, name):
        for cmp in self.__hierarchy:
            if cmp.name == name:
                return cmp




