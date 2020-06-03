class Model:
    def __init__(self, hierarchy=None):
        self.__hierarchy = hierarchy

    def set_hierarchy(self, hierarchy):
        self.__hierarchy = hierarchy

    def get_hierarchy(self):
        return self.__hierarchy

    def get_component_by_name(self, name):
        def __get_component_by_name(__name, __hierarchy):
            for cmp in __hierarchy:
                if cmp.name == __name:
                    return cmp
                else:
                    cmp = __get_component_by_name(__name, cmp.children)
                    if cmp:
                        return cmp

        return __get_component_by_name(name, self.__hierarchy)




