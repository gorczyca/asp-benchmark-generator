from typing import Optional


class Association:
    """Represents associations - relationship (and its quantity) between the root component and other components.

    Attributes:
        min_: Minimal quantity of components
        max_: Maximal quantity of components
    """
    def __init__(self, min_: Optional[int] = None, max_: Optional[int] = None):
        self.min_ = min_
        self.max_ = max_

    @classmethod
    def from_json(cls, data):
        """Necessary to create an instance from JSON"""
        return cls(**data)
