import docker
import json


def get_docker_container_info(server, container_name, ssh_client=None):
    """Fetches detailed information about a Docker container."""
    try:
        if ssh_client:
            # Execute docker inspect command over SSH
            _, stdout, stderr = ssh_client.exec_command(f"docker inspect {container_name}")
            if stderr:
                raise Exception(f"Error inspecting container: {stderr.read().decode()}")
            container_data = json.loads(stdout.read().decode())[0]
        else:
            # Local Docker connection
            client = docker.from_env()
            container = client.containers.get(container_name)
            container_data = container.attrs

        # Filter and format relevant container information (adjust based on your needs)
        filtered_data = {
            'name': container_data['Name'][1:],  # Remove the leading '/'
            'image': container_data['Config']['Image'],
            'state': container_data['State']['Status'],
            'exposed_ports': {port: bindings[0]['HostPort']
                              for port, bindings in container_data['HostConfig']['PortBindings'].items() if bindings},
            'labels': container_data['Config']['Labels'],
            # ... (Add other fields as needed)
        }

        return filtered_data

    except docker.errors.NotFound:
        raise ValueError(f"Docker container '{container_name}' not found.")
    except Exception as e:
        app.logger.error(f"Error getting Docker container info: {e}")
        raise


def list_docker_containers(server, ssh_client=None):
    """Retrieves a list of all Docker containers on the specified server."""
    try:
        if ssh_client:
            # Execute docker ps command over SSH
            _, stdout, stderr = ssh_client.exec_command("docker ps --format '{{json .}}'")
            if stderr:
                raise Exception(f"Error listing containers: {stderr.read().decode()}")
            containers_data = [json.loads(line) for line in stdout.readlines()]

        else:
            # Local Docker connection
            client = docker.from_env()
            containers = client.containers.list(all=True)  # Get all containers (running and stopped)
            containers_data = [container.attrs for container in containers]

        # Filter and format container information
        filtered_containers = []
        for container_data in containers_data:
            filtered_containers.append({
                'name': container_data['Name'][1:],
                'image': container_data['Config']['Image'],
                'state': container_data['State']['Status'],
                'labels': container_data['Config']['Labels']
            })

        return filtered_containers

    except Exception as e:
        app.logger.error(f"Error listing Docker containers: {e}")
        raise
