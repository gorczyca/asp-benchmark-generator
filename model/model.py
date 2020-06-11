from model.hierarchy import Hierarchy


class Model:
    """Serves the communication between View and Controller.

    Gathers in one place all configuration's problem instance information.

    Attributes:
        __hierarchy:    Hierarchy of components.
    """
    def __init__(self, hierarchy: Hierarchy = None):
        self.__hierarchy: Hierarchy = hierarchy

    @property
    def hierarchy(self): return self.__hierarchy

    @hierarchy.setter
    def hierarchy(self, value): self.__hierarchy = value

    def clear(self):
        """Destroys all Model's attributes"""
        self.__hierarchy = None

