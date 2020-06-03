class Component:
    def __init__(self, name, level, symmetry_breaking=None, count=None, is_leaf=False, children=None):
        self.name = name
        self.is_leaf = is_leaf
        self.level = level
        self.children = children if children is not None else []
        self.count = count
        self.symmetry_breaking = symmetry_breaking

        # the names have to match column names in tree view

    def set_leaf(self):
        self.is_leaf = True

    def get_by_name(self, name):
        return self.__getattribute__(name)

    # TODO: for development only
    def __str__(self):
        return self.name

    def __repr__(self):
        return self.name





