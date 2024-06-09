import XenAPI
from FlaredUI.Modules.Errors import XenError, VMNotFoundError
from FlaredUI.Logging import get_logger


logger = get_logger(__name__)


# Yes I know they are the same for now but the likelihood of api changes warrants both.
def get_xen_vm_info(server, vm_name, ssh_client=None):
    """Fetches detailed information about a VMs on a XenServer/XCP-ng host."""

    try:
        # Connect to XenServer/XCP-ng using XenAPI (adjust for SSL validation in production)
        session = XenAPI.Session(f"https://{server.hostname}")
        session.login_with_password(server.username, server.password)

        # Find the VMs by name
        vms = session.xenapi.VM.get_by_name_label(vm_name)
        if not vms:
            raise VMNotFoundError(f"VMs '{vm_name}' not found on XenServer/XCP-ng host '{server.hostname}'.")

        vm_ref = vms[0]  # Assuming only one VMs with this name exists

        # Get VMs record (detailed information)
        vm_record = session.xenapi.VM.get_record(vm_ref)

        # Extract relevant information (adjust fields as needed)
        vm_info = {
            'name': vm_record['name_label'],
            'guest_os_id': vm_record.get('os_version', {}).get('distro', 'unknown'),
            'os_type': vm_record.get('os_version', {}).get('name', 'unknown'),  # Attempt to get OS info
            'cpu_cores': vm_record['VCPUs_max'],
            'memory': vm_record['memory_dynamic_max'] // (1024 * 1024),  # Convert bytes to MB
            'state': vm_record['power_state'],
            'labels': None,  # No direct label support in XCP-ng VMs
            # ... (Add other fields as needed)
        }

        # Get IP addresses from VIFs (Virtual Network Interfaces)
        vifs = session.xenapi.VM.get_VIFs(vm_ref)
        for vif_ref in vifs:
            vif_record = session.xenapi.VIF.get_record(vif_ref)
            # Check if VIF is connected and has an IP
            if vif_record["currently_attached"] and vif_record.get("IP"):
                vm_info.setdefault('ip_addresses', []).append(vif_record["IP"])

        session.xenapi.session.logout()  # Close the session
        return vm_info

    except XenAPI.Failure as e:
        logger.error(f"XenAPI Error: {e}")
        raise XenError(f"Error retrieving VMs information from XenServer/XCP-ng: {e}")
    except Exception as e:  # Catch any unexpected errors
        logger.error(f"Error getting XenServer/XCP-ng VMs info: {e}")
        raise XenError(f"Error retrieving VMs information from XenServer/XCP-ng: {e}")


def list_xen_vms(server, ssh_client=None):
    """Retrieves a list of all VMs on the XenServer/XCP-ng server."""

    try:
        # Connect to XenServer/XCP-ng (same as in get_xen_vm_info)
        session = XenAPI.Session(f"https://{server.hostname}")
        session.login_with_password(server.username, server.password)

        # Get all VMs records
        vm_records = session.xenapi.VM.get_all_records()

        filtered_data = []
        for vm_ref, vm_record in vm_records.items():
            filtered_data.append({
                'vmid': vm_ref,  # VMs reference (UUID)
                'name': vm_record['name_label'],
                'os_type': vm_record.get('os_version', {}).get('name', 'unknown'),  # Attempt to get OS info
                'state': vm_record['power_state'],
                'labels': None  # No direct label support in XCP-ng VMs
            })

        session.xenapi.session.logout()
        return filtered_data

    except XenAPI.Failure as e:
        logger.error(f"XenAPI Error: {e}")
        raise XenError(f"Error listing VMs on XenServer/XCP-ng: {e}")
    except Exception as e:
        logger.error(f"Error listing XenServer/XCP-ng VMs: {e}")
        raise XenError(f"Error listing VMs on XenServer/XCP-ng: {e}")
