from flask import jsonify, request, redirect, url_for
from flask_login import login_user, logout_user, current_user
from FlaredUI.Modules.Errors import UnauthorizedError
from FlaredUI.Modules.Auth import logger
from FlaredUI.Modules.DB import LoginSchema
from marshmallow import ValidationError


def userpass_login(request):
    try:
        # Validate request data
        LoginSchema().load(request.form)

        if current_user.is_authenticated:
            return redirect(url_for('index'))

        username = request.form.get('username')
        password = request.form.get('password')
        user = current_user

        if user and user.check_password(password):
            login_user(user)
            logger.info(f"{user.username} logged in using User/Pass")
            return redirect(url_for('index'))
        else:
            raise UnauthorizedError("Invalid credentials")
    except UnauthorizedError as e:
        logger.warning(f"Failed login attempt for user: {username}")
        return jsonify({"error": str(e)}), 401
    except ValidationError as err:
        return jsonify(err.messages), 400



