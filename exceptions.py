"""Custom error."""


class BGError(Exception):
    def __init__(self, message: str = 'An error occurred.'):
        Exception().__init__(message)
        self.message = message



