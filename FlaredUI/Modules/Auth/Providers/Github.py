from authlib.integrations.flask_client import OAuth
from flask import url_for, request, redirect
from flask_login import login_user
from FlaredUI.Modules.DB import get_or_create_oauth_user, OAuthProvider


class Github:
    def __init__(self, oauth, client_id=None, client_secret=None):
        self.oauth = oauth
        self.client_id = client_id
        self.client_secret = client_secret

        # Register the GitHub OAuth provider
        self.oauth.register(
            name='github',
            client_id=self.client_id,
            client_secret=self.client_secret,
            access_token_url='https://github.com/login/oauth/access_token',
            access_token_params=None,
            authorize_url='https://github.com/login/oauth/authorize',
            authorize_params=None,
            api_base_url='https://api.github.com/',
            client_kwargs={'scope': 'user:email'},
        )

    def register(self):
        """Registers the OAuth callback route for GitHub."""

        @self.oauth.callback("github")
        def github_callback():
            """Handles the callback from GitHub after user authorization."""
            resp = self.oauth.github.authorize_access_token()
            profile = self.oauth.github.get('user', token=resp).json()
            email = profile['email']

            user_data = {
                'username': profile['login'],
                'email': email,
                'provider_id': OAuthProvider.query.filter_by(platform='github').first().id,
                'oauth_id': str(profile['id'])
            }
            user = get_or_create_oauth_user(user_data)
            login_user(user)
            return redirect(url_for("index"))