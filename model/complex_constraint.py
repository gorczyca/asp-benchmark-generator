import uuid
from typing import Optional, List

from model.simple_constraint import SimpleConstraint


class ComplexConstraint:
    """

    """
    def __init__(self, id_: Optional[int] = None, name: str = None, description: str = None,
                 antecedent: List[SimpleConstraint] = None, consequent: List[SimpleConstraint] = None,
                 antecedent_all: bool = True, consequent_all: bool = True):
        self.id_: int = id_ if id_ is not None else uuid.uuid4().int
        self.name: str = name
        self.description: str = description
        self.antecedent: List[SimpleConstraint] = antecedent if antecedent is not None else []
        self.antecedent_all: bool = antecedent_all
        self.consequent: List[SimpleConstraint] = consequent if consequent is not None else []
        self.consequent_all: bool = consequent_all

