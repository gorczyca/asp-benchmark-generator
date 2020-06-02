class Model:
    def __init__(self, hierarchy=None):
        self.__hierarchy = hierarchy

    def set_hierarchy(self, hierarchy):
        self.__hierarchy = hierarchy

    def get_hierarchy(self):
        return self.__hierarchy

