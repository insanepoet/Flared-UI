from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from flasgger import swag_from
from marshmallow import ValidationError
from FlaredUI.Modules.DB import (
    db, get_all_api_keys, get_api_key_by_id, get_api_keys_by_user,
    create_api_key, update_api_key, delete_api_key
)
from FlaredUI.Logging import get_logger

logger = get_logger(__name__)


api_keys_bp = Blueprint("api_keys", __name__)


# --- API Key Routes ---
@api_keys_bp.route('/', methods=['POST'])
@swag_from('../../SwagDocs/ApiKeys/create_api_key.yml')
@login_required
def create_api_key_route():
    """Creates a new API key for the current user."""

    try:
        data = request.get_json()

        # Use the current_user ID
        data['user_id'] = current_user.id

        # Validate and create the API key
        api_key = create_api_key(data)

        # Return the created API key, excluding the value for security
        return jsonify(api_key.to_dict()), 201
    except ValidationError as err:
        logger.error(f"Validation error creating API key: {err.messages}")
        return jsonify(err.messages), 400  # Bad Request
    except ValueError as e:  # Catch ValueError from create_api_key
        logger.error(f"Value error creating API key: {e}")
        return jsonify({"error": str(e)}), 400  # Bad Request for invalid input
    except Exception as e:
        logger.error(f"Error creating API key: {e}")
        db.session.rollback()
        return jsonify({"error": "Internal server error"}), 500  # Internal Server Error


@api_keys_bp.route('/', methods=['GET'])
@swag_from('../../SwagDocs/ApiKeys/list_api_keys.yml')
@login_required
def list_api_keys_route():
    """Lists all API keys for the current user."""

    try:
        api_keys = get_api_keys_by_user(current_user.id)
        return jsonify([api_key.to_dict() for api_key in api_keys])
    except Exception as e:  # Catch any unexpected errors
        logger.error(f"Error listing API keys: {e}")
        return jsonify({"error": "Internal server error"}), 500


@api_keys_bp.route('/<int:api_key_id>', methods=['GET'])
@swag_from('../../SwagDocs/ApiKeys/get_api_key.yml')
@login_required
def get_api_key_route(api_key_id):
    """Retrieves an API key by its ID, but excludes the actual key value."""

    try:
        api_key = get_api_key_by_id(api_key_id)
        if not api_key:
            raise ValueError("API key not found")
        return jsonify(api_key.to_dict())
    except Exception as e:  # Catch any unexpected errors
        logger.error(f"Error getting API key: {e}")
        return jsonify({"error": "Internal server error"}), 500


@api_keys_bp.route('/<int:api_key_id>', methods=['PUT'])
@swag_from('../../SwagDocs/ApiKeys/update_api_key.yml')
@login_required
def update_api_key_route(api_key_id):
    """Updates an API key's information (name and description)."""

    try:
        data = request.get_json()
        update_api_key(api_key_id, data)

        api_key = get_api_key_by_id(api_key_id)
        if not api_key:
            raise ValueError("API key not found")
        return jsonify(api_key.to_dict()), 200
    except ValidationError as err:
        logger.error(f"Validation error updating API key: {err.messages}")
        return jsonify(err.messages), 400  # Bad Request
    except ValueError as e:
        return jsonify({"error": str(e)}), 404  # Not Found
    except Exception as e:  # Catch any other unexpected errors
        db.session.rollback()
        logger.error(f"Error updating API key: {e}")
        return jsonify({"error": "Internal server error"}), 500


@api_keys_bp.route('/<int:api_key_id>', methods=['DELETE'])
@swag_from('../../SwagDocs/ApiKeys/delete_api_key.yml')
@login_required
def delete_api_key_route(api_key_id):
    """Deletes an API key."""
    try:
        api_key = delete_api_key(api_key_id)
        if not api_key:
            raise ValueError("API key not found")
        return jsonify(api_key.to_dict()), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 404  # Not Found
    except Exception as e:  # Catch any other unexpected errors

        logger.error(f"Error deleting API key: {e}")
        return jsonify({"error": "Internal server error"}), 500