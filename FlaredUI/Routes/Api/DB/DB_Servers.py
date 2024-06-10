from flask import Blueprint, request, jsonify
from flask_login import login_required
from FlaredUI.Modules.DB import ServerSchema, create_server, get_all_servers, get_server_by_id, update_server, \
    delete_server
from FlaredUI.Modules.Errors import ServerNotFoundError
from flasgger import swag_from
from marshmallow import ValidationError

db_server_bp = Blueprint('server', __name__, url_prefix='/api/servers')


# --- Server Routes ---
@db_server_bp.route('/', methods=['POST'])
@swag_from('../../SwagDocs/Servers/create_server.yml')  # TODO: Update the path to the YAML file
@login_required
def create_server_route():
    """Creates a new server."""
    return create_server(request)


@db_server_bp.route('/', methods=['GET'])
@swag_from('../../SwagDocs/Servers/list_servers.yml')  # Update the path to the YAML file
@login_required
def list_servers_route():
    """Lists all servers."""
    return get_all_servers()


@db_server_bp.route('/<int:server_id>', methods=['GET'])
@swag_from('../../SwagDocs/Servers/get_server.yml')  # Update the path to the YAML file
@login_required
def get_server_route(server_id):
    """Retrieves a server by ID."""

    try:
        server = get_server_by_id(server_id)
        if not server:
            raise ServerNotFoundError(f"Server not found with id {server_id}")
        return jsonify(server.to_dict())
    except ServerNotFoundError as e:
        app.logger.error(str(e))
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        app.logger.error(f"Unexpected error retrieving server: {e}")
        return jsonify({"error": "Internal server error"}), 500


@db_server_bp.route('/<int:server_id>', methods=['PUT'])
@swag_from('../../SwagDocs/Servers/update_server.yml')  # Update the path to the YAML file
@login_required
def update_server_route(server_id):
    """Updates a server by ID."""

    try:
        data = request.get_json()
        server_schema = ServerSchema(exclude=['id'])  # Exclude the ID as it shouldn't be updated
        server_schema.load(data)
        return update_server(request, server_id)
    except ValidationError as err:
        app.logger.error(f"Validation error updating server: {err.messages}")
        return jsonify({"error": err.messages}), 400


@db_server_bp.route('/<int:server_id>', methods=['DELETE'])
@swag_from('../../SwagDocs/Servers/delete_server.yml')  # Update the path to the YAML file
@login_required
def delete_server_route(server_id):
    """Deletes a server by ID."""
    return delete_server(server_id)

