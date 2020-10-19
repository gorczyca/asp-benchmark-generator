import uuid
from typing import Optional, List

from misc.json_converter import deserialize_list
from model import SimpleConstraint


class ComplexConstraint:
    """Represents complex constraint, expressed in a following form:
        if ANTECEDENT holds, then CONSEQUENT must hold.

    Attributes:
        id_: Unique identifier.
        name: Name of the constraint.
        description: Constraint's description.
        antecedent: List of SimpleConstraints expressing Antecedent (conditions).
        consequent: List of SimpleConstraint expressing Consequent.
        antecedent_all: If True, then every element of antecedent must hold, so that it's satisfied;
            otherwise it's enough if only one of them holds.
        consequent_all: If True, then the all elements of consequent must evaluate to true at the same time;
            otherwise some of them must.
    """
    def __init__(self,
                 id_: Optional[int] = None,
                 name: str = None,
                 description: str = None,
                 antecedent: List[SimpleConstraint] = None,
                 consequent: List[SimpleConstraint] = None,
                 antecedent_all: bool = True,
                 consequent_all: bool = True):
        self.id_: int = id_ if id_ is not None else uuid.uuid4().int
        self.name: str = name
        self.description: str = description
        self.antecedent: List[SimpleConstraint] = antecedent if antecedent is not None else []
        self.antecedent_all: bool = antecedent_all
        self.consequent: List[SimpleConstraint] = consequent if consequent is not None else []
        self.consequent_all: bool = consequent_all

    @classmethod
    def from_json(cls, data):
        """Necessary to create an instance from JSON"""
        data['antecedent'] = deserialize_list(SimpleConstraint, data['antecedent'])
        data['consequent'] = deserialize_list(SimpleConstraint, data['consequent'])
        return cls(**data)

