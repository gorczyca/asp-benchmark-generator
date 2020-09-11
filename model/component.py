import uuid
from typing import Optional, Dict

from json_converter import deserialize_dict
from model import Association


class Component:
    """Represents components in the component hierarchy.

    Attributes:
        name: Name
        level: Nesting level
        id_: Unique identifier
        parent_id: Id of parent; None if component is a root
        is_leaf: True if component is a leaf component; False otherwise
        exact: Whether the number of component's instances is exact or bounded.
            None if unspecified (has to be None for non-leaf components).
        count: Exact number of instances of component (if exact is True).
            None if unspecified (has to be None for non-leaf components)
        min_count: Minimal number of instances (if exact is False).
            None if unspecified (has to be None for non-leaf components)
        max_count: Maximal number of instances (if exact is False).
            None if unspecified (has to be None for non-leaf components)
        symmetry_breaking: Whether or not apply symmetry breaking (None for non-leaf components)
        association: Expresses relationship (and its quantity) between the root component and this component.
        produces: Dictionary of type "id of resource": "Amount produced". Negative number in "Amount produced" value
            means that resource is consumed by component.
        ports: Dictionary of type "id of port": "Amount of ports the component has".
    """
    def __init__(self,
                 name: str,
                 level: int,
                 id_: Optional[int] = None,
                 parent_id: Optional[int] = None,
                 is_leaf: bool = False,
                 exact: Optional[bool] = None,
                 count: Optional[int] = None,
                 min_count: Optional[int] = None,
                 max_count: Optional[int] = None,
                 symmetry_breaking: Optional[bool] = None,
                 association: Optional[Association] = None,
                 produces: Dict[int, int] = None,
                 ports: Dict[int, int] = None):
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






