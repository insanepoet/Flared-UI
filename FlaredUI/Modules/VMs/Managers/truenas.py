from flask import requests
from urllib3.exceptions import InsecureRequestWarning
from FlaredUI.Modules.Errors import TrueNASVMError
from FlaredUI.Logging import get_logger


logger = get_logger(__name__)

requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)


# --- TrueNAS VMs Functions ---

def get_truenas_vm_info(server, vm_name, ssh_client=None):
    """Fetches detailed information about a VMs on TrueNAS."""
    try:
        # Fetch TrueNAS API key from server
        api_key = server.password

        # Construct API URL
        api_url = f"https://{server.hostname}/api/v2.0/vm/id/{vm_name}"  # Use /vm endpoint
        headers = {
            "Authorization": f"Bearer {api_key}"
        }

        # Make API call to get VMs information
        response = requests.get(api_url, headers=headers, verify=False)
        response.raise_for_status()
        vm_data = response.json()

        if vm_data:
            # Extract relevant information (adjust as needed)
            vm_info = {
                'name': vm_data['name'],
                'os_type': vm_data['description'],  # TrueNAS doesn't provide detailed OS info
                'cpu_cores': vm_data['vcpus'],
                'memory': vm_data['memory'],
                'state': vm_data['status']['state'],  # Extract state from nested dict
                'labels': None,  # No direct labels in TrueNAS VMs
            }

            # Try to get IP addresses (not always available)
            try:
                vm_info['ip_addresses'] = [
                    vm_data['devices'][0]['attributes']['mac']]  # Assuming first device is the NIC
            except (KeyError, IndexError):
                vm_info['ip_addresses'] = []

            return vm_info
        else:
            raise TrueNASVMError(f"TrueNAS VMs '{vm_name}' not found.")

    except requests.exceptions.RequestException as e:

        logger.error(f"Error getting TrueNAS VMs info: {e}")
        raise TrueNASVMError(f"Error communicating with TrueNAS API: {e}")


def list_truenas_vms(server, ssh_client=None):
    """Retrieves a list of all VMs on TrueNAS."""
    try:
        # Fetch TrueNAS API key from server
        api_key = server.password

        # Construct API URL
        api_url = f"https://{server.hostname}/api/v2.0/vm/"  # Use /vm endpoint
        headers = {
            "Authorization": f"Bearer {api_key}"
        }

        # Make API call to get all VMs
        response = requests.get(api_url, headers=headers, verify=False)
        response.raise_for_status()
        vms_data = response.json()

        filtered_data = []
        for vm in vms_data:
            filtered_data.append({
                'name': vm['name'],
                'os_type': vm['description'],  # TrueNAS doesn't provide detailed OS info
                'state': vm['status']['state'],  # Extract state from nested dict
                'labels': None,
            })

        return filtered_data

    except requests.exceptions.RequestException as e:

        logger.error(f"Error listing TrueNAS VMs: {e}")
        raise TrueNASVMError(f"Error communicating with TrueNAS API: {e}")

