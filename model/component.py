import uuid
from typing import Optional, Dict

from json_converter import deserialize_dict
from model import Association


class Component:
    """Represents components in the component hierarchy.

    Attributes:
        id_:       Unique identifier
        name:      Unique name
        is_leaf:   True if component is a leaf component; False otherwise
        level:     Nesting level
        parent_id: Id of parent; None if component is a root
        count:     Number of instances of component; None if unspecified (has to be None for non-leaf components)
        symmetry_breaking:    Whether or not apply symmetry breaking (None for non-leaf components)
        produces:   Dictionary of type "id of resource": "Amount produced". Negative number in "Amount produced" value
            means that resource is consumed by component.
        ports: Dictionary of type "id of port": "Amount of ports the component has".
    """
    def __init__(self, name: str, level: int, id_: Optional[int] = None, parent_id: Optional[int] = None,
                 is_leaf: bool = False, symmetry_breaking: Optional[bool] = None, count: Optional[int] = None,
                 min_count: Optional[int] = None, max_count: Optional[int] = None, max_: Optional[int] = None,
                 exact: Optional[bool] = None, association: Optional[Association] = None,
                 produces: Dict[int, int] = None, ports: Dict[int, int] = None):
        self.id_: int = id_ if id_ is not None else uuid.uuid4().int
        self.name: str = name
        self.is_leaf: bool = is_leaf
        self.level: int = level
        self.parent_id: Optional[int] = parent_id
        self.exact: Optional[bool] = exact
        self.count: Optional[int] = count
        self.min_count: Optional[int] = min_count
        self.max_count: Optional[int] = max_count
        self.symmetry_breaking: Optional[bool] = symmetry_breaking
        self.association: Optional[Association] = association
        self.produces: Dict[int, int] = produces if produces is not None else {}
        self.ports: Dict[int, int] = ports if ports is not None else {}

    @classmethod
    def from_json(cls, data):
        """Necessary to create an instance from JSON"""
        data['association'] = Association.from_json(data['association'])
        data['produces'] = deserialize_dict(data['produces'])
        data['ports'] = deserialize_dict(data['ports'])
        return cls(**data)

    def __repr__(self):
        """Provides object's string representation. For development purposes only."""
        return self.name






