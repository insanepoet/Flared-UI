from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from marshmallow import ValidationError
from cachetools import cached, TTLCache
from FlaredUI.Modules.DB import db, Tunnel, TunnelSchema, TLD, tunnel_tlds
from FlaredUI.Modules.Errors import TunnelNotFoundError
import uuid
from FlaredUI.Logging import get_logger


logger = get_logger(__name__)


def create_tunnel(data):
    """Creates a new tunnel with the given information."""
    try:
        TunnelSchema().load(data)
    except ValidationError as err:

        logger.error(f"Validation error creating tunnel: {err.messages}")
        raise ValueError(err.messages)

    try:
        tunnel_uuid = str(uuid.uuid4())
        tunnel = Tunnel(
            name=data['name'],
            uuid=tunnel_uuid,  # Generate a UUID for the tunnel
            domain=data['domain'],
            description=data.get('description')
        )

        # Associate TLDs
        for tld_name in data.get('tlds', []):
            tld = TLD.query.filter_by(name=tld_name).first()
            if not tld:
                raise ValueError(f"Invalid TLD: {tld_name}")
            tunnel.tlds.append(tld)

        db.session.add(tunnel)
        db.session.commit()
        return tunnel
    except IntegrityError:
        db.session.rollback()
        raise ValueError("Tunnel name or domain already exists")
    except SQLAlchemyError as e:
        db.session.rollback()

        logger.error(f"Database error creating tunnel: {e}")
        raise Exception("Database error")


@cached(cache=TTLCache(maxsize=1024, ttl=300))
def get_all_tunnels():
    """Retrieves all tunnels."""
    try:
        return Tunnel.query.all()
    except SQLAlchemyError as e:

        logger.error(f"Database error: {e}")
        raise Exception("Database error")


@cached(cache=TTLCache(maxsize=1024, ttl=300))
def get_tunnel_by_id(tunnel_id):
    """Retrieves a tunnel by its ID."""
    try:
        tunnel = Tunnel.query.get(tunnel_id)
        if not tunnel:
            raise TunnelNotFoundError(f"Tunnel with ID {tunnel_id} not found.")
        return tunnel
    except SQLAlchemyError as e:

        logger.error(f"Database error: {e}")
        raise Exception("Database error")


@cached(cache=TTLCache(maxsize=1024, ttl=300))
def get_tunnel_by_uuid(uuid):
    """Retrieves a tunnel by its UUID."""
    try:
        tunnel = Tunnel.query.get(uuid)
        if not tunnel:
            raise TunnelNotFoundError(f"Tunnel with UUID {uuid} not found.")
        return tunnel
    except SQLAlchemyError as e:

        logger.error(f"Database error: {e}")
        raise Exception("Database error")


@cached(cache=TTLCache(maxsize=1024, ttl=300))
def get_tunnel_by_name(name):
    """Retrieves a tunnel by its name."""
    try:
        return Tunnel.query.filter_by(name=name).first()
    except SQLAlchemyError as e:

        logger.error(f"Database error: {e}")
        raise Exception("Database error")


def update_tunnel(tunnel_id, **kwargs):
    """Updates a tunnel's information based on the provided keyword arguments."""
    try:
        tunnel = get_tunnel_by_id(tunnel_id)
        if tunnel:
            for key, value in kwargs.items():
                if key == 'tlds':
                    tunnel.tlds = []  # Clear existing associations
                    for tld_name in value:
                        tld = TLD.query.filter_by(name=tld_name).first()
                        if tld:
                            tunnel.tlds.append(tld)  # Add new associations
                else:
                    setattr(tunnel, key, value)
            db.session.commit()

            get_tunnel_by_uuid.cache_clear()
            get_tunnel_by_name.cache_clear()
            get_all_tunnels.cache_clear()
            get_tunnel_by_id.cache_clear()
        return tunnel
    except SQLAlchemyError as e:

        logger.error(f"Database error: {e}")
        raise Exception("Database error")


def delete_tunnel(tunnel_id):
    """Deletes a tunnel by its ID."""
    try:
        tunnel = get_tunnel_by_id(tunnel_id)  # Reuse get_tunnel_by_id to handle errors
        if tunnel:
            db.session.delete(tunnel)
            db.session.commit()
        return tunnel
    except SQLAlchemyError as e:

        logger.error(f"Database error: {e}")
        raise Exception("Database error")
