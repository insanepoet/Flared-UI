import requests
import json

from FlaredUI.Modules.DB import create_container, update_container
from FlaredUI.Modules.Errors import UnraidError
from FlaredUI.Logging import get_logger

logger = get_logger(__name__)

UNRAID_API_ENDPOINT = "/usr/local/emhttp/plugins/dynamix.docker.manager/include/DockerClient.php"


def get_unraid_container_info(server, container_name, ssh_client=None):
    """Fetches detailed information about a container in Unraid's Docker."""
    try:
        # Construct API URL
        api_url = f"https://{server.hostname}{UNRAID_API_ENDPOINT}?action=getContainer&container={container_name}"

        # Authentication (if needed)
        auth = (server.username,
                server.password) if server.username and server.password else None  # Decrypt password here if encrypted

        # Make API call
        response = requests.get(api_url, auth=auth, verify=False)
        response.raise_for_status()

        container_data = response.json()

        # Check for errors in the API response
        if 'error' in container_data:
            raise UnraidError(container_data['error'])

        if not container_data:
            raise UnraidError(f"Unraid container '{container_name}' not found.")

        # Filter and format relevant information (adjust as needed)
        filtered_data = {
            "name": container_data.get("Name", ""),
            "image": container_data.get("Image", ""),
            "state": container_data.get("State", ""),
            "exposed_ports": {
                port["PrivatePort"]: port["PublicPort"]
                for port in container_data.get("Ports", [])
                if "PrivatePort" in port and "PublicPort" in port
            },
            "labels": container_data.get("Labels", {}),
            # ... (Add other fields as needed)
        }
        return filtered_data

    except requests.exceptions.RequestException as e:
        logger.error(f"Error getting Unraid container info: {e}")
        raise UnraidError(f"Error communicating with Unraid Docker API: {e}")


def list_unraid_containers(server, ssh_client=None):
    """Retrieves a list of all containers on Unraid."""
    try:
        # Construct API URL
        api_url = f"https://{server.hostname}{UNRAID_API_ENDPOINT}?action=getContainers"

        # Authentication (same as in get_unraid_container_info)
        auth = (server.username, server.password) if server.username and server.password else None

        # Make API call
        response = requests.get(api_url, auth=auth, verify=False)
        response.raise_for_status()

        containers_data = response.json()

        # Check for errors in the API response
        if 'error' in containers_data:
            raise UnraidError(containers_data['error'])

        filtered_data = []
        for container in containers_data:
            filtered_data.append({
                'name': container.get('Name', ''),
                'image': container.get('Image', ''),
                'state': container.get('State', ''),
                'labels': container.get('Labels', {}),
            })

        return filtered_data

    except requests.exceptions.RequestException as e:
        logger.error(f"Error listing Unraid containers: {e}")
        raise UnraidError(f"Error communicating with Unraid Docker API: {e}")
