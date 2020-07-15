import uuid
from typing import Optional, List


class SimpleConstraint:
    """

    """
    def __init__(self, id_: Optional[int] = None, components_ids: List[int] = None, min_: Optional[int] = None,
                 max_: Optional[int] = None, contains: bool = True, name: str = None, description: str = None,
                 distinct: bool = False):
        self.id_: int = id_ if id_ is not None else uuid.uuid4().int
        self.name: str = name
        self.description: str = description
        self.min_: Optional[int] = min_
        self.max_: Optional[int] = max_
        self.components_ids: List[int] = components_ids if components_ids is not None else []
        self.contains: bool = contains    # TODO: remove (should be unnecessary)
        self.distinct: bool = distinct

