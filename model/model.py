class Model:
    def __init__(self, hierarchy=None):
        self.__hierarchy = hierarchy

    def set_hierarchy(self, hierarchy):
        self.__hierarchy = hierarchy

    def get_hierarchy(self):
        return self.__hierarchy

    def get_component_by_name(self, name):
        for cmp in self.__hierarchy:
            if cmp.name == name:
                return cmp




