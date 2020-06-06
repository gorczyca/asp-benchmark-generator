class Component:
    def __init__(self, id_, name, level, parent_id=None, is_leaf=False, symmetry_breaking=None, count=None):
        self.id_ = id_
        self.name = name
        self.is_leaf = is_leaf
        self.level = level
        self.parent_id = parent_id
        self.count = count
        self.symmetry_breaking = symmetry_breaking

        # the names have to match column names in tree view

    def set_leaf(self):
        self.is_leaf = True

    # TODO: rename
    def get_by_name(self, name):
        return self.__getattribute__(name)

    @classmethod
    def from_json(cls, data):
        return cls(**data)

    # TODO: for development only
    def __str__(self):
        return self.name

    def __repr__(self):
        return self.name





