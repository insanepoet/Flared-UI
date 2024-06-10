from flask import Blueprint, request, jsonify
from flask_login import login_required
from FlaredUI.Modules.DB import (
    db, update_vm, delete_vm, create_vm,
    get_server_by_id, VMCreateSchema, VMSchema
)
from FlaredUI.Modules.VMs import get_vm_info, list_vms
from flasgger import swag_from
from marshmallow import ValidationError

db_vm_bp = Blueprint('vm', __name__)


# --- VM Routes ---
@db_vm_bp.route('/servers/<int:server_id>/vms', methods=['GET'])
@swag_from('../../SwagDocs/VMs/list_vms.yml')
@login_required
def list_vms_route(server_id):
    """List all VMs on a specified server."""

    try:
        server = get_server_by_id(server_id)
        if not server:
            return jsonify({"error": "Server not found"}), 404

        # Call the list_vms function from DB_VMs.py
        vms = list_vms(server)
        return jsonify(vms), 200
    except Exception as e:
        app.logger.error(f"Error listing VMs: {e}")
        return jsonify({"error": str(e)}), 500


@db_vm_bp.route('/servers/<int:server_id>/vms/<string:vm_id>', methods=['GET'])
@swag_from('../../SwagDocs/VMs/get_vm.yml')
@login_required
def get_vm_route(server_id, vm_id):
    """Get detailed information about a specific VM on a server."""

    try:
        server = get_server_by_id(server_id)
        if not server:
            return jsonify({"error": "Server not found"}), 404

        # Call the get_vm_info function from DB_VMs.py
        vm_info = get_vm_info(server, vm_id)
        return jsonify(vm_info), 200
    except Exception as e:
        app.logger.error(f"Error getting VM info: {e}")
        return jsonify({"error": str(e)}), 500


@db_vm_bp.route('/servers/<int:server_id>/vms', methods=['POST'])
@swag_from('../../SwagDocs/VMs/create_vm.yml')
@login_required
def create_vm_route(server_id):
    """Creates a new VM on the specified server."""

    try:
        data = request.get_json()
        VMCreateSchema().load(data)  # Validate input data
        server = get_server_by_id(server_id)
        if not server:
            return jsonify({"error": "Server not found"}), 404

        # Validate VM manager
        if server.vm_manager is None:
            return jsonify({"error": f"Server '{server.name}' does not have a VM manager defined."}), 400

        # Create the VM
        vm = create_vm(data)
        return jsonify(vm.to_dict()), 201
    except ValidationError as err:
        return jsonify(err.messages), 400
    except ValueError as e:  # Catch ValueError from database functions
        app.logger.error(f"Error creating VM: {e}")
        return jsonify({"error": str(e)}), 400
    except Exception as e:  # Catch any other unexpected exceptions
        app.logger.error(f"Unexpected error creating VM: {e}")
        db.session.rollback()
        return jsonify({"error": "Internal server error"}), 500


@db_vm_bp.route('/servers/<int:server_id>/vms/<int:vm_id>', methods=['PUT'])
@swag_from('../../SwagDocs/VMs/update_vm.yml')
@login_required
def update_vm_route(server_id, vm_id):
    """Updates an existing VM on the specified server."""

    try:
        data = request.get_json()
        VMSchema(exclude=["name", "server_id"]).load(data)
        server = get_server_by_id(server_id)
        if not server:
            return jsonify({"error": "Server not found"}), 404

        # Validate VM manager
        if server.vm_manager is None:
            return jsonify({"error": f"Server '{server.name}' does not have a VM manager defined."}), 400
        vm = update_vm(vm_id, data)

        if not vm:
            return jsonify({"error": "VM not found"}), 404

        return jsonify(vm.to_dict()), 200
    except ValidationError as err:
        return jsonify(err.messages), 400
    except Exception as e:
        app.logger.error(f"Unexpected error updating VM: {e}")
        db.session.rollback()
        return jsonify({"error": "Internal server error"}), 500


@db_vm_bp.route('/servers/<int:server_id>/vms/<int:vm_id>', methods=['DELETE'])
@swag_from('../../SwagDocs/VMs/delete_vm.yml')  # Reference your delete_vm.yml file
@login_required
def delete_vm_route(server_id, vm_id):
    """Deletes a VM from the specified server."""

    try:
        server = get_server_by_id(server_id)
        if not server:
            return jsonify({"error": "Server not found"}), 404

        vm = delete_vm(vm_id)
        if not vm:
            return jsonify({"error": "VM not found"}), 404

        return jsonify({"message": "VM deleted successfully"}), 200
    except Exception as e:
        app.logger.error(f"Error deleting VM: {e}")
        db.session.rollback()
        return jsonify({"error": str(e)}), 500