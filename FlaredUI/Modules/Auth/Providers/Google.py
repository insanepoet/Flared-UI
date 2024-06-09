from authlib.integrations.flask_client import OAuth
from flask import url_for, request
from FlaredUI.Modules.DB import get_or_create_oauth_user, OAuthProvider
from flask_login import login_user, redirect


class Google:
    def __init__(self, oauth, client_id=None, client_secret=None):
        self.oauth = oauth
        self.client_id = client_id
        self.client_secret = client_secret

        # Register the Google OAuth provider
        self.oauth.register(
            name='google',
            client_id=self.client_id,
            client_secret=self.client_secret,
            server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
            client_kwargs={'scope': 'openid email profile'},
        )

    def register(self):
        """Registers the OAuth callback route for Google."""

        @self.oauth.callback("google")
        def google_callback():
            """Handles the callback from Google after user authorization."""
            resp = self.oauth.google.authorize_access_token()
            user_info = self.oauth.google.parse_id_token(resp)
            user_data = {
                'username': user_info['name'],
                'email': user_info['email'],
                'provider_id': OAuthProvider.query.filter_by(platform='google').first().id,
                'oauth_id': user_info['sub']
            }
            user = get_or_create_oauth_user(user_data)
            login_user(user)
            return redirect(url_for("index"))
