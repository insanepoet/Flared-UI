from FlaredUI.Modules.DB import db, ContainerManagement, VMManagement, ContainerManagementSchema, VMManagementSchema
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from marshmallow import ValidationError
from cachetools import cached, TTLCache
from FlaredUI.Logging import get_logger


logger = get_logger(__name__)


# Predefined manager names
CONTAINER_MANAGERS = ["docker", "podman", "kubernetes", "truenas", "unraid"]
VM_MANAGERS = ["esxi", "nutanix", "openstack", "proxmox", "truenas", "unraid", "xcp", "xen"]


@cached(cache=TTLCache(maxsize=1024, ttl=300))
def get_container_managers():
    """Retrieves all available container managers from the database."""
    try:
        return ContainerManagement.query.all()
    except SQLAlchemyError as e:

        logger.error(f"Database error getting container managers: {e}")
        raise Exception("Database error.")


@cached(cache=TTLCache(maxsize=1024, ttl=300))
def get_vm_managers():
    """Retrieves all available VMs managers from the database."""
    try:
        return VMManagement.query.all()
    except SQLAlchemyError as e:

        logger.error(f"Database error getting VMs managers: {e}")
        raise Exception("Database error.")


def create_container_managers():
    """Creates the predefined container manager entries in the database."""

    try:
        for name in CONTAINER_MANAGERS:
            data = {'name': name}
            ContainerManagementSchema().load(data)  # Validate data before creation
            manager = ContainerManagement(**data)
            db.session.add(manager)
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        logger.warning("Container managers already exist. Skipping creation.")
    except SQLAlchemyError as e:
        db.session.rollback()
        logger.error(f"Database error creating container managers: {e}")
        raise Exception("Database error creating container managers.")
    except ValidationError as err:
        db.session.rollback()
        logger.error(f"Validation error creating container manager: {err.messages}")
        raise ValueError(err.messages)


def create_vm_managers():
    """Creates the predefined VMs manager entries in the database."""

    try:
        for name in VM_MANAGERS:
            data = {'name': name}
            VMManagementSchema().load(data)  # Validate data before creation
            manager = VMManagement(**data)
            db.session.add(manager)
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        logger.warning("VMs managers already exist. Skipping creation.")
    except SQLAlchemyError as e:
        db.session.rollback()
        logger.error(f"Database error creating VMs managers: {e}")
        raise Exception("Database error creating VMs managers.")
    except ValidationError as err:
        db.session.rollback()
        logger.error(f"Validation error creating VMs manager: {err.messages}")
        raise ValueError(err.messages)


def add_manager(manager_type, data):
    """Adds a new container or VMs manager to the database."""

    try:
        if manager_type == "container":
            ContainerManagementSchema().load(data)
            manager = ContainerManagement(**data)
        elif manager_type == "vm":
            VMManagementSchema().load(data)
            manager = VMManagement(**data)
        else:
            raise ValueError("Invalid manager type. Must be 'container' or 'vm'.")

        db.session.add(manager)
        db.session.commit()
        return manager
    except IntegrityError as e:
        db.session.rollback()
        raise ValueError(f"Manager with name '{data['name']}' already exists.") from e
    except SQLAlchemyError as e:
        logger.error(f"Database error creating manager: {e}")
        db.session.rollback()
        raise Exception("Database error creating manager.")
    except ValidationError as err:
        db.session.rollback()
        logger.error(f"Validation error creating manager: {err.messages}")
        raise ValueError(err.messages)