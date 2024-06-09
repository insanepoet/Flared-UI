from flask import jsonify
from FlaredUI.Modules.Auth.OAuth import oauth_login
from FlaredUI.Modules.Auth.UserPass import userpass_login
from FlaredUI.Modules.Auth.ApiKey import load_user_from_api_key
from FlaredUI.Modules.DB.Schemas import LoginSchema, OAuthLoginSchema
from marshmallow import ValidationError
from markupsafe import Markup

from FlaredUI.Modules.Auth import logger


def handle_login(request):
    """
    Handles login requests, sanitizes input, and determines the appropriate authentication method.
    """
    try:
        if 'username' in request.form and 'password' in request.form:
            # User/Password Login
            login_data = {
                'username': Markup.escape(request.form.get('username')),
                'password': Markup.escape(request.form.get('password'))
            }
            LoginSchema().load(login_data)
            return userpass_login(request)

        elif 'provider' in request.args:
            # OAuth Login
            oauth_data = {
                'provider': Markup.escape(request.args.get('provider'))
            }
            OAuthLoginSchema().load(oauth_data)
            return oauth_login(oauth_data['provider'])

        elif 'X-API-Key' in request.headers:
            # API Key Login
            return load_user_from_api_key(request)

        else:
            raise ValidationError("Invalid login request format.")
    except ValidationError as err:
        return jsonify({"error": err.messages}), 400
