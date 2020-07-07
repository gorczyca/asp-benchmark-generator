# TODO: create a unified way of creation of exceptions


class HierarchyStringError(Exception):
    def __init__(self, message: str = 'Error while entering hierarchy.'):
        super().__init__(message)
        self.message = message


class ComponentError(Exception):
    def __init__(self, message: str = 'Error while creating port.'):
        super().__init__(message)
        self.message = message


class ResourceError(Exception):
    def __init__(self, message: str = 'Error while creating resource.'):
        super().__init__(message)
        self.message = message


class PortError(Exception):
    def __init__(self, message: str = 'Error while creating port.'):
        super().__init__(message)
        self.message = message

class ConstraintError(Exception):
    def __init__(self, message: str = 'Error while creating constraint.'):
        super().__init__(message)
        self.message = message
