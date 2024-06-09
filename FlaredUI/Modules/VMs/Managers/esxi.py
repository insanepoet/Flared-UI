from pyVim.connect import SmartConnect, Disconnect
from pyVmomi import vim
import ssl
from FlaredUI.Modules.Errors import ESXiError
from FlaredUI.Logging import get_logger


logger = get_logger(__name__)


def get_esxi_vm_info(server, vm_name, ssh_client=None):
    """Fetches detailed information about a VMs on an ESXi host."""
    try:
        # Connect to ESXi host
        context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
        context.verify_mode = ssl.CERT_NONE  # Disable SSL verification (for testing)
        si = SmartConnect(host=server.hostname, user=server.username, pwd=server.password,
                          port=server.ssh_port, sslContext=context)

        # Find the VMs by name
        content = si.RetrieveContent()
        vm = None
        for child in content.rootFolder.childEntity:
            if hasattr(child, 'vmFolder'):
                for vm_obj in child.vmFolder.childEntity:
                    if vm_obj.name == vm_name:
                        vm = vm_obj
                        break
        if not vm:
            raise ESXiError(f"VMs '{vm_name}' not found on ESXi host '{server.hostname}'.")

        # Gather VMs details
        vm_info = {
            'name': vm.name,
            'guest_os_id': vm.config.guestId,
            'os_type': vm.config.guestFullName,
            'os_name': 'unknown',  # pyvmomi does not expose os_name or version will extract
            'os_version': 'unknown',
            'cpu_cores': vm.config.hardware.numCPU,
            'memory': vm.config.hardware.memoryMB,
            'state': vm.summary.runtime.powerState,
            'labels': None,
            # ... (Add other fields as needed, e.g., network info, storage info)
        }

        # Extract OS Name and Version (this may need to be modified based on the specific format in guestFullName)
        os_info = vm.config.guestFullName.split()
        if len(os_info) >= 2:
            vm_info['os_name'] = os_info[0]
            vm_info['os_version'] = os_info[1]

        Disconnect(si)
        return vm_info
    except Exception as e:

        logger.error(f"Error getting ESXi VMs info: {e}")
        raise ESXiError(f"Error retrieving VMs information from ESXi: {e}")


def list_esxi_vms(server, ssh_client=None):
    """Retrieves a list of all VMs on an ESXi host."""
    try:
        # Connect to ESXi host (same as in get_esxi_vm_info)
        context = ssl._create_unverified_context()
        si = SmartConnect(host=server.hostname, user=server.username, pwd=server.password, port=server.ssh_port,
                          sslContext=context)

        if not si:
            raise ESXiError(f"Could not connect to ESXi host '{server.hostname}'.")

        content = si.RetrieveContent()
        vms = []

        # Iterate through VMs and gather basic information
        for child in content.rootFolder.childEntity:
            if hasattr(child, 'vmFolder'):
                for vm in child.vmFolder.childEntity:
                    vms.append({
                        'name': vm.name,
                        'guest_os_id': vm.config.guestId,
                        'os_type': vm.config.guestFullName,  # Extract OS name and version later if needed
                        'state': vm.summary.runtime.powerState,
                        'labels': None  # No labels in ESXi by default
                    })

        Disconnect(si)
        return vms

    except vim.fault.InvalidLogin as e:
        raise ESXiError(f"Invalid credentials for ESXi host '{server.hostname}': {e}")
    except Exception as e:

        logger.error(f"Error listing ESXi VMs: {e}")
        raise ESXiError(f"Error retrieving VMs list from ESXi: {e}")
