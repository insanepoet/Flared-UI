from flask import Blueprint, jsonify
from flask_login import login_required
from FlaredUI.Modules.DB import get_vm_by_id, get_server_by_id
from FlaredUI.Modules.VMs.VM import get_vm_info, list_vms
from flasgger import swag_from
from FlaredUI.Modules.Errors import VMNotFound
from FlaredUI.Modules.VMs.Managers import *

op_vm_bp = Blueprint("op_vms", __name__, url_prefix="/api/vms")  # Define blueprint


@op_vm_bp.route('/<int:vm_id>/start', methods=['POST'])
@swag_from('../../SwagDocs/VMs/start_vm.yml')  # Add your Swagger YAML doc
@login_required
def start_vm(vm_id):
    """Starts a VM."""

    try:
        # Fetch VM and Server details from the database
        vm = get_vm_by_id(vm_id)
        if not vm:
            raise VMNotFound(f"VM with ID {vm_id} not found.")
        server = get_server_by_id(vm.server_id)

        # Start the VM using the appropriate manager
        manager_name = server.vm_manager.name.lower()
        start_vm_function = globals().get(f"start_{manager_name}_vm")
        if start_vm_function:
            start_vm_function(server, vm)
            return jsonify({"message": f"VM '{vm.name}' started successfully."}), 200
        else:
            raise NotImplementedError(f"Starting VMs for '{manager_name}' is not yet implemented.")

    except (VMNotFound, NotImplementedError) as e:
        app.logger.error(str(e))
        return jsonify({'error': str(e)}), 404 if isinstance(e, VMNotFound) else 501
    except Exception as e:
        app.logger.error(f"Unexpected error starting VM: {e}")
        return jsonify({"error": "Internal server error"}), 500


# Add similar routes for /stop and /restart
@op_vm_bp.route('/<int:vm_id>/stop', methods=['POST'])
@swag_from('../../SwagDocs/VMs/stop_vm.yml')
@login_required
def stop_vm(vm_id):
    """Stops a VM."""

    try:
        vm = get_vm_by_id(vm_id)
        if not vm:
            raise VMNotFound(f"VM with ID {vm_id} not found.")
        server = get_server_by_id(vm.server_id)

        manager_name = server.vm_manager.name.lower()
        stop_vm_function = globals().get(f"stop_{manager_name}_vm")
        if stop_vm_function:
            stop_vm_function(server, vm)
            return jsonify({"message": f"VM '{vm.name}' stopped successfully."}), 200
        else:
            raise NotImplementedError(f"Stopping VMs for '{manager_name}' is not yet implemented.")

    except (VMNotFound, NotImplementedError) as e:
        return jsonify({'error': str(e)}), 404 if isinstance(e, VMNotFound) else 501
    except Exception as e:  # Catch any other unexpected exceptions
        app.logger.error(f"Unexpected error stopping VM: {e}")
        return jsonify({"error": "Internal server error"}), 500


@op_vm_bp.route('/<int:vm_id>/restart', methods=['POST'])
@swag_from('../../SwagDocs/VMs/restart_vm.yml')
@login_required
def restart_vm(vm_id):
    """Restarts a VM."""

    try:
        vm = get_vm_by_id(vm_id)
        if not vm:
            raise VMNotFound(f"VM with ID {vm_id} not found.")
        server = get_server_by_id(vm.server_id)

        manager_name = server.vm_manager.name.lower()
        restart_vm_function = globals().get(f"restart_{manager_name}_vm")
        if restart_vm_function:
            restart_vm_function(server, vm)
            return jsonify({"message": f"VM '{vm.name}' restarted successfully."}), 200
        else:
            raise NotImplementedError(f"Restarting VMs for '{manager_name}' is not yet implemented.")

    except (VMNotFound, NotImplementedError) as e:
        return jsonify({'error': str(e)}), 404 if isinstance(e, VMNotFound) else 501
    except Exception as e:  # Catch any other unexpected exceptions
        app.logger.error(f"Unexpected error restarting VM: {e}")
        return jsonify({"error": "Internal server error"}), 500