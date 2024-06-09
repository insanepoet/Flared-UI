from proxmoxer import ProxmoxAPI
from FlaredUI.Modules.Errors import ProxmoxError, VMNotFoundError
from FlaredUI.Logging import get_logger


logger = get_logger(__name__)


def get_proxmox_vm_info(server, vm_id, ssh_client=None):
    """Fetches detailed information about a VMs on a Proxmox server."""
    try:
        # Connect to Proxmox API (adjust verify_ssl for production)
        proxmox = ProxmoxAPI(server.hostname, user=f"{server.username}@pam", password=server.password, verify_ssl=False)

        # Get VMs details
        vm = proxmox.nodes(server.name).qemu(vm_id).status.current.get()

        if not vm:
            raise VMNotFoundError(f"VMs with ID '{vm_id}' not found on Proxmox server '{server.name}'.")

        # Extract and format relevant information
        vm_info = {
            'name': vm['name'],
            'guest_os_id': None,  # Proxmox doesn't have a direct guest OS ID equivalent
            'os_type': vm.get('os', 'unknown'),
            'cpu_cores': vm['cpus'],
            'memory': vm['maxmem'] // (1024 * 1024),  # Convert bytes to MB
            'state': vm['status'],
            'labels': None,  # Handle labels if needed
            # 'ip_addresses': [],  # You'll need to add logic to fetch IP addresses
            # ... (Add other fields as needed)
        }
        return vm_info
    except Exception as e:  # Consider using more specific Proxmox exceptions

        logger.error(f"Error getting Proxmox VMs info: {e}")
        raise ProxmoxError(f"Error retrieving VMs information from Proxmox: {e}")


def list_proxmox_vms(server, ssh_client=None):
    """Retrieves a list of all VMs on the Proxmox server."""
    try:
        # Connect to Proxmox API (same as in get_proxmox_vm_info)
        proxmox = ProxmoxAPI(server.hostname, user=f"{server.username}@pam", password=server.password, verify_ssl=False)

        # Get all VMs from the node
        vms = proxmox.nodes(server.name).qemu.get()

        filtered_data = []
        for vm in vms:
            vm_status = proxmox.nodes(server.name).qemu(vm['vmid']).status.current.get()
            filtered_data.append({
                'vmid': vm['vmid'],
                'name': vm['name'],
                'status': vm_status['status']
            })

        return filtered_data

    except Exception as e:

        logger.error(f"Error listing Proxmox VMs: {e}")
        raise ProxmoxError(f"Error retrieving VMs list from Proxmox: {e}")
