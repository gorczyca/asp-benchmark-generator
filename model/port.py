import uuid
from typing import Optional, List


class Port:
    """Represents a port used to connect two components.

    Attributes:
        id_:    Unique identifier
        name:   Unique name
        compatible_with:    List of port ids that this port is compatible with.
        force_connection:   Whether or not a port connection is required.
    """
    def __init__(self, name: str, id_: Optional[int] = None, compatible_with: List[int] = None,
                 force_connection: bool = False):
        self.id_: int = id_ if id_ is not None else uuid.uuid4().int
        self.name: str = name
        self.force_connection: bool = force_connection
        self.compatible_with = compatible_with if compatible_with is not None else []

    @classmethod
    def from_json(cls, data):
        """Necessary to create an instance from JSON"""
        return cls(**data)
