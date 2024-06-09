from FlaredUI.Modules.DB import create_plugin_repo, get_plugin_repos, get_plugins
from FlaredUI.Modules.Errors import PluginError
from flask import jsonify
from FlaredUI.Logging import get_logger


logger = get_logger(__name__)


# --- Plugin Handler Functions ---
def add_plugin_repository_handler(request):
    """Handles the request to add a plugin repository."""
    try:
        data = request.get_json()

        # Validate repository data (use Marshmallow or similar)
        if not data.get("name") or not data.get("url"):
            raise ValueError("Name and URL are required for a plugin repository.")

        repo = create_plugin_repo(data["name"], data["url"])
        return jsonify(repo.to_dict()), 201

    except (ValueError, PluginError) as e:
        logger.error(f"Error adding plugin repository: {e}")
        return jsonify({"error": str(e)}), 400


def list_plugin_repositories_handler():
    """Handles the request to list all plugin repositories."""
    try:
        repos = get_plugin_repos()
        return jsonify([repo.to_dict() for repo in repos]), 200
    except PluginError as e:
        logger.error(f"Error listing plugin repositories: {e}")
        return jsonify({"error": str(e)}), 500


def list_plugins_handler():
    """Handles the request to list all plugins."""
    try:
        plugins = get_plugins()
        return jsonify([plugin.to_dict() for plugin in plugins]), 200
    except PluginError as e:
        logger.error(f"Error listing plugins: {e}")
        return jsonify({"error": str(e)}), 500


# ... (Add other handler functions for install, uninstall, activate, deactivate)
