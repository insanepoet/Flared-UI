import json
import logging
from FlaredUI.Modules.DB import db, get_server_by_id, get_container_by_name_and_server, create_container, update_container
from FlaredUI.Modules.Errors import ContainerNotFound, SSHConnectionError, NotImplementedError, ContainerRetrievalError, ContainerUpdateError, ContainerManagerNotSupportedError
from FlaredUI.Modules.Containers.Managers import *

logger = logging.getLogger(__name__)

def get_container_info(server, container_name, ssh_client=None):
    """Fetches detailed information about a container from a given server."""
    try:
        logger.debug(f"Fetching container info for {container_name} on {server.name}")

        # Ensure container exists in the database
        container_obj = get_container_by_name_and_server(container_name, server.id)
        if not container_obj:
            raise ContainerNotFound(f"Container '{container_name}' not found in the database.")

        # Dynamically determine and call the appropriate function based on container manager type
        manager_name = server.container_manager.name.lower()
        function_name = f"get_{manager_name}_container_info"
        try:
            container_info_function = globals()[function_name]
        except KeyError:
            raise ContainerManagerNotSupportedError(f"Support for container manager '{manager_name}' not implemented.")

        # Fetch container info using the appropriate function
        try:
            if ssh_client:
                container_info = container_info_function(server, container_name, ssh_client=ssh_client)
            else:
                container_info = container_info_function(server, container_name)
            logger.debug(f"Successfully retrieved container info for {container_name} on {server.name}")
            return container_info
        except ContainerNotFound as e:
            raise ContainerRetrievalError(str(e)) from e  # Chain the original exception
        except Exception as e:  # Catch-all for unexpected errors during retrieval
            logger.error(f"Unexpected error getting container info: {e}")
            raise ContainerRetrievalError("An unexpected error occurred while retrieving container information.") from e

    except (ContainerNotFound, ContainerManagerNotSupportedError) as e:
        raise  # Re-raise these specific exceptions to be handled higher up

    except Exception as e:  # Catch-all for any other unhandled exception
        logger.exception("An unexpected error occurred in get_container_info:")  # Log the exception with traceback
        raise ContainerRetrievalError("An unexpected error occurred while retrieving container information.") from e



def list_containers(server, ssh_client=None):
    """Retrieves a list of all containers on the specified server."""
    try:
        logger.debug(f"Listing containers on {server.name}")

        # Get container manager from server
        container_manager = server.container_manager
        if container_manager is None:
            raise ValueError(f"No container manager defined for server '{server.name}'")

        manager_name = container_manager.name.lower()
        function_name = f"list_{manager_name}_containers"

        try:
            container_list_function = globals()[function_name]
        except KeyError:
            raise ContainerManagerNotSupportedError(f"Support for container manager '{manager_name}' not implemented.")

        try:
            if ssh_client:
                containers_data = container_list_function(server, ssh_client=ssh_client)
            else:
                containers_data = container_list_function(server)

            # Add information from the database to each container
            for container_data in containers_data:
                container_obj = get_container_by_name_and_server(container_data['name'], server.id)
                if container_obj:
                    container_data['enabled'] = container_obj.enabled
                    container_data['hostname'] = container_obj.hostname

                    if container_obj.applications:
                        container_data['tunnel_ids'] = [app.tunnel_id for app in container_obj.applications if app.tunnel_id]
                    else:
                        container_data['tunnel_ids'] = []

            logger.debug(f"Successfully retrieved list of containers on {server.name}")
            return containers_data
        except ContainerNotFound as e:
            raise ContainerRetrievalError(str(e))
        except Exception as e:  # Catch-all for unexpected errors during retrieval
            logger.error(f"Unexpected error listing container info: {e}")
            raise ContainerRetrievalError("An unexpected error occurred while retrieving container information.") from e

    except (ContainerNotFound, ContainerManagerNotSupportedError) as e:
        raise # Re-raise these specific exceptions to be handled higher up

    except Exception as e:  # Catch-all for any other unhandled exception
        logger.exception("An unexpected error occurred in list_containers:") # Log the exception with traceback
        raise ContainerRetrievalError("An unexpected error occurred while retrieving container information.") from e


def update_container_db(server, container_info):
    """Updates or creates a Container entry in the database."""
    try:
        logger.debug(f"Updating container info in DB for: {container_info['name']}")

        container = get_container_by_name_and_server(container_info['name'], server.id)

        if container:
            # Update existing container
            update_container(container.id, **container_info)
            logger.debug(f"Updated container info in DB for: {container_info['name']}")
        else:
            # Create a new container
            create_container(**container_info, server_id=server.id)
            logger.debug(f"Created container info in DB for: {container_info['name']}")

        db.session.commit()

    except Exception as e:
        app.logger.error(f"Database update failed: {e}")
        db.session.rollback()
        raise ContainerUpdateError("Database error updating container.")