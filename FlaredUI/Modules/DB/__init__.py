from flask_sqlalchemy import SQLAlchemy
from FlaredUI.Modules.Utilities import ModulesUtility
import sys


# Create SQLAlchemy database instance but don't initialize yet
db = SQLAlchemy()


# Get the current module
current_module = sys.modules[__name__]


# Initialize the utility class
utils = ModulesUtility(current_module.__name__)


# Import submodules using the current module object
utils.import_submodules(current_module)


# Dynamically create __all__
utils.export_globals()


# Initialize the database after all submodules are loaded
def init_db(app):
    """Initializes the database with the given Flask app instance."""
    db.init_app(app)

# TODO: Implement Caching in all get db functions, Completed: Settings.py
