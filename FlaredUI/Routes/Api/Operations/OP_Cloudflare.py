from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from flasgger import swag_from
from FlaredUI.Modules.Errors import TunnelNotFoundError, CloudflaredError
from FlaredUI.Modules.DB import get_tunnel_by_id
from FlaredUI.Modules.Cloudflare import cloudflared_tunnel_status, cloudflared_tunnel_run, cloudflared_tunnel_cleanup

op_cf_bp = Blueprint("op_cloudflare", __name__, url_prefix="/api/cloudflare")


# --- Cloudflare Operational Routes ---
@op_cf_bp.route('/tunnels/<int:tunnel_id>/start', methods=['POST'])
@swag_from('../../SwagDocs/Tunnels/start_tunnel.yml')
@login_required
def start_tunnel(tunnel_id):
    try:
        tunnel = get_tunnel_by_id(tunnel_id)
        if not tunnel:
            raise TunnelNotFoundError("Tunnel not found")
        cloudflared_tunnel_run(tunnel.name)  # Use tunnel.name to run cloudflared
        return jsonify({"message": "Tunnel started successfully", "tunnel": tunnel.to_dict()}), 200
    except TunnelNotFoundError as e:
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@op_cf_bp.route('/tunnels/<int:tunnel_id>/stop', methods=['POST'])
@swag_from('../../SwagDocs/Tunnels/stop_tunnel.yml')
@login_required
def stop_tunnel(tunnel_id):
    try:
        tunnel = get_tunnel_by_id(tunnel_id)
        if not tunnel:
            raise TunnelNotFoundError("Tunnel not found")
        result = cloudflared_tunnel_cleanup(tunnel.name)  # Stop and cleanup the tunnel
        return jsonify({"message": "Tunnel stopped successfully", "result": result}), 200
    except TunnelNotFoundError as e:
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# Add tunnel status route to op_cf_bp
@op_cf_bp.route('/tunnels/<int:tunnel_id>/status', methods=['GET'])
@swag_from('../../SwagDocs/Tunnels/tunnel_status.yml')
@login_required
def tunnel_status(tunnel_id):
    """Gets the status of a Cloudflare tunnel."""

    try:
        tunnel = get_tunnel_by_id(tunnel_id)
        if not tunnel:
            return jsonify({"error": "Tunnel not found"}), 404

        tunnel_status = cloudflared_tunnel_status(tunnel.uuid)
        return jsonify({"status": tunnel_status}), 200
    except Exception as e:
        app.logger.error(f"Error getting tunnel status: {e}")
        return jsonify({"error": str(e)}), 500


