from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from flasgger import swag_from
from marshmallow import ValidationError
from FlaredUI.Modules.DB import db, TunnelSchema, ApplicationTunnelSchema, create_tunnel, get_all_tunnels, \
    get_tunnel_by_id, update_tunnel, delete_tunnel, get_application_by_id, get_routes_for_tunnel, get_route_by_id
from FlaredUI.Modules.Cloudflare import create_cloudflared_tunnel, cloudflared_tunnel_delete, \
    cloudflared_tunnel_cleanup, generate_cloudflared_config, cloudflared_route_delete, cloudflared_route_create, \
    get_cloudflared_tunnel_info
from FlaredUI.Modules.Errors import CloudflaredError
from sqlalchemy.exc import SQLAlchemyError
from markupsafe import Markup

db_cf_bp = Blueprint("cf", __name__, url_prefix="/api/cloudflare")


# --- Cloudflare Tunnel Database Routes ---


@db_cf_bp.route('/tunnels', methods=['POST'])
@swag_from('../../SwagDocs/Tunnels/create_tunnel.yml')
@login_required
def create_tunnel_route():
    """Creates a new tunnel in the database and using cloudflared."""

    # Validate input data
    data = request.get_json()
    try:
        # Validate input data against schema
        TunnelSchema().load(data)
    except ValidationError as err:
        return jsonify(err.messages), 400

    try:
        tunnel_name = Markup.escape(data['name'])  # escape name
        tunnel_domain = Markup.escape(data['domain'])  # escape domain
        tunnel_description = Markup.escape(data.get('description'))  # escape description
        tunnel = create_tunnel(
            name=tunnel_name,
            uuid=None,
            domain=tunnel_domain,
            description=tunnel_description
        )

        # Create the tunnel using cloudflared CLI
        cloudflared_tunnel_info = create_cloudflared_tunnel(data['name'])
        tunnel_uuid = cloudflared_tunnel_info["id"]  # Get the generated UUID

        # Update the tunnel in the database with the UUID
        tunnel.uuid = tunnel_uuid
        db.session.commit()

        # Generate and update the config.yml file
        generate_cloudflared_config(tunnel.id)

        return jsonify(tunnel.to_dict()), 201
    except ValidationError as err:
        db.session.rollback()  # Rollback the transaction if validation fails
        app.logger.error(f"Validation error creating tunnel: {err.messages}")
        return jsonify(err.messages), 400  # Bad Request
    except (CloudflaredError) as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500
    except Exception as e:
        db.session.rollback()
        app.logger.error(f"Unexpected error creating tunnel: {e}")
        return jsonify({"error": "Internal server error"}), 500


@db_cf_bp.route('/tunnels', methods=['GET'])
@swag_from('../../SwagDocs/Tunnels/list_tunnels.yml')
@login_required
def list_tunnels_route():
    """Lists all tunnels in the database."""

    try:
        tunnels = get_all_tunnels()
        tunnel_list = []
        for tunnel in tunnels:
            tunnel_data = tunnel.to_dict()

            # Get additional tunnel information from cloudflared
            try:
                tunnel_data['cloudflared_tunnel_details'] = get_cloudflared_tunnel_info(tunnel.uuid)
            except CloudflaredError as e:
                # If we cant get the info return an empty dict
                tunnel_data['cloudflared_tunnel_details'] = {}

            tunnel_list.append(tunnel_data)

        return jsonify(tunnel_list)
    except Exception as e:
        app.logger.error(f"Error listing tunnels: {e}")
        return jsonify({"error": "Internal server error"}), 500


@db_cf_bp.route('/tunnels/<int:tunnel_id>', methods=['GET'])
@swag_from('../../SwagDocs/Tunnels/get_tunnel.yml')
@login_required
def get_tunnel_route(tunnel_id):
    """Retrieves details of a specific tunnel by ID."""

    try:
        tunnel = get_tunnel_by_id(tunnel_id)
        if not tunnel:
            return jsonify({"error": "Tunnel not found"}), 404

        tunnel_data = tunnel.to_dict()

        # Get additional tunnel information from cloudflared
        try:
            tunnel_data['cloudflared_tunnel_details'] = get_cloudflared_tunnel_info(tunnel.uuid)
        except CloudflaredError as e:
            # If we cant get the info return an empty dict
            tunnel_data['cloudflared_tunnel_details'] = {}

        return jsonify(tunnel_data), 200
    except Exception as e:
        app.logger.error(f"Error getting tunnel: {e}")
        return jsonify({"error": "Internal server error"}), 500


@db_cf_bp.route('/tunnels/<int:tunnel_id>', methods=['PUT'])
@swag_from('../../SwagDocs/Tunnels/update_tunnel.yml')
@login_required
def update_tunnel_route(tunnel_id):
    """Updates a tunnel's information."""

    try:
        data = request.get_json()
        TunnelSchema().load(data)

        tunnel = update_tunnel(tunnel_id, **data)
        if not tunnel:
            return jsonify({"error": "Tunnel not found"}), 404

        # Regenerate and update config.yml after updating the tunnel
        generate_cloudflared_config(tunnel_id)
        return jsonify(tunnel.to_dict()), 200
    except ValidationError as err:
        return jsonify(err.messages), 400
    except Exception as e:  # Catch any other unexpected exceptions
        db.session.rollback()
        app.logger.error(f"Error updating tunnel: {e}")
        return jsonify({"error": "Internal server error"}), 500


