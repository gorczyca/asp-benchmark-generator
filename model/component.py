import uuid
from typing import Optional

from model.association import Association


class Component:
    """Represents components in the component hierarchy.

    Attributes:
        id_:        Unique identifier
        name:      Unique name
        is_leaf:   True if component is a leaf component; False otherwise
        level:     Nesting level
        parent_id: Id of parent; None if component is a root
        count:     Number of instances of component; None if unspecified (has to be None for non-leaf components)
        symmetry_breaking:    Whether or not apply symmetry breaking (None for non-leaf components)
    """
    def __init__(self, name: str, level: int, id_: Optional[int] = None, parent_id: Optional[int] = None, is_leaf: bool = False,
                 symmetry_breaking: Optional[bool] = None, count: Optional[int] = None,
                 association: Optional[Association] = None):
        self.id_: int = id_ if id_ is not None else uuid.uuid4().int
        self.name: str = name
        self.is_leaf: bool = is_leaf
        self.level: int = level
        self.parent_id: Optional[int] = parent_id
        self.count: Optional[int] = count
        self.symmetry_breaking: Optional[bool] = symmetry_breaking
        self.association: Optional[Association] = association

    @classmethod
    def from_json(cls, data):
        """Necessary to create an instance from JSON"""
        # Convert dictionary to object
        association = None if data['association'] is None else Association.from_json(data['association'])
        data['association'] = association
        return cls(**data)

    def __repr__(self):
        """Provides object's string representation.

        For development purposes only.
        """
        return self.name






