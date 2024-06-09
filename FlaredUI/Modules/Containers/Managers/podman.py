import podman
import json

from FlaredUI.Modules.DB import create_container, update_container
from FlaredUI.Modules.Errors import PodmanError


def get_podman_container_info(server, container_name, ssh_client=None):
    """Fetches detailed information about a Podman container."""
    try:
        if ssh_client:
            # Execute podman inspect command over SSH (adjust path if needed)
            _, stdout, stderr = ssh_client.exec_command(f"podman inspect {container_name}")
            if stderr:
                raise PodmanError(f"Error inspecting container over SSH: {stderr.read().decode()}")
            container_data = json.loads(stdout.read().decode())[0]
        else:
            # Local Podman connection (using Podman API)
            with podman.PodmanClient() as client:
                try:
                    container = client.containers.get(container_name)
                except podman.errors.NotFound as e:
                    raise PodmanError(f"Podman container '{container_name}' not found.") from e
                container_data = container.attrs

        # Filter and format relevant container information
        filtered_data = {
            'name': container_data['Name'][1:],  # Remove leading '/'
            'image': container_data['ImageName'],
            'state': container_data['State'],
            'exposed_ports': {
                str(port['container_port']): port.get('host_port')
                for port in container_data.get('Ports', [])
                if port.get('protocol') == 'tcp'
            },
            'labels': container_data.get('Labels', {}),
            # ... (Add other fields as needed)
        }
        return filtered_data

    except (podman.errors.ErrorOccurred, podman.errors.APIError) as e:  # Catch podman errors
        app.logger.error(f"Podman Error: {e}")
        raise PodmanError(f"Podman error: {e}")
    except Exception as e:
        app.logger.error(f"Error getting Podman container info: {e}")
        raise  # Re-raise the exception after logging


def list_podman_containers(server, ssh_client=None):
    """Retrieves a list of all Podman containers on the specified server."""
    try:
        if ssh_client:
            # Execute podman ps command over SSH
            _, stdout, stderr = ssh_client.exec_command("podman ps --format '{{json .}}'")  # Using JSON format
            if stderr:
                raise PodmanError(f"Error listing containers over SSH: {stderr.read().decode()}")
            container_data = [json.loads(line) for line in stdout.readlines()]
        else:
            # Local Podman connection (using Podman API)
            with podman.PodmanClient() as client:
                containers = client.containers.list(all=True)  # Get all containers (running and stopped)
                container_data = [container.attrs for container in containers]

        # Filter and format container information
        filtered_data = []
        for container in container_data:
            filtered_data.append({
                'name': container['Name'][1:],  # Remove leading '/'
                'image': container['ImageName'],
                'state': container['State'],
                'labels': container.get('Labels', {})
            })
        return filtered_data

    except (podman.errors.ErrorOccurred, podman.errors.APIError) as e:  # Catch podman errors
        app.logger.error(f"Podman Error: {e}")
        raise PodmanError(f"Podman error: {e}")
    except Exception as e:
        app.logger.error(f"Error listing Podman containers: {e}")
        raise
