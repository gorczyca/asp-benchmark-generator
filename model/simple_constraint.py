import uuid
from typing import Optional, List


class SimpleConstraint:
    """Represents a simple constraint.

    Attributes:
        id_: Unique identifier.
        name: Name
        description: Constraint's description.
        min_: Minimal amount of component's (from components_ids) a valid configuration must contain.
        max_: Maximal amount of component's (from components_ids) a valid configuration must contain.
        components_ids: Ids of components that this constraint enforces.
        distinct: If set to True, components of the same type are counted only once;
            otherwise every appearance is counted.
    """
    def __init__(self,
                 id_: Optional[int] = None,
                 name: str = None,
                 description: str = None,
                 min_: Optional[int] = None,
                 max_: Optional[int] = None,
                 components_ids: List[int] = None,
                 distinct: bool = False):
        self.id_: int = id_ if id_ is not None else uuid.uuid4().int
        self.name: str = name
        self.description: str = description
        self.min_: Optional[int] = min_
        self.max_: Optional[int] = max_
        self.components_ids: List[int] = components_ids if components_ids is not None else []
        self.distinct: bool = distinct

    @classmethod
    def from_json(cls, data):
        """Necessary to create an instance from JSON"""
        return cls(**data)

