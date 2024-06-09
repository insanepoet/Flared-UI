import logging.config
import os
import glob
import importlib


# Basic Configuration
LOGGING_CONFIG = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'json': {
            'class': 'pythonjsonlogger.jsonlogger.JsonFormatter',
            'format': '%(asctime)s %(levelname)s %(name)s %(message)s',
        },
    },
    'handlers': {
        'main_file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': '',  # Placeholder, will be set later
            'maxBytes': 1024 * 1024 * 10,  # 10 MB
            'backupCount': 5,
            'formatter': 'json',
        },
        'auth_file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': '',  # Placeholder, will be set later
            'maxBytes': 1024 * 1024 * 10,  # 10 MB
            'backupCount': 5,
            'formatter': 'json',
        },
    },
    'loggers': {
        # This will be populated dynamically
    },
}


# Function to dynamically load logger configurations
def load_logger_configurations(log_dir):
    logger_files = glob.glob(os.path.join(os.path.dirname(__file__), 'Loggers', '*.py'))
    for logger_file in logger_files:
        module_name = os.path.splitext(os.path.basename(logger_file))[0]
        if module_name != '__init__' and module_name != 'BaseLogger':
            try:
                # Check if the module has a logger attribute
                module = importlib.import_module(f"Backend.Logging.Loggers.{module_name}")
                if hasattr(module, 'logger'):
                    LOGGING_CONFIG['loggers'][f'Backend.Modules.{module_name}'] = module.logger.get_config()
            except (ImportError, AttributeError):
                # Log an error if the module cannot be imported or doesn't have a logger attribute
                logging.getLogger("BaseLogger").error(f"Error loading logger configuration for module {module_name}")
