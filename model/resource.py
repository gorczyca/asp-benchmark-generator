import uuid


class Resource:
    """Represents a resource.

    Attributes:
        id_: Unique identifier
        name: Name
    """
    def __init__(self,
                 name: str,
                 id_: int = None):
        self.id_ = id_ if id_ is not None else uuid.uuid4().int
        self.name = name

    @classmethod
    def from_json(cls, data):
        """Necessary to create an instance from JSON"""
        return cls(**data)

