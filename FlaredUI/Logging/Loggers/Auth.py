import logging
from logging.handlers import RotatingFileHandler
from FlaredUI.Logging.Logging_Config import LOGGING_CONFIG


class AuthLogger:
    def __init__(self):
        self.logger = logging.getLogger("Backend.Modules.Auth")
        self.logger.setLevel(LOGGING_CONFIG['loggers']['']['level'])  # Use same level as root logger
        self.logger.propagate = False  # Prevent propagation

    def get_config(self):
        return {
            'handlers': [h.get_name() for h in self.logger.handlers],
            'level': self.logger.level,
            'propagate': self.logger.propagate,
        }


# Create the logger instance to be used in the module
logger = AuthLogger()
