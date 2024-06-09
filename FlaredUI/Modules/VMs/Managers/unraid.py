from flask import requests
from FlaredUI.Modules.Errors import UnraidError, VMNotFoundError
from FlaredUI.Logging import get_logger


logger = get_logger(__name__)


def get_unraid_vm_info(server, vm_name, ssh_client=None):
    """Fetches detailed information about a VMs on Unraid (assuming KVM/libvirt)."""

    try:
        # Construct API URL (adjust the endpoint based on your Unraid and virtualization setup)
        api_url = f"https://{server.hostname}/Dashboard.htm?action=getVMInfo&name={vm_name}"

        # Authentication (if needed)
        auth = (server.username, server.password) if server.username and server.password else None

        # Make API call
        response = requests.get(api_url, auth=auth, verify=False)  # Consider using verify=True in production
        response.raise_for_status()

        vm_data = response.json()  # Assuming the API returns JSON

        if not vm_data or vm_data.get('state') == 'STOPPED':
            raise VMNotFoundError(f"VMs '{vm_name}' not found or stopped on Unraid server.")

        # Filter and format relevant information (adjust as needed)
        vm_info = {
            'name': vm_name,
            'state': vm_data.get('state', 'unknown'),
            'cpu_cores': vm_data.get('cpus', 0),
            'memory': vm_data.get('mem', 0),  # Convert to MB if needed
            'os_type': vm_data.get('template', 'unknown'),  # Might be the template used to create the VMs
            'os_name': 'unknown',  # You'll need to fetch this from the VMs itself
            'os_version': 'unknown',  # You'll need to fetch this from the VMs itself
            'labels': None,
        }

        # TODO: Fetch IP address(es) of the VMs (not directly available in Unraid API)
        #       - Might need to SSH into Unraid and run commands like `virsh domifaddr <vm_name>`
        #       - Or, if the VMs is accessible, could likely ping/probe it directly to get the IP

        return vm_info

    except requests.exceptions.RequestException as e:

        logger.error(f"Error getting Unraid VMs info: {e}")
        raise UnraidError(f"Error communicating with Unraid API: {e}")


def list_unraid_vms(server, ssh_client=None):
    """Retrieves a list of all VMs on Unraid."""
    try:
        # Construct API URL (adjust the endpoint based on your Unraid and virtualization setup)
        api_url = f"https://{server.hostname}/Dashboard.htm?action=getVMList"

        # Authentication (same as in get_unraid_vm_info)
        auth = (server.username, server.password) if server.username and server.password else None

        # Make API call
        response = requests.get(api_url, auth=auth, verify=False)
        response.raise_for_status()

        vms_data = response.json()  # Assuming the API returns JSON

        filtered_data = []
        for vm in vms_data:
            filtered_data.append({
                'name': vm.get('name', ''),
                'state': vm.get('state', 'unknown'),
                'labels': None  # Unraid VMs don't have labels by default
            })

        return filtered_data

    except requests.exceptions.RequestException as e:

        logger.error(f"Error listing Unraid VMs: {e}")
        raise UnraidError(f"Error communicating with Unraid API: {e}")