@db_cf_bp.route('/tunnels/<int:tunnel_id>', methods=['DELETE'])
@swag_from('../../SwagDocs/Tunnels/delete_tunnel.yml')
@login_required
def delete_tunnel_route(tunnel_id):
    """Deletes a tunnel from the database."""

    try:
        tunnel = delete_tunnel(tunnel_id)
        if not tunnel:
            return jsonify({"error": "Tunnel not found"}), 404

        # Cleanup the tunnel (stop and delete config)
        cloudflared_tunnel_delete(tunnel.uuid)
        cloudflared_tunnel_cleanup(tunnel.uuid)  # Clean up config

        return jsonify({"message": "Tunnel deleted successfully"}), 200
    except Exception as e:  # Catch any other unexpected exceptions
        db.session.rollback()  # Rollback the database transaction if an error occurs
        app.logger.error(f"Error deleting tunnel: {e}")
        return jsonify({"error": "Internal server error"}), 500


# --- Routes Routes ---
@db_cf_bp.route('/tunnels/<tunnel_id>/routes', methods=['GET'])
@swag_from('../../SwagDocs/Routes/list_routes.yml')
@login_required
def list_routes(tunnel_id):
    """List all configured routes for a specific tunnel."""

    try:
        tunnel = get_tunnel_by_id(tunnel_id)
        if not tunnel:
            return jsonify({"error": "Tunnel not found"}), 404

        routes = get_routes_for_tunnel(tunnel_id)
        return jsonify([route.to_dict() for route in routes]), 200
    except Exception as e:
        app.logger.error(f"Error listing routes: {e}")
        return jsonify({"error": str(e)}), 500


@db_cf_bp.route('/routes', methods=['POST'])
@swag_from('../../SwagDocs/Routes/create_route.yml')
@login_required
def create_route():
    """Creates a new route for the specified tunnel and application."""

    try:
        data = request.get_json()
        ApplicationTunnelSchema().load(data)

        # Get the tunnel
        tunnel = get_tunnel_by_id(data['tunnel_id'])
        if not tunnel:
            return jsonify({"error": "Tunnel not found"}), 404

        # Get the application
        application = get_application_by_id(data['application_id'])
        if not application:
            return jsonify({"error": "Application not found"}), 404

        # Associate the application with the tunnel
        tunnel.applications.append(application)
        db.session.commit()

        # Create the route using cloudflared CLI
        cloudflared_route_create(tunnel.uuid, application.hostname, application.service_url)

        # Regenerate and update config.yml after adding a new route
        generate_cloudflared_config(tunnel)

        return jsonify({"message": "Route created successfully", "route": application.to_dict()}), 201
    except ValidationError as err:
        return jsonify(err.messages), 400
    except Exception as e:
        app.logger.error(f"Error creating route: {e}")
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@db_cf_bp.route('/routes/<int:route_id>', methods=['PUT'])
@swag_from('../../SwagDocs/Routes/update_route.yml')
@login_required
def update_route(route_id):
    """Updates an application's hostname or tunnel association."""

    try:
        data = request.get_json()
        ApplicationTunnelSchema(partial=True).load(data)  # Validate input data, allow partial updates

        # Get the application associated with the route
        application = get_route_by_id(route_id)
        if not application:
            raise ValueError("Application not found.")

        # Update the application's hostname or tunnel association
        for key, value in data.items():
            if key == 'tunnel_id':
                tunnel = get_tunnel_by_id(value)
                if not tunnel:
                    return jsonify({"error": "Tunnel not found"}), 404
                application.tunnels = [tunnel]  # Set as the only associated tunnel
            else:
                setattr(application, key, value)  # Update other attributes

        db.session.commit()
        app.logger.info(f"Updated route: {application.hostname} for tunnel {application.tunnel.name}")
        return jsonify({"message": "Route updated successfully", "application": application.to_dict()}), 200
    except ValidationError as err:
        return jsonify(err.messages), 400
    except SQLAlchemyError as e:
        app.logger.error(f"Database error updating route: {e}")
        raise Exception("Database error.")


@db_cf_bp.route('/routes/<int:route_id>', methods=['DELETE'])
@swag_from('../../SwagDocs/Routes/delete_route.yml')
@login_required
def delete_route(route_id):
    """Deletes an application's association with a tunnel."""

    try:
        application = get_route_by_id(route_id)
        if not application:
            raise ValueError(f"Application with ID {route_id} not found.")

        # Remove the application from its associated tunnels
        if application.tunnels:
            for tunnel in application.tunnels:
                cloudflared_route_delete(tunnel.uuid, application.hostname)
                application.tunnels.remove(tunnel)

        db.session.commit()
        app.logger.info(f"Deleted route for application ID: {route_id}")
        return jsonify({"message": "Route deleted successfully"}), 200
    except SQLAlchemyError as e:
        app.logger.error(f"Database error deleting route: {e}")
        raise Exception("Database error.")