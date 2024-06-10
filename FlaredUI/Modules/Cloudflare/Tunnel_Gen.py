import yaml

from FlaredUI.Modules.DB import get_tunnel_by_id, get_container_by_id


def generate_cloudflared_config(tunnel_id):
    """Generates the cloudflared config.yml file for a given tunnel."""

    try:
        # Fetch tunnel details from the database
        tunnel = get_tunnel_by_id(tunnel_id)
        if not tunnel:
            raise ValueError("Tunnel not found.")

        # Construct the configuration dictionary
        config_data = {
            'tunnel': tunnel.uuid,
            'credentials-file': '/etc/cloudflared/cert.pem',
            'ingress': [],
        }

        # Assuming you have a relationship in your models to get containers associated with a tunnel
        for container in tunnel.containers:
            if container.enabled:
                config_data['ingress'].append(
                    {
                        'hostname': container.hostname,
                        'service': f"http://{container.server.ip_address}:{container.exposed_ports}"
                    }
                )

        # Add a catch-all rule
        config_data['ingress'].append(
            {
                'service': 'http_status:404'
            }
        )

        # Generate the YAML string
        yaml_config = yaml.dump(config_data)

        # Write the YAML string to the config.yml file
        with open('../Data/Flared.config', 'w') as f:
            f.write(yaml_config)
    except Exception as e:
        # Log the error
        logger.error(f"Error generating Cloudflared config: {e}")
        raise
