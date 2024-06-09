import json

import requests
from urllib3.exceptions import InsecureRequestWarning
from FlaredUI.Modules.Errors import TrueNASJailError

requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)


# --- TrueNAS Jail Functions ---

def get_truenas_jail_container_info(server, jail_name, ssh_client=None):
    """Fetches detailed information about a container within a TrueNAS jail."""
    try:
        # Fetch TrueNAS API key from server
        api_key = server.password  # Assuming API key is stored as the password

        # Construct API URL
        api_url = f"https://{server.hostname}/api/v2.0/jail/id/{jail_name}"
        headers = {
            "Authorization": f"Bearer {api_key}"
        }

        # Make API call to get jail information
        response = requests.get(api_url, headers=headers, verify=False)
        response.raise_for_status()  # Raise an exception for bad responses

        jail_data = response.json()

        if jail_data and jail_data["state"] == "up":
            # Fetch IP addresses from jail interfaces
            interfaces = jail_data.get('interfaces', [])
            ip_addresses = [interface.get('ip4_addr') for interface in interfaces if interface.get('ip4_addr')]

            return {
                "name": jail_name,
                "image": None,  # Jails don't have a direct concept of images
                "state": jail_data["state"],
                "ip_addresses": ip_addresses,  # Include IP addresses
                "exposed_ports": {
                    str(port["jail_port"]): str(port["host_port"])
                    for port in jail_data.get("fstab", [])
                },
                "labels": None,  # No direct equivalent to Docker labels in TrueNAS jails
                # ... (Add other fields as needed)
            }
        else:
            raise TrueNASJailError(f"TrueNAS jail '{jail_name}' not found or not running.")

    except requests.exceptions.RequestException as e:
        app.logger.error(f"Error getting TrueNAS jail info: {e}")
        raise TrueNASJailError(f"Error communicating with TrueNAS API: {e}")

def list_truenas_jail_containers(server, ssh_client=None):
    """Retrieves a list of all TrueNAS jails on the specified server."""
    try:
        # Fetch TrueNAS API key
        api_key = server.password

        # Construct API URL
        api_url = f"https://{server.hostname}/api/v2.0/jail/"
        headers = {
            "Authorization": f"Bearer {api_key}"
        }

        # Make API call to get all jails
        response = requests.get(api_url, headers=headers, verify=False)
        response.raise_for_status()

        jails_data = response.json()

        filtered_data = []
        for jail in jails_data:
            filtered_data.append(
                {
                    "name": jail["id"],
                    "image": None,
                    "state": jail["state"],
                    "labels": None,
                }
            )

        return filtered_data

    except requests.exceptions.RequestException as e:
        app.logger.error(f"Error listing TrueNAS jails: {e}")
        raise TrueNASJailError(f"Error communicating with TrueNAS API: {e}")
