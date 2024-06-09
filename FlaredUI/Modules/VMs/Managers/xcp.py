import XenAPI
from FlaredUI.Modules.Errors import XCPError, VMNotFoundError
from FlaredUI.Logging import get_logger


logger = get_logger(__name__)


def get_xcp_vm_info(server, vm_name, ssh_client=None):
    """Fetches detailed information about a VMs on an XCP-ng host."""

    try:
        # Connect to XCP-ng using XenAPI
        session = XenAPI.Session(f"https://{server.hostname}")
        session.login_with_password(server.username, server.password)

        # Find the VMs by name
        vms = session.xenapi.VM.get_by_name_label(vm_name)
        if not vms:
            raise VMNotFoundError(f"VMs '{vm_name}' not found on XCP-ng host '{server.hostname}'.")

        vm_ref = vms[0]  # Assuming only one VMs with this name exists

        # Get VMs record (detailed information)
        vm_record = session.xenapi.VM.get_record(vm_ref)

        # Extract relevant information (adjust fields as needed)
        vm_info = {
            'name': vm_record['name_label'],
            'guest_os_id': None,  # XCP-ng doesn't provide a standard guest OS ID
            'os_type': vm_record.get('os_version', {}).get('name', 'unknown'),  # Attempt to get OS info
            'cpu_cores': vm_record['VCPUs_max'],
            'memory': vm_record['memory_dynamic_max'] // (1024 * 1024),  # Convert bytes to MB
            'state': vm_record['power_state'],
            'ip_addresses': [],  # Add logic to fetch IP addresses (e.g., from guest metrics)
            'labels': None,  # No direct label support in XCP-ng VMs
            # ... (Add other fields as needed)
        }

        # TODO: Fetch IP address(es) of the VMs (not directly available in the VMs record)
        #       - You might need to use XenAPI calls to get network interface info and then fetch IP addresses

        session.xenapi.session.logout()  # Close the session
        return vm_info

    except XenAPI.Failure as e:
        logger.error(f"XCP-ng Error: {e}")
        raise XCPError(f"Error retrieving VMs information from XCP-ng: {e}")
    except Exception as e:  # Catch any unexpected errors
        logger.error(f"Error getting XCP-ng VMs info: {e}")
        raise XCPError(f"Error retrieving VMs information from XCP-ng: {e}")


def list_xcp_vms(server, ssh_client=None):
    """Retrieves a list of all VMs on the XCP-ng server."""

    try:
        # Connect to XCP-ng (same as in get_xcp_vm_info)
        session = XenAPI.Session(f"https://{server.hostname}")
        session.login_with_password(server.username, server.password)

        # Get all VMs records
        vm_records = session.xenapi.VM.get_all_records()

        filtered_data = []
        for vm_ref, vm_record in vm_records.items():
            filtered_data.append({
                'vmid': vm_record['uuid'],  # VMs UUID in XCP-ng
                'name': vm_record['name_label'],
                'os_type': vm_record.get('os_version', {}).get('name', 'unknown'),  # Attempt to get OS info
                'state': vm_record['power_state'],
                'labels': None
            })

        session.xenapi.session.logout()
        return filtered_data

    except XenAPI.Failure as e:
        logger.error(f"XCP-ng Error: {e}")
        raise XCPError(f"Error listing VMs on XCP-ng: {e}")
    except Exception as e:
        logger.error(f"Error listing XCP-ng VMs: {e}")
        raise XCPError(f"Error listing VMs on XCP-ng: {e}")
