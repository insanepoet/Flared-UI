from flask import Blueprint, request, render_template, redirect, url_for
from flask_login import login_required, logout_user
from FlaredUI.Modules.Auth import handle_login, logout
from flasgger import swag_from


auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')
site_bp = Blueprint('site', __name__, url_prefix='/')


@site_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Handle login form submission here (verify credentials)
        # If successful, login_user(...)
        return redirect(url_for('index'))  # Or the desired page after login
    return render_template('login.html')


@auth_bp.route('/login', methods=['POST'])
@swag_from('../SwagDocs/Auth/login.yml')
def login_route():
    """Route for handling all login requests (user/pass, OAuth, or API key)."""
    return handle_login(request)


@auth_bp.route('/logout', methods=['GET'])
@swag_from('../SwagDocs/Auth/logout.yml')
@login_required
def logout_route():
    """Route for handling logout requests."""
    return logout_user()