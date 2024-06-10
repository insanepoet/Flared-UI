from flask import Blueprint
from FlaredUI.Modules.Utilities import BlueprintUtility
import sys


# Create the main API blueprint
api_bp = Blueprint("api", __name__, url_prefix="/api")


# Get the current module (for dynamic blueprint registration)
current_module = sys.modules[__name__]


# Initialize utility classes
blueprint_util = BlueprintUtility(app)


# Dynamically register blueprints
blueprint_util.register_blueprints(current_module)


# Dynamically create __all__ for this module
blueprint_util.export_globals()
