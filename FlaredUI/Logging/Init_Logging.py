import logging
import logging.config
import os
import importlib
from .Logging_Config import LOGGING_CONFIG, load_logger_configurations
from FlaredUI.Modules.DB.Settings import get_app_setting_by_name


def get_logger(module_name="BaseLogger"):
    """Dynamically gets the logger for the specified module."""
    logger_module_path = f"Backend.Logging.Loggers.{module_name}"

    try:
        module = importlib.import_module(logger_module_path)
        return module.logger  # Use the module's logger if found
    except (ImportError, AttributeError):
        # Fallback to the BaseLogger if module or logger attribute not found
        from .Loggers.BaseLogger import logger as base_logger
        return base_logger


def initialize_logging(log_dir=os.path.join(app.root_path, '..', 'Data', 'Logs')):
    os.makedirs(log_dir, exist_ok=True)

    # Update filenames in the configuration based on the log directory
    LOGGING_CONFIG['handlers']['main_file']['filename'] = os.path.join(log_dir, 'application.log')
    LOGGING_CONFIG['handlers']['auth_file']['filename'] = os.path.join(log_dir, 'auth.log')

    # Dynamically load logger configurations
    load_logger_configurations(log_dir)

    # Get log levels and set in the configuration
    log_level_setting = get_app_setting_by_name('LogLevel')
    log_level = log_level_setting.value.upper() if log_level_setting else 'DEBUG'

    # Set the log level for all loggers
    for logger_name in LOGGING_CONFIG['loggers']:
        LOGGING_CONFIG['loggers'][logger_name]['level'] = log_level

    logging.config.dictConfig(LOGGING_CONFIG)
    return get_logger()