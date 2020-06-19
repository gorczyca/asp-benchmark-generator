# TODO: improve


class HierarchyStringError(Exception):
    def __init__(self, message: str = 'Error while entering hierarchy.'):
        super().__init__(message)
        self.message = message


class ResourceStringError(Exception):
    def __init__(self, message: str = 'Error while creating resource.'):
        super().__init__(message)
        self.message = message
