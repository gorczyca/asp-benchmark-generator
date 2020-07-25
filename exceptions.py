from abc import ABC, abstractmethod


class CustomException(Exception, ABC):
    @abstractmethod
    def __init__(self, message: str = 'An error occurred.'):
        Exception().__init__(message)
        self.message = message


class HierarchyStringError(CustomException):
    def __init__(self, message: str = 'Error while entering hierarchy.'):
        CustomException.__init__(self, message)


class ComponentError(CustomException):
    def __init__(self, message: str = 'Error while creating port.'):
        CustomException.__init__(self, message)


class ResourceError(CustomException):
    def __init__(self, message: str = 'Error while creating resource.'):
        CustomException.__init__(self, message)


class PortError(CustomException):
    def __init__(self, message: str = 'Error while creating port.'):
        CustomException.__init__(self, message)


class ConstraintError(CustomException):
    def __init__(self, message: str = 'Error while creating constraint.'):
        CustomException.__init__(self, message)




