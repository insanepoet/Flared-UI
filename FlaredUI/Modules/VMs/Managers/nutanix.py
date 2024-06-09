import ntnx_vmm_py_client
from ntnx_vmm_py_client.rest import ApiException
from FlaredUI.Modules.Errors import NutanixError, VMNotFoundError
from FlaredUI.Logging import get_logger


logger = get_logger(__name__)


def get_nutanix_vm_info(server, vm_name, ssh_client=None):
    """Fetches detailed information about a VMs on Nutanix AHV."""
    try:
        # Create a configuration object
        configuration = ntnx_vmm_py_client.Configuration()
        configuration.host = f'https://{server.hostname}:9440/api/nutanix/v3'
        configuration.username = server.username
        configuration.password = server.password
        configuration.verify_ssl = False  # Disable SSL verification for testing, adjust for production

        # Create an API client
        api_instance = ntnx_vmm_py_client.ApiClient(configuration)
        api_helper = ntnx_vmm_py_client.VmsApi(api_instance)

        # Fetch VMs details by name
        vm_list = api_helper.get_vms(filter=f"vm_name=={vm_name}")
        if not vm_list.entities:
            raise VMNotFoundError(f"VMs '{vm_name}' not found on Nutanix cluster '{server.hostname}'.")

        vm = vm_list.entities[0]  # Assuming one VMs matches the name

        # Extract relevant information (adjust fields as needed)
        vm_info = {
            'name': vm.spec.name,
            'guest_os_id': None,  # Nutanix doesn't have a direct guest OS ID equivalent
            'os_type': vm.status.guest_tools.os_version,
            'os_name': vm.status.resources.guest_os.os_name,
            'os_version': vm.status.resources.guest_os.os_version,
            'cpu_cores': vm.spec.resources.num_sockets,  # change to num_vcpus for virtual CPUs
            'memory': vm.spec.resources.memory_size_mib,
            'state': vm.status.state,
            'ip_addresses': [
                nic.ip_endpoint_list[0].ip for nic in vm.status.resources.nic_list
                if nic.ip_endpoint_list
            ],
            'labels': None,  # Handle labels if needed
        }
        return vm_info

    except ApiException as e:

        logger.error(f"Nutanix API Error: {e}")
        raise NutanixError(f"Nutanix API error: {e.body}")  # Extract error details from the API response
    except Exception as e:
        logger.error(f"Error getting Nutanix VMs info: {e}")
        raise NutanixError(f"Error retrieving VMs information from Nutanix: {e}")


def list_nutanix_vms(server, ssh_client=None):
    """Retrieves a list of all VMs on the Nutanix AHV cluster."""

    try:
        # Create a configuration object
        configuration = ntnx_vmm_py_client.Configuration()
        configuration.host = f'https://{server.hostname}:9440/api/nutanix/v3'
        configuration.username = server.username
        configuration.password = server.password
        configuration.verify_ssl = False  # Disable SSL verification for testing, adjust for production

        # Create an API client
        api_instance = ntnx_vmm_py_client.ApiClient(configuration)
        api_helper = ntnx_vmm_py_client.VmsApi(api_instance)
        vms_data = api_helper.get_vms()

        filtered_data = []
        for vm in vms_data.entities:
            filtered_data.append({
                'name': vm.spec.name,
                'os_type': vm.status.guest_tools.os_version,
                'state': vm.status.state,
                'labels': None,  # Add label extraction if needed
            })

        return filtered_data

    except ApiException as e:
        logger.error(f"Nutanix API Error: {e}")
        raise NutanixError(f"Nutanix API error: {e.body}")
    except Exception as e:
        logger.error(f"Error listing Nutanix VMs: {e}")
        raise NutanixError(f"Error retrieving VMs list from Nutanix: {e}")
