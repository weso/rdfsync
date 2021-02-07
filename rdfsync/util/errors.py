class StringValidationError(Exception):
    def __init__(self, message):
        super().__init__(message)


class FormatValidationError(Exception):
    def __init__(self, message):
        super().__init__(message)
