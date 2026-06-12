class DomainError(Exception):
    pass


class ModelNotFoundError(DomainError):
    pass


class DuplicateModelVersionError(DomainError):
    pass


class InvalidModelVersionError(DomainError):
    pass


class InvalidModelFileError(DomainError):
    pass


class ModelFileMissingError(DomainError):
    pass


class ModelConversionError(DomainError):
    pass
