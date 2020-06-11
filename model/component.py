import uuid
from typing import Optional


class Component:
    """Represents components in the component hierarchy.

    Attributes:
        __id        Unique identifier
        __name      Unique name
        __is_leaf   True if component is a leaf component; False otherwise
        __level     Nesting level
        __parent_id Id of parent; None if component is a root
        __count     Number of instances of component; None if unspecified (has to be None for non-leaf components)
        symmetry_breaking:    Whether or not apply symmetry breaking (None for non-leaf components)
    """
    def __init__(self, name: str, level: int, id_=None, parent_id: Optional[int] = None, is_leaf: bool = False,
                 symmetry_breaking: Optional[bool] = None, count: Optional[int] = None):
        self.id_: int = id_ if id_ is not None else uuid.uuid4().int
        self.name: str = name
        self.is_leaf: bool = is_leaf
        self.level: int = level
        self.parent_id: Optional[int] = parent_id
        self.count: Optional[int] = count
        self.symmetry_breaking: Optional[bool] = symmetry_breaking

    @classmethod
    def from_json(cls, data):
        """Necessary to create an instance from JSON"""
        return cls(**data)

    def __repr__(self):
        """Provides object's string representation.

        For development purposes only.
        """
        return self.name






