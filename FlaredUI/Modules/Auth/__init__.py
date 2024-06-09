from flask_login import LoginManager
from FlaredUI.Modules.Utilities import ModulesUtility
import sys


# Create LoginManager (if needed)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "auth.userpass_login"


# Get the current module
current_module = sys.modules[__name__]


# Initialize the utility class
utils = ModulesUtility(current_module.__name__)


# Import submodules using the current module object
utils.import_submodules(current_module)


# Dynamically create __all__
utils.export_globals()
