from flask import Blueprint, jsonify
from flask_login import login_required
from FlaredUI.Modules.DB import db, get_plugin_by_id, update_plugin
from FlaredUI.Modules.Errors import PluginNotFoundError, PluginInvalidOperationError
from flasgger import swag_from

op_plugin_bp = Blueprint("op_plugins", __name__, url_prefix="/api/plugins")


@op_plugin_bp.route("/<int:plugin_id>/activate", methods=["POST"])
@swag_from('../../SwagDocs/Plugins/activate_plugin.yml')
@login_required
def activate_plugin(plugin_id):
    """Activate a plugin by ID."""
    try:
        plugin = get_plugin_by_id(plugin_id)
        if not plugin:
            return jsonify({"error": "Plugin not found"}), 404
        # TODO: Add your activation logic here
        app.logger.info(f"Activated plugin '{plugin.name}'")
        return jsonify({"message": f"Plugin '{plugin.name}' activated"}), 200

    except Exception as e:
        app.logger.error(f"Error activating plugin: {e}")
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@op_plugin_bp.route("/<int:plugin_id>/deactivate", methods=["POST"])
@swag_from('../../SwagDocs/Plugins/deactivate_plugin.yml')
@login_required
def deactivate_plugin(plugin_id):
    """Deactivate a plugin by ID."""

    try:
        plugin = get_plugin_by_id(plugin_id)
        if not plugin:
            raise PluginNotFoundError()

        if not plugin.active:
            raise PluginInvalidOperationError("Plugin is already deactivated.")

        plugin.active = False
        update_plugin(plugin.id, plugin.to_dict())  # Save changes to the database
        app.logger.info(f"Deactivated plugin '{plugin.name}'")
        return jsonify({"message": f"Plugin '{plugin.name}' deactivated"}), 200
    except (PluginNotFoundError, PluginInvalidOperationError) as e:
        # Handle specific plugin errors
        return jsonify({"error": str(e)}), 400  # Bad Request
    except Exception as e:
        # Log and handle other unexpected errors
        app.logger.error(f"Error deactivating plugin: {e}")
        db.session.rollback()
        return jsonify({"error": "Internal Server Error"}), 500