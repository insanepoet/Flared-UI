from flask import Blueprint, request, jsonify
from flask_login import login_required
from FlaredUI.Modules.DB import (
    get_all_containers, get_container_by_id,
    get_containers_by_server, update_container,
    delete_container, ContainerSchema,
    get_server_by_id
)
from FlaredUI.Modules.Containers import get_container_info, list_containers
from flasgger import swag_from

db_container_bp = Blueprint('container', __name__)


# --- Container Routes ---
@db_container_bp.route('/servers/<int:server_id>/containers', methods=['GET'])
@swag_from('../../SwagDocs/Containers/list_containers.yml')
@login_required
def list_containers_route(server_id):
    """List all containers on a specified server."""

    try:
        server = get_server_by_id(server_id)
        if not server:
            return jsonify({"error": "Server not found"}), 404
        containers = list_containers(server)  # Update the function call
        return jsonify(containers), 200
    except Exception as e:
        app.logger.error(f"Error listing containers: {e}")
        return jsonify({"error": str(e)}), 500


@db_container_bp.route('/servers/<int:server_id>/containers/<string:container_name>', methods=['GET'])
@swag_from('../../SwagDocs/Containers/get_container.yml')
@login_required
def get_container_route(server_id, container_name):
    """Get detailed information about a specific container on a server."""

    try:
        server = get_server_by_id(server_id)
        if not server:
            return jsonify({"error": "Server not found"}), 404

        container_info = get_container_info(server, container_name)
        return jsonify(container_info), 200
    except Exception as e:
        app.logger.error(f"Error getting container info: {e}")
        return jsonify({"error": str(e)}), 500