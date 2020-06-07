BOOLEAN_TO_STRING_DICT = {
    True: 'yes',
    False: 'no',
    None: ''
}


class Component:
    def __init__(self, id_, name, level, parent_id=None, is_leaf=False, symmetry_breaking=None, count=None):
        self.id_ = id_
        self.name = name
        self.is_leaf = is_leaf
        self.level = level
        self.parent_id = parent_id
        self.count = count
        self.symmetry_breaking = symmetry_breaking

    def set_leaf(self):
        self.is_leaf = True

    def set_symmetry_breaking(self):
        self.symmetry_breaking = True

    @classmethod
    def from_json(cls, data):
        return cls(**data)

    def to_view_item(self):
        return ComponentTreeItem(self)

    # TODO: for development only
    def __str__(self):
        return self.name

    def __repr__(self):
        return self.name


class ComponentTreeItem(Component):
    def __init__(self, cmp):
        Component.__init__(self, cmp.id_, cmp.name, cmp.level, parent_id=cmp.parent_id, is_leaf=cmp.is_leaf,
                           symmetry_breaking=cmp.symmetry_breaking, count=cmp.count)

    def get_count(self):
        return self.count if self.count is not None else ''

    def get_symmetry_breaking(self):
        return BOOLEAN_TO_STRING_DICT[self.symmetry_breaking]





