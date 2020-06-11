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
        __symmetry_breaking:    Whether or not apply symmetry breaking (None for non-leaf components)
    """
    def __init__(self, name: str, level: int, parent_id: Optional[int] = None, is_leaf: bool = False,
                 symmetry_breaking: Optional[bool] = None, count: Optional[int] = None):
        self.__id: int = uuid.uuid4().int
        self.__name: str = name
        self.__is_leaf: bool = is_leaf
        self.__level: int = level
        self.__parent_id: Optional[int] = parent_id
        self.__count: Optional[int] = count
        self.__symmetry_breaking: Optional[bool] = symmetry_breaking

    @property
    def id(self): return self.__id

    @property
    def name(self): return self.__name

    @name.setter
    def name(self, value): self.__name = value

    @property
    def level(self): return self.__level

    @property
    def count(self): return self.__count

    @count.setter
    def count(self, value): self.__count = value

    @property
    def parent_id(self): return self.__parent_id

    @parent_id.setter
    def parent_id(self, value): self.__parent_id = value

    @property
    def is_leaf(self): return self.__is_leaf

    @is_leaf.setter
    def is_leaf(self, value): self.__is_leaf = value

    @property
    def symmetry_breaking(self): return self.__symmetry_breaking

    @symmetry_breaking.setter
    def symmetry_breaking(self, value): self.__symmetry_breaking = value

    @classmethod
    def from_json(cls, data):
        """Necessary to create an instance from JSON"""
        return cls(**data)

    def __repr__(self):
        """Provides object's string representation.

        For development purposes only.
        """
        return self.__name






