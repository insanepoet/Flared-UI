
from flask import jsonify

from sqlalchemy.exc import IntegrityError, SQLAlchemyError  # Import SQLAlchemyError
from Backend.Modules.DB import db, Servers, Managers, Contained, Server, ServerSchema, get_all_servers, get_server_by_id, update_server, delete_server
from marshmallow import ValidationError
from cachetools import cached, TTLCache
from FlaredUI.Logging import get_logger


logger = get_logger(__name__)


# --- Server Handler Functions ---
def create_server_handler(request):
    """Handles the server creation request."""
    try:
        data = request.get_json()

        # Validate input data using Marshmallow
        server_schema = ServerSchema()
        server_data = server_schema.load(data)

        server = create_server_handler(server_data)
        server_dict = server.to_dict()
        server_dict.pop('password_hash')  # Don't include password hash in the response

        logger.info(f"Server '{server.name}' created successfully.")
        return jsonify(server_dict), 201
    except ValidationError as err:
        logger.error(f"Validation error creating server: {err.messages}")
        return jsonify(err.messages), 400  # Bad Request
    except ValueError as e:  # Catch ValueError from database functions
        logger.error(f"Error creating server: {e}")
        return jsonify({"error": str(e)}), 400  # Bad Request for invalid input
    except Exception as e:  # Catch any other unexpected exceptions
        logger.error(f"Unexpected error creating server: {e}")
        db.session.rollback()
        return jsonify({"error": "Internal server error"}), 500  # Internal Server Error


@cached(cache=TTLCache(maxsize=1024, ttl=300))
def list_servers_handler():
    """Handles the request to list all servers."""
    try:
        servers = get_all_servers()
        logger.info(f"Listed all servers successfully.")
        return jsonify([server.to_dict() for server in servers])
    except SQLAlchemyError as e:
        logger.error(f"Database error listing servers: {e}")
        return jsonify({"error": "Internal server error"}), 500  # Internal Server Error


@cached(cache=TTLCache(maxsize=1024, ttl=300))
def get_server_handler(server_id):
    """Handles the request to get a server by ID."""
    try:
        server = get_server_by_id(server_id)
        if not server:
            logger.warning(f"Server with ID {server_id} not found.")
            return jsonify({"error": "Server not found"}), 404
        server_dict = server.to_dict()
        server_dict.pop('password_hash')  # Don't include password hash in response
        logger.info(f"Retrieved server '{server.name}' (ID: {server_id}) successfully.")
        return jsonify(server_dict)
    except Exception as e:  # Catch any unexpected errors
        logger.error(f"Unexpected error getting server by ID: {e}")
        return jsonify({"error": "Internal server error"}), 500


def update_server_handler(request, server_id):
    """Handles the request to update a server by ID."""
    try:
        data = request.get_json()
        ServerSchema(exclude=['password']).load(data)
    except ValidationError as err:
        return jsonify(err.messages), 400

    try:
        server = update_server(server_id, **data)
        if not server:
            return jsonify({"error": "Server not found"}), 404
        server_dict = server.to_dict()
        server_dict.pop('password_hash')
        logger.info(f"Updated server '{server.name}' (ID: {server_id}) successfully.")
        return jsonify(server_dict), 200
    except Exception as e:  # Catch any unexpected errors
        logger.error(f"Unexpected error updating server: {e}")
        db.session.rollback()
        return jsonify({"error": "Internal server error"}), 500


def delete_server_handler(server_id):
    """Handles the request to delete a server by ID."""
    try:
        server = delete_server(server_id)
        if not server:
            logger.warning(f"Server with ID {server_id} not found for deletion.")
            return jsonify({"error": "Server not found"}), 404
        logger.info(f"Deleted server '{server.name}' (ID: {server_id}) successfully.")
        return jsonify({"message": "Server deleted successfully"}), 200
    except Exception as e:
        logger.error(f"Unexpected error deleting server: {e}")
        db.session.rollback()
        return jsonify({"error": "Internal server error"}), 500

