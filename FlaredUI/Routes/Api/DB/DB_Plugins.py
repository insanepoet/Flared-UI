from flask import Blueprint, request, jsonify
from flask_login import login_required
from FlaredUI.Modules.DB import (
    db, create_plugin_repo, get_plugin_repos, get_plugin_repo_by_id,
    update_plugin_repo, delete_plugin_repo, create_plugin,
    get_plugins, get_plugin_by_id, PluginRepositorySchema, PluginSchema
)
from marshmallow import ValidationError
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from flasgger import swag_from
from FlaredUI.Logging import get_logger

logger = get_logger(__name__)


db_plugin_bp = Blueprint("db_plugins", __name__)


# --- Plugin Repository Routes ---

@db_plugin_bp.route("/repositories", methods=["POST"])
@swag_from('../../SwagDocs/Plugins/add_plugin_repository.yml')
@login_required
def add_plugin_repository_route():
    """Add a new plugin repository."""
    try:
        data = request.get_json()
        PluginRepositorySchema().load(data)
        repository = create_plugin_repo(**data)
        return jsonify(repository.to_dict()), 201
    except ValidationError as err:
        return jsonify(err.messages), 400


@db_plugin_bp.route("/repositories", methods=["GET"])
@swag_from('../../SwagDocs/Plugins/list_plugin_repositories.yml')
@login_required
def list_plugin_repositories_route():
    """List all plugin repositories."""
    repositories = get_plugin_repos()
    return jsonify([repo.to_dict() for repo in repositories])


@db_plugin_bp.route("/repositories/<int:repo_id>", methods=["PUT"])
@swag_from('update_plugin_repository.yml')  # Create this YAML file for update schema
@login_required
def update_plugin_repository_route(repo_id):
    """Update a plugin repository by ID."""
    try:
        data = request.get_json()
        PluginRepositorySchema(partial=True).load(data)
        updated_repo = update_plugin_repo(repo_id, data)
        if not updated_repo:
            return jsonify({"error": "Plugin repository not found"}), 404
        return jsonify(updated_repo.to_dict())
    except ValidationError as err:
        return jsonify(err.messages), 400


@db_plugin_bp.route("/repositories/<int:repo_id>", methods=["DELETE"])
@swag_from('delete_plugin_repository.yml')  # Create this YAML file
@login_required
def delete_plugin_repository_route(repo_id):
    """Delete a plugin repository by ID."""

    try:
        deleted_repo = delete_plugin_repo(repo_id)
        if not deleted_repo:
            return jsonify({"error": "Plugin repository not found"}), 404
        return jsonify({"message": f"Plugin repository '{deleted_repo.name}' deleted"}), 200
    except Exception as e:
        logger.error(f"Error deleting plugin repository: {e}")
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


# --- Plugin Routes ---
@db_plugin_bp.route("/", methods=["POST"])
@swag_from('../../SwagDocs/Plugins/add_plugin.yml')  # Create this YAML file
@login_required
def add_plugin_route():
    """Add a new plugin."""
    try:
        data = request.get_json()
        PluginSchema().load(data)
        plugin = create_plugin(**data)
        return jsonify(plugin.to_dict()), 201
    except ValidationError as err:
        return jsonify(err.messages), 400
    except IntegrityError as e:  # Handle unique constraint violations
        db.session.rollback()
        raise ValueError(
            f"Plugin with name '{data['name']}' from repository ID {data['repository_id']} already exists.") from e
    except SQLAlchemyError as e:
        db.session.rollback()
        raise Exception(f"Database error: {e}")


@db_plugin_bp.route("/", methods=["GET"])
@swag_from('../../SwagDocs/Plugins/list_plugins.yml')
@login_required
def list_plugins_route():
    """List all plugins."""
    plugins = get_plugins()
    return jsonify([plugin.to_dict() for plugin in plugins])


@db_plugin_bp.route("/<int:plugin_id>", methods=["GET"])
@swag_from('get_plugin_by_id.yml')
@login_required
def get_plugin_by_id_route(plugin_id):
    """Retrieve a plugin by its ID."""

    try:
        plugin = get_plugin_by_id(plugin_id)
        if not plugin:
            return jsonify({"error": "Plugin not found"}), 404
        return jsonify(plugin.to_dict())
    except Exception as e:  # Catch general exceptions for error handling
        logger.error(f"Error getting plugin: {e}")
        return jsonify({"error": str(e)}), 500


@db_plugin_bp.route("/<int:plugin_id>", methods=["PUT"])
@swag_from('update_plugin.yml')  # Create this YAML file for update schema
@login_required
def update_plugin_route(plugin_id):
    """Update a plugin by ID."""
    try:
        data = request.get_json()
        PluginSchema(partial=True).load(data)
        updated_plugin = update_plugin_route(plugin_id, data)
        if not updated_plugin:
            return jsonify({"error": "Plugin not found"}), 404
        return jsonify(updated_plugin.to_dict())
    except ValidationError as err:
        return jsonify(err.messages), 400


@db_plugin_bp.route("/<int:plugin_id>", methods=["DELETE"])
@swag_from('delete_plugin.yml')  # Create this YAML file
@login_required
def delete_plugin_route(plugin_id):
    """Delete a plugin by ID."""

    try:
        deleted_plugin = delete_plugin_route(plugin_id)
        if not deleted_plugin:
            return jsonify({"error": "Plugin not found"}), 404
        return jsonify({"message": f"Plugin '{deleted_plugin.name}' deleted"}), 200
    except Exception as e:
        logger.error(f"Error deleting plugin: {e}")
        db.session.rollback()
        return jsonify({"error": str(e)}), 500
