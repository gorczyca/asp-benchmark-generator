class Component:
    def __init__(self, name, level, is_leaf=False, children=None):
        self.name = name
        self.is_leaf = is_leaf
        self.level = level
        self.children = children if children is not None else []

    def set_leaf(self):
        self.is_leaf = True


