import openstack
from FlaredUI.Modules.Errors import OpenstackError, VMNotFoundError
from FlaredUI.Logging import get_logger


logger = get_logger(__name__)


def get_openstack_vm_info(server, vm_name, ssh_client=None):
    """Fetches detailed information about a VMs on OpenStack."""
    try:
        # Connect to OpenStack (adjust for your authentication method)
        conn = openstack.connect(
            auth_url=server.hostname,
            project_name=server.project_name,  # You might need to store project name in your Server model
            username=server.username,
            password=server.password,
            # ... other authentication parameters
        )

        # Find the VMs by name
        vm = conn.compute.find_server(vm_name)
        if not vm:
            raise VMNotFoundError(f"VMs '{vm_name}' not found on OpenStack '{server.hostname}'.")

        # Extract and format relevant information (adjust fields as needed)
        vm_info = {
            'name': vm.name,
            'guest_os_id': vm.image['id'],  # OpenStack image ID
            'os_type': vm.flavor['name'],  # OpenStack flavor name might give some OS info
            'cpu_cores': vm.flavor['vcpus'],
            'memory': vm.flavor['ram'],
            'state': vm.status,
            'ip_addresses': [addr['addr'] for addr in vm.addresses.values() for addr in addr if
                             addr['OS-EXT-IPS:type'] == 'floating'],  # Extract floating IPs
            'labels': None,  # OpenStack doesn't use labels in the same way as Docker
            # ... (Add other fields as needed)
        }

        return vm_info

    except openstack.exceptions.ResourceNotFound as e:
        raise VMNotFoundError(f"VMs '{vm_name}' not found on OpenStack '{server.hostname}'.")
    except Exception as e:  # Consider using more specific OpenStack exceptions

        logger.error(f"Error getting OpenStack VMs info: {e}")
        raise OpenstackError(f"Error retrieving VMs information from OpenStack: {e}")


def list_openstack_vms(server, ssh_client=None):
    """Retrieves a list of all VMs on the OpenStack server."""

    try:
        # Connect to OpenStack (same as in get_openstack_vm_info)
        conn = openstack.connect(
            auth_url=server.hostname,
            project_name=server.project_name,  # You might need to store project name in your Server model
            username=server.username,
            password=server.password,
            # ... other authentication parameters
        )

        # Get all servers (VMs)
        vms = list(conn.compute.servers())

        filtered_data = []
        for vm in vms:
            filtered_data.append({
                'id': vm.id,
                'name': vm.name,
                'status': vm.status,
                'image_id': vm.image['id'],
                'flavor_name': vm.flavor['name'],
            })

        return filtered_data

    except Exception as e:

        logger.error(f"Error listing OpenStack VMs: {e}")
        raise OpenstackError(f"Error retrieving VMs list from OpenStack: {e}")
