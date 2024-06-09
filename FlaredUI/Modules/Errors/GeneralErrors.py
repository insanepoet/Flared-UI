from FlaredUI import Logging as logging


class CustomFlaskError(Exception):
    """Base class for custom Flask errors with integrated logging."""

    def __init__(self, message, status_code=None, payload=None):
        Exception.__init__(self)
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        self.payload = payload
        self.log_error()  # Call the logging method

    def to_dict(self):
        rv = dict(self.payload or ())
        rv['message'] = self.message
        return rv

    def log_error(self):
        """Logs the error with traceback information."""
        logger = logging.get_logger(__name__)
        logger.error(self.message, exc_info=True)


class ModuleImportError(CustomFlaskError):
    """Raised when a module or submodule fails to import."""

    def __init__(self, module_name, message=None, status_code=500, payload=None):
        if message is None:
            message = f"Failed to import module: {module_name}"
        super().__init__(message, status_code, payload)


class ModuleLogger:
    """Class to handle module-level logging consistently."""

    def __init__(self, module_name):
        self.logger = logging.get_logger(module_name)

    def debug(self, message):
        """Logs a debug message."""
        self.logger.debug(message)

    def info(self, message):
        """Logs an info message."""
        self.logger.info(message)

    def warning(self, message):
        """Logs a warning message."""
        self.logger.warning(message)

    def error(self, message):
        """Logs an error message."""
        self.logger.error(message)

    def critical(self, message):
        """Logs a critical message."""
        self.logger.critical(message)


class UnauthorizedError(CustomFlaskError):
    """Raised when an action is not allowed due to insufficient permissions."""

    def __init__(self, message="Unauthorized", status_code=401, payload=None):
        super().__init__(message, status_code, payload)


class NotImplementedError(CustomFlaskError):
    """Raised when a feature or functionality is not yet implemented."""

    def __init__(self, message="Not Implemented", status_code=501, payload=None):
        super().__init__(message, status_code, payload)


class UserNotFoundError(CustomFlaskError):
    """Raised when a user is not found."""

    def __init__(self, message="User not found.", status_code=404, payload=None):
        super().__init__(message, status_code, payload)


class TunnelNotFoundError(CustomFlaskError):
    """Raised when a tunnel is not found in the database."""

    def __init__(self, message="Tunnel not found.", status_code=404, payload=None):
        super().__init__(message, status_code, payload)