from authlib.integrations.flask_client import OAuth
from flask import jsonify, session, redirect, request, url_for
from FlaredUI.Config import config
from FlaredUI.Modules.Auth.Providers import Github, Google, OpenId
from FlaredUI.Modules.Errors import UnauthorizedError
from FlaredUI.Modules.DB import db, OAuthProvider, OAuthProviderSchema, get_or_create_oauth_user, UserSchema, User
from flask_login import login_user
import os


def create_oauth(app):
    oauth = OAuth(app, fetch_token=fetch_token)

    # Load OAuth provider configurations from the database
    provider_schemas = OAuthProviderSchema(many=True)
    providers = provider_schemas.dump(db.session.query(OAuthProvider).filter_by(enabled=True).all())

    for provider in providers:
        provider_cls = globals().get(provider['platform'].capitalize())
        if provider_cls:
            provider_obj = provider_cls(oauth, provider['client_id'], provider.get_client_secret())  # Decrypt secret
            provider_obj.register()

    return oauth


def fetch_token(name, request):
    token = oauth.create_client(name).authorize_access_token()
    return token


def oauth_login(provider):
    if provider not in oauth.client_names:
        return jsonify({"error": f"OAuth provider '{provider}' not found."}), 404

    # Generate and store a CSRF token for security
    csrf_token = os.urandom(16).hex()
    session[csrf_token] = True

    redirect_uri = url_for("auth.oauth_authorize", provider=provider, _external=True, state=csrf_token)
    return oauth.create_client(provider).authorize_redirect(redirect_uri,
                                                            state=csrf_token)  # Include state for security


def oauth_authorize(provider):
    # Check CSRF token for security
    if not session.pop(request.args.get('state'), False):
        raise UnauthorizedError("Invalid state parameter.")

    client = oauth.create_client(provider)
    token = client.authorize_access_token()
    user_info = client.parse_id_token(token)

    if user_info:
        user_schema = UserSchema()  # Marshmallow schema for validation
        user_data, errors = user_schema.load(user_info)  # Updated to capture errors
        if errors:
            return jsonify({"error": "Invalid user data from OAuth provider."}), 400  # Bad Request

        user = User.get_or_create_oauth_user(user_data)
        login_user(user)
        return redirect(url_for("index"))
    else:
        raise UnauthorizedError("Failed to retrieve user info from OAuth provider.")


def init_oauth(app):
    """Initialize the OAuth instance before handling any requests."""
    global oauth
    if not oauth:
        oauth = create_oauth(app)


oauth = None  # Initialize OAuth object