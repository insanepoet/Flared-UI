from FlaredUI.Modules.Errors.GeneralErrors import CustomFlaskError


class ContainerError(CustomFlaskError):
    """Base class for errors related to containers."""
    pass


class ContainerNotFoundOnServerError(ContainerError):
    """Raised when a container is not found on the specified server."""

    def __init__(self, message="Container not found on server.", status_code=404, payload=None):
        super().__init__(message, status_code, payload)


class ContainerNotFoundInDatabaseError(ContainerError):
    """Raised when a container is not found in the database."""

    def __init__(self, message="Container not found in database.", status_code=404, payload=None):
        super().__init__(message, status_code, payload)


class ContainerRetrievalError(ContainerError):
    """Raised for general errors during container retrieval."""

    def __init__(self, message="Error retrieving container.", status_code=500, payload=None):
        super().__init__(message, status_code, payload)


class ContainerUpdateError(ContainerError):
    """Raised for general errors during container update."""

    def __init__(self, message="Error updating container.", status_code=500, payload=None):
        super().__init__(message, status_code, payload)


class ContainerManagerNotSupportedError(ContainerError):
    """Raised when a container manager is not supported."""

    def __init__(self, message="Container manager not supported.", status_code=501, payload=None):
        super().__init__(message, status_code, payload)
