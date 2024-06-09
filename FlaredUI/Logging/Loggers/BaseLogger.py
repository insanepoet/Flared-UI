import logging
import logging.config
from FlaredUI.Logging.Logging_Config import LOGGING_CONFIG


class BaseLogger:
    """A base logger class for handling logging when a module-specific logger is not found."""

    def __init__(self, name="BaseLogger", level=logging.DEBUG):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(level)
        self.logger.propagate = True

    def debug(self, msg, *args, **kwargs):
        self.logger.debug(msg, *args, **kwargs)

    def info(self, msg, *args, **kwargs):
        self.logger.info(msg, *args, **kwargs)

    def warning(self, msg, *args, **kwargs):
        self.logger.warning(msg, *args, **kwargs)

    def error(self, msg, *args, **kwargs):
        self.logger.error(msg, *args, **kwargs)

    def critical(self, msg, *args, **kwargs):
        self.logger.critical(msg, *args, **kwargs)


# Create an instance of the BaseLogger that will be used by default
logger = BaseLogger()
