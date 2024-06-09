from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from marshmallow import ValidationError
from cachetools import cached, TTLCache
from FlaredUI.Modules.DB import (
    db, ContainerSchema, VMSchema,
    Container, VM, Servers
)
from FlaredUI.Logging import get_logger


logger = get_logger(__name__)


# --- Container-related functions ---
def create_container(data):
    try:
        ContainerSchema().load(data)

        # Ensure server_id is valid
        server = Servers.get_server_by_id(data['server_id'])
        if not server:
            raise ValueError(f"Server with ID {data['server_id']} not found.")

        container = Container(**data)
        db.session.add(container)
        db.session.commit()
        return container
    except ValidationError as err:

        logger.error(f"Validation error creating container: {err.messages}")
        raise ValueError(err.messages)
    except IntegrityError:
        db.session.rollback()
        raise ValueError("Container name already exists on this server.")
    except SQLAlchemyError as e:
        db.session.rollback()

        logger.error(f"Database error creating container: {e}")
        raise Exception("Database error")


@cached(cache=TTLCache(maxsize=1024, ttl=300))
def get_all_containers():
    """Retrieves all containers."""
    try:
        return Container.query.all()
    except SQLAlchemyError as e:

        logger.error(f"Database error: {e}")
        raise Exception("Database error")


@cached(cache=TTLCache(maxsize=1024, ttl=300))
def get_container_by_id(container_id):
    """Retrieves a container by its ID."""
    try:
        container = Container.query.get(container_id)
        if not container:
            raise ValueError("Container not found")
        return container
    except SQLAlchemyError as e:

        logger.error(f"Database error: {e}")
        raise Exception("Database error")


@cached(cache=TTLCache(maxsize=1024, ttl=300))
def get_containers_by_server(server_id):
    """Retrieves all containers associated with a specific server."""
    try:
        return Container.query.filter_by(server_id=server_id).all()
    except SQLAlchemyError as e:

        logger.error(f"Database error: {e}")
        raise Exception("Database error")


@cached(cache=TTLCache(maxsize=1024, ttl=300))
def get_container_by_name_and_server(name, server_id):
    """Retrieves a container by its name and server ID."""
    try:
        return Container.query.filter_by(name=name, server_id=server_id).first()
    except SQLAlchemyError as e:

        logger.error(f"Database error: {e}")
        raise Exception("Database error")


def update_container(container_id, data):
    try:
        ContainerSchema(exclude=["name", "server_id"]).load(data)  # Exclude non-updatable fields
    except ValidationError as err:

        logger.error(f"Validation error updating container: {err.messages}")
        raise ValueError(err.messages)

    try:
        container = get_container_by_id(container_id)
        if not container:
            raise ValueError("Container not found")

        for key, value in data.items():
            setattr(container, key, value)
        db.session.commit()
        return container
    except SQLAlchemyError as e:
        db.session.rollback()

        logger.error(f"Database error updating container: {e}")
        raise Exception("Database error")


def delete_container(container_id):
    """Deletes a container."""
    try:
        container = get_container_by_id(container_id)
        if container:
            db.session.delete(container)
            db.session.commit()
        return container
    except SQLAlchemyError as e:

        logger.error(f"Database error: {e}")
        raise Exception("Database error")


# --- VMs-related functions ---

def create_vm(data):
    try:
        VMSchema().load(data)
        server = Servers.get_server_by_id(data['server_id'])  # Get server using Servers module
        if not server:
            raise ValueError(f"Server with ID {data['server_id']} not found.")
        vm = VM(**data)
        db.session.add(vm)
        db.session.commit()
        return vm
    except ValidationError as err:

        logger.error(f"Validation error creating VMs: {err.messages}")
        raise ValueError(err.messages)
    except IntegrityError:
        db.session.rollback()
        raise ValueError("VMs name already exists on this server.")
    except SQLAlchemyError as e:
        db.session.rollback()

        logger.error(f"Database error creating VMs: {e}")
        raise Exception("Database error")


@cached(cache=TTLCache(maxsize=1024, ttl=300))
def get_all_vms():
    """Retrieves all virtual machines."""
    try:
        return VM.query.all()
    except SQLAlchemyError as e:

        logger.error(f"Database error: {e}")
        raise Exception("Database error")


@cached(cache=TTLCache(maxsize=1024, ttl=300))
def get_vm_by_id(vm_id):
    """Retrieves a virtual machine by its ID."""
    try:
        vm = VM.query.get(vm_id)
        if not vm:
            raise ValueError("VMs not found")
        return vm
    except SQLAlchemyError as e:

        logger.error(f"Database error: {e}")
        raise Exception("Database error")


@cached(cache=TTLCache(maxsize=1024, ttl=300))
def get_vms_by_server(server_id):
    """Retrieves all virtual machines associated with a specific server."""
    try:
        return VM.query.filter_by(server_id=server_id).all()
    except SQLAlchemyError as e:

        logger.error(f"Database error: {e}")
        raise Exception("Database error")


@cached(cache=TTLCache(maxsize=1024, ttl=300))
def get_vm_by_name_and_server(name, server_id):
    """Retrieves a VMs by its name and server ID."""
    try:
        return VM.query.filter_by(name=name, server_id=server_id).first()
    except SQLAlchemyError as e:

        logger.error(f"Database error: {e}")
        raise Exception("Database error")


def update_vm(vm_id, data):
    try:
        VMSchema(exclude=["name", "server_id"]).load(data)  # Exclude non-updatable fields
    except ValidationError as err:

        logger.error(f"Validation error updating VMs: {err.messages}")
        raise ValueError(err.messages)

    try:
        vm = get_vm_by_id(vm_id)
        if not vm:
            raise ValueError("VMs not found")

        for key, value in data.items():
            setattr(vm, key, value)
        db.session.commit()
        return vm
    except SQLAlchemyError as e:
        db.session.rollback()

        logger.error(f"Database error updating VMs: {e}")
        raise Exception("Database error")


def delete_vm(vm_id):
    """Deletes a virtual machine."""
    try:
        vm = get_vm_by_id(vm_id)
        if vm:
            db.session.delete(vm)
            db.session.commit()
        return vm
    except SQLAlchemyError as e:

        logger.error(f"Database error: {e}")
        raise Exception("Database error")
