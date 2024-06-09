from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from marshmallow import ValidationError
from cachetools import cached, TTLCache
from FlaredUI.Modules.DB import db, ServerSchema, Server
from FlaredUI.Modules.Errors import ServerNotFoundError
from FlaredUI.Logging.Init_Logging import get_logger


logger = get_logger(__name__)


def create_server(data):
    """Creates a new server entry in the database."""
    try:
        ServerSchema().load(data)
        server = Server(**data)
        server.set_password(data['password'])
        db.session.add(server)
        db.session.commit()
        logger.info(f"Server created: {server.name}")  # Log server creation
        return server
    except ValidationError as err:
        logger.error(f"Validation error creating server: {err.messages}")
        raise ValueError(err.messages)
    except IntegrityError:
        db.session.rollback()
        logger.error("Integrity error creating server. Server name, hostname, or IP address already exists.")
        raise ValueError("Server name, hostname, or IP address already exists")
    except SQLAlchemyError as e:
        db.session.rollback()
        logger.error(f"Database error creating server: {e}")
        raise Exception("Database error")


@cached(cache=TTLCache(maxsize=1024, ttl=300))
def get_all_servers():
    """Retrieves all servers from the database."""
    try:
        servers = Server.query.all()
        logger.info(f"Retrieved {len(servers)} servers")  # Log number of servers retrieved
        return servers
    except SQLAlchemyError as e:
        logger.error(f"Database error: {e}")
        raise Exception("Database error")


@cached(cache=TTLCache(maxsize=1024, ttl=300))
def get_server_by_id(server_id):
    """Retrieves a server from the database by its ID."""
    try:
        server = Server.query.get(server_id)
        if not server:
            raise ServerNotFoundError(f"Server with ID {server_id} not found")
        return server
    except SQLAlchemyError as e:
        logger.error(f"Database error: {e}")
        raise Exception("Database error")


def update_server(server_id, **kwargs):
    """Updates a server's information in the database."""
    try:
        server = get_server_by_id(server_id)
        if server:
            # Handle password updates separately if provided
            if 'password' in kwargs:
                server.set_password(kwargs.pop('password'))
            for key, value in kwargs.items():
                setattr(server, key, value)  # Set the new attribute values on the server object
            db.session.commit()
            logger.info(f"Server updated: {server.name}")  # Log server update
        return server
    except SQLAlchemyError as e:
        logger.error(f"Database error: {e}")
        raise Exception("Database error")


def delete_server(server_id):
    """Deletes a server from the database by its ID."""
    try:
        server = get_server_by_id(server_id)
        if server:
            db.session.delete(server)  # Delete the server object
            db.session.commit()
            logger.info(f"Server deleted: {server.name}")  # Log server deletion
        return True  # Indicate successful deletion
    except SQLAlchemyError as e:
        logger.error(f"Database error: {e}")
        raise Exception("Database error")
