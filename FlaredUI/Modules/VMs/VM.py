import json
from FlaredUI.Modules.DB import (
    db, get_server_by_id, create_vm, update_vm,
    get_vm_by_name_and_server, get_vm_by_id, get_container_by_name_and_server,
)
from FlaredUI.Modules.Errors import VMNotFoundError, SSHConnectionError, NotImplementedError
from FlaredUI.Modules.VMs.Managers import *
from cachetools import cached, TTLCache
from FlaredUI.Logging import get_logger


logger = get_logger(__name__)


# Error Classes (Add to errors.py)
class VMRetrievalError(Exception):
    pass


class VMUpdateError(Exception):
    pass


def get_vm_info(server, vm_name, ssh_client=None):
    """Fetches detailed information about a VMs from a given server."""
    try:
        logger.debug(f"Fetching VMs info for {vm_name} on {server.name}")

        # Ensure VMs exists in the database
        vm_obj = get_vm_by_id(vm_name, server.id)
        if not vm_obj:
            raise VMNotFoundError(f"VMs '{vm_name}' not found in the database.")

        # Dynamically determine and call the appropriate function based on VMs manager type
        manager_name = server.vm_manager.name.lower()
        function_name = f"get_{manager_name}_vm_info"

        try:
            vm_info_function = globals()[function_name]
        except KeyError:
            raise NotImplementedError(f"Support for VMs manager '{manager_name}' not implemented.")

        # Fetch VMs info using the appropriate function
        try:
            if ssh_client:
                vm_info = vm_info_function(server, vm_name, ssh_client=ssh_client)
            else:
                vm_info = vm_info_function(server, vm_name)
            logger.debug(f"Successfully retrieved VMs info for {vm_name} on {server.name}")
            return vm_info
        except VMNotFoundError as e:
            raise VMRetrievalError(str(e)) from e  # Chain the original exception
        except Exception as e:  # Catch-all for unexpected errors during retrieval
            logger.error(f"Unexpected error getting VMs info: {e}")
            raise VMRetrievalError("An unexpected error occurred while retrieving VMs information.") from e

    except (VMNotFoundError, NotImplementedError) as e:
        raise  # Re-raise these specific exceptions to be handled higher up

    except Exception as e:  # Catch-all for any other unhandled exception
        logger.exception("An unexpected error occurred in get_vm_info:")  # Log the exception with traceback
        raise VMRetrievalError("An unexpected error occurred while retrieving VMs information.") from e


@cached(cache=TTLCache(maxsize=1024, ttl=300))
def list_vms(server, ssh_client=None):
    """Retrieves a list of all VMs on the specified server."""
    try:
        logger.debug(f"Listing VMs on {server.name}")

        # Get container manager from server
        vm_manager = server.vm_manager
        if vm_manager is None:
            raise ValueError(f"No VMs manager defined for server '{server.name}'")

        manager_name = vm_manager.name.lower()
        function_name = f"list_{manager_name}_vms"

        try:
            vm_list_function = globals()[function_name]
        except KeyError:
            raise NotImplementedError(f"Support for VMs manager '{manager_name}' not implemented.")

        try:
            if ssh_client:
                vms_data = vm_list_function(server, ssh_client=ssh_client)
            else:
                vms_data = vm_list_function(server)

            # Add information from the database to each VMs
            for vm_data in vms_data:
                vm_obj = get_vm_by_id(vm_data['guest_os_id'], server.id)
                if vm_obj:
                    vm_data['enabled'] = vm_obj.enabled

                    if vm_obj.applications:  # If the container has applications
                        vm_data['tunnel_ids'] = [app.tunnel_id for app in vm_obj.applications if app.tunnel_id]
                        vm_data["hostname"] = [app.hostname for app in vm_obj.applications]
                        # Get all the applications for the vm
                    else:
                        vm_data['tunnel_ids'] = []
                        vm_data["hostname"] = []

            logger.debug(f"Successfully retrieved list of VMs on {server.name}")
            return vms_data
        except VMNotFoundError as e:
            raise VMRetrievalError(str(e))
        except Exception as e:
            logger.error(f"Unexpected error listing VMs info: {e}")
            raise VMRetrievalError("An unexpected error occurred while retrieving VMs information.") from e


    except (VMNotFoundError, NotImplementedError) as e:
        raise  # Re-raise these specific exceptions to be handled higher up

    except Exception as e:  # Catch-all for any other unhandled exception
        logger.exception("An unexpected error occurred in list_vms:")
        raise VMRetrievalError("An unexpected error occurred while retrieving VMs information.") from e


def update_vm_db(server, vm_info):
    """Updates or creates a VMs entry in the database."""

    logger.debug(f"Updating VMs info in DB for: {vm_info['name']}")

    try:
        # Search VMs by name and Server ID
        vm = get_vm_by_name_and_server(vm_info['name'], server.id)

        if vm:
            # Update existing VMs
            update_vm(vm.id, **vm_info)
        else:
            # Create a new VMs
            vm = create_vm(**vm_info, server_id=server.id)  # Update the VMs

        db.session.commit()

        get_vm_by_id.cache_clear()
        get_vm_by_name_and_server.cache_clear()

    except Exception as e:
        logger.error(f"Database update failed: {e}")
        db.session.rollback()
        raise VMUpdateError("Database error updating VMs.")