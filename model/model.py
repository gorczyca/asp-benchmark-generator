from model.hierarchy import Hierarchy


class Model:
    """Serves the communication between View and Controller.

    Gathers in one place all configuration's problem instance information.

    Attributes:
        hierarchy:    Hierarchy of components.
    """
    def __init__(self, hierarchy: Hierarchy = None):
        self.hierarchy: Hierarchy = hierarchy

    def clear(self):
        """Destroys all Model's attributes"""
        self.hierarchy = None

