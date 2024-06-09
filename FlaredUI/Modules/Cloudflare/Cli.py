import subprocess
import json
from shutil import which
from FlaredUI.Modules.Cloudflare.Tunnel_Gen import generate_cloudflared_config
from FlaredUI.Modules.Errors import CloudflaredError


def is_cloudflared_installed():
    """Checks if cloudflared is installed."""
    return which("cloudflared") is not None


def initialize_cloudflared():
    """Initializes cloudflared, ensuring it's installed and available."""

    if not is_cloudflared_installed():
        raise RuntimeError(
            "cloudflared is not installed. Please ensure it is installed in the Docker image."
        )

    # TODO: Add additional initialization steps (e.g., checking version, configuration) if needed. Version may be
    #  useful but likely container update to resolve. (Possibly through actions)


def run_cloudflared_command(command_args, input_data=None):
    """Runs a cloudflared command and returns the output as a dictionary."""

    try:
        # Ensure cloudflared is installed before running commands
        initialize_cloudflared()

        # Execute command (handling input_data if provided)
        result = subprocess.run(
            ["cloudflared"] + command_args,
            input=json.dumps(input_data).encode() if input_data else None,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True,
            text=True,
        )

        # Parse output
        try:
            output = json.loads(result.stdout)
        except json.JSONDecodeError:
            output = result.stdout  # Return raw output if not JSON

        # Log stderr output if present
        if result.stderr:
            app.logger.warning(f"cloudflared command stderr: {result.stderr}")

        return output

    except subprocess.CalledProcessError as e:
        app.logger.error(f"Error running cloudflared command: {e}")
        error_output = e.stderr if e.stderr else "An error occurred."
        raise CloudflaredError(error_output)

    # --- Tunnel Functions ---


def create_cloudflared_tunnel(tunnel_name):
    """Creates a new cloudflared tunnel and returns the tunnel ID."""
    output = run_cloudflared_command(["tunnel", "create", tunnel_name])
    return output


def list_cloudflared_tunnels():
    """Lists all cloudflared tunnels."""
    output = run_cloudflared_command(["tunnel", "list"])
    return output


def get_cloudflared_tunnel_info(tunnel_id_or_name):
    """Gets information about a specific cloudflared tunnel."""
    output = run_cloudflared_command(["tunnel", "info", tunnel_id_or_name])
    return output


def start_cloudflared_tunnel(tunnel_id):
    """Runs the cloudflared tunnel process for the specified tunnel ID."""
    output = run_cloudflared_command(["tunnel", "run", tunnel_id])
    return output


def cloudflared_tunnel_status(tunnel_id):
    """Performs a health check for the specified tunnel ID."""
    output = run_cloudflared_command(["tunnel", "status", tunnel_id])
    return output


def cloudflared_tunnel_delete(tunnel_id_or_name):
    """Deletes the cloudflared tunnel with the given ID or name."""
    return run_cloudflared_command(["tunnel", "delete", tunnel_id_or_name])


def stop_and_cleanup_cloudflared_tunnel(tunnel_id_or_name):
    """Cleans up the cloudflared tunnel. This might include stopping the tunnel, removing routes, or clearing configuration."""
    # First, stop the tunnel if it's running
    run_cloudflared_command(["tunnel", "stop", tunnel_id_or_name])

    # Add other cleanup tasks here as needed
    # For example, removing routes associated with the tunnel

    generate_cloudflared_config(tunnel_id_or_name)


# --- Route Functions ---

def cloudflared_route_list():
    """Lists all configured routes."""
    return run_cloudflared_command(["route", "list"])


def cloudflared_route_create(tunnel_id, hostname, service):
    """Creates a new route for the specified tunnel."""
    return run_cloudflared_command(["route", "add", tunnel_id, hostname, service])


def cloudflared_route_delete(route_id):
    """Deletes a route by ID."""
    return run_cloudflared_command(["route", "delete", route_id])


# --- Login Functions ---

def cloudflared_login(token):
    """Performs a cloudflared login using the provided API token."""
    command_args = ["login", "--no-autoupdate"]  # Disable autoupdate to avoid conflicts
    output = run_cloudflared_command(command_args, input_data={"token": token})

    # TODO: Yadd logic to save the token to the database (encrypted)
    return output


# --- Token Functions ---

def cloudflared_token_create(name, scopes=None):
    """Creates a new cloudflared token with optional scopes."""
    command_args = ["token", "create", name]
    if scopes:
        command_args.extend(scopes)  # Add scopes to the command if provided
    output = run_cloudflared_command(command_args)
    return output


def cloudflared_token_list():
    """Lists all cloudflared tokens."""
    return run_cloudflared_command(["token", "list"])


def cloudflared_token_delete(token_name):
    """Deletes a cloudflared token by name."""
    return run_cloudflared_command(["token", "delete", token_name])


# --- Access Functions ---

def cloudflared_access_list(account_name=None, application_aud=None):
    """Lists Access applications, optionally filtered by account or aud."""
    command_args = ["access", "list"]
    if account_name:
        command_args.append(f"--account-name={account_name}")
    if application_aud:
        command_args.append(f"--application-aud={application_aud}")
    return run_cloudflared_command(command_args)


# Example of access rule creation function
def cloudflared_access_rule_create(application_name, allow_ip, allow_email=None):
    """Creates an Access rule that allows the specified IP or email."""
    command_args = [
        "access", "rule", "create", application_name, "--allow-ip", allow_ip
    ]
    if allow_email:
        command_args.extend(["--allow-email", allow_email])
    return run_cloudflared_command(command_args)


# --- Teams Functions ---
def cloudflared_teams_list():
    """Lists teams the user is a member of."""
    return run_cloudflared_command(["teams", "list"])