from kubernetes import client, config
import json
from FlaredUI.Modules.DB import create_container, update_container
from FlaredUI.Modules.Errors import KubectlError
from FlaredUI.Logging import get_logger

logger = get_logger(__name__)

DEFAULT_NAMESPACE = "default"  # Default namespace if none is provided


def get_kubernetes_container_info(server, container_name, ssh_client=None):
    """Fetches detailed information about a Kubernetes pod and its container."""

    try:
        # Load Kubernetes configuration based on connection type
        if ssh_client:
            kubeconfig_path = "/path/to/kubeconfig"
            config.load_kube_config(config_file=kubeconfig_path)
        else:
            config.load_incluster_config()  # Assuming running inside a Kubernetes pod

        v1 = client.CoreV1Api()
        namespace = server.namespace if server.namespace else DEFAULT_NAMESPACE

        # Find the pod containing the container (use the namespace from the server)
        pods = v1.list_namespaced_pod(namespace, label_selector=f"app={container_name}").items
        if not pods:
            raise KubectlError(f"Kubernetes pod with label 'app={container_name}' not found in namespace '{namespace}'.")

        pod = pods[0]  # Assuming only one pod matches the label
        container_status = next(
            (c for c in pod.status.container_statuses if c.name == container_name), None
        )
        if not container_status:
            raise KubectlError(f"Container '{container_name}' not found in pod '{pod.metadata.name}'.")

        # Extract and format container information
        filtered_data = {
            "name": container_name,
            "image": container_status.image,
            "state": container_status.state.running.started_at if container_status.state.running else "Terminated",  # Handle terminated state
            "exposed_ports": {
                str(p.container_port): None for p in pod.spec.containers[0].ports
            },  # Kubernetes doesn't expose host ports directly
            "labels": pod.metadata.labels,
            # ... (Add other fields as needed)
        }

        return filtered_data

    except KubectlError as e:
        logger.error(f"Kubernetes API error: {e}")
        raise # Re-raise the exception after logging
    except Exception as e:
        logger.error(f"Error getting Kubernetes container info: {e}")
        raise  # Re-raise the exception after logging


def list_kubernetes_containers(server, ssh_client=None):
    """Retrieves a list of all Kubernetes pods and their containers."""
    try:
        # Load Kubernetes configuration (same as in get_kubernetes_container_info)
        if ssh_client:
            kubeconfig_path = "/path/to/kubeconfig"  # Adjust path if needed
            config.load_kube_config(config_file=kubeconfig_path)  # Use config_file for explicit path
        else:
            config.load_incluster_config()  # Assuming running inside a Kubernetes pod

        v1 = client.CoreV1Api()

        # Use the server's namespace if available, otherwise use the default
        namespace = server.namespace if server.namespace else DEFAULT_NAMESPACE
        pods = v1.list_namespaced_pod(namespace).items if namespace else v1.list_pod_for_all_namespaces().items

        filtered_data = []
        for pod in pods:
            for container in pod.spec.containers:
                container_status = next((c for c in pod.status.container_statuses if c.name == container.name), None)
                if container_status:
                    filtered_data.append(
                        {
                            "name": container.name,
                            "image": container.image,
                            "state": container_status.state.running.started_at
                            if container_status.state.running
                            else "Terminated",
                            "labels": pod.metadata.labels,
                        }
                    )
        return filtered_data

    except Exception as e:
        logger.error(f"Error listing Kubernetes containers: {e}")
        raise
