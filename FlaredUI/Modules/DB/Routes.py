from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from marshmallow import ValidationError
from cachetools import cached, TTLCache
from FlaredUI.Modules.DB import db, Application, Tunnel, get_tunnel_by_id, ApplicationTunnelSchema
from FlaredUI.Modules.Errors import TunnelNotFoundError
from FlaredUI.Logging import get_logger


logger = get_logger(__name__)


def create_route(data):
    """Creates a new route associated with a tunnel and an application."""

    try:
        # Validate input data
        ApplicationTunnelSchema().load(data)

        # Fetch the tunnel and application
        tunnel = Tunnel.query.get(data['tunnel_id'])
        application = Application.query.get(data['application_id'])

        # Associate the application with the tunnel
        tunnel.applications.append(application)
        db.session.commit()

        logger.info(f"Created route: {application.hostname} for tunnel {tunnel.name}")
        return application

    except ValidationError as err:
        logger.error(f"Validation error creating route: {err.messages}")
        raise ValueError(err.messages)
    except SQLAlchemyError as e:
        db.session.rollback()
        logger.error(f"Database error creating route: {e}")
        raise Exception("Database error.")
    except ValueError as e:
        logger.error(f"Value error creating route: {e}")
        raise e


# Modify get_routes_for_tunnel function
@cached(cache=TTLCache(maxsize=1024, ttl=300))
def get_routes_for_tunnel(tunnel_id):
    """Retrieves all applications associated with a tunnel."""

    try:
        tunnel = get_tunnel_by_id(tunnel_id)
        if not tunnel:
            raise TunnelNotFoundError(f"Tunnel with ID {tunnel_id} not found.")
        return tunnel.applications  # Use the 'applications' relationship
    except SQLAlchemyError as e:
        logger.error(f"Database error getting routes for tunnel {tunnel_id}: {e}")
        raise Exception("Database error.")


# Modify get_route_by_id function
@cached(cache=TTLCache(maxsize=1024, ttl=300))
def get_route_by_id(application_id):
    """Retrieves an application by its ID (route)."""

    try:
        application = Application.query.get(application_id)
        if not application:
            raise ValueError(f"Application with ID {application_id} not found.")
        return application
    except SQLAlchemyError as e:
        logger.error(f"Database error getting application by ID: {e}")
        raise Exception("Database error.")


# Modify update_route function
def update_route(application_id, data):
    """Updates an application's hostname or tunnel association."""

    try:
        # TODO: Validate input data (likely need to create a new schema for this)

        application = Application.query.get(application_id)
        if not application:
            raise ValueError("Application not found.")

        for key, value in data.items():
            if key == "tunnel_id":  # Update tunnel association
                tunnel = Tunnel.query.get(value)
                if not tunnel:
                    raise TunnelNotFoundError(f"Tunnel with ID {value} not found.")
                application.tunnels = [tunnel]  # Set as the only associated tunnel
            else:
                setattr(application, key, value)  # Update other attributes

        db.session.commit()

        get_routes_for_tunnel.cache_clear()
        get_route_by_id.cache_clear()
        logger.info(f"Updated route: {application.hostname} for tunnel {application.tunnel.name}")
        return application
    except ValidationError as err:
        logger.error(f"Validation error updating route: {err.messages}")
        raise ValueError(err.messages)
    except SQLAlchemyError as e:
        logger.error(f"Database error updating route: {e}")
        raise Exception("Database error.")


# Modify delete_route function
def delete_route(application_id):
    """Deletes a route (application association with tunnel) by ID."""

    try:
        application = get_route_by_id(application_id)
        if not application:
            raise ValueError(f"Application with ID {application_id} not found.")

        if application.tunnel:  # Remove from tunnel if associated
            application.tunnels.remove(application.tunnel)
            db.session.commit()

        logger.info(
            f"Deleted route: {application.hostname} from tunnel {application.tunnel.name if application.tunnel else None}")
        return application
    except SQLAlchemyError as e:
        logger.error(f"Database error deleting route: {e}")
        raise Exception("Database error.")
