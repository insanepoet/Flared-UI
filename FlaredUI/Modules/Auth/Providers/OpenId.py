from authlib.integrations.flask_client import OAuth
from flask import url_for, request, redirect, jsonify
from FlaredUI.Modules.Errors import UnauthorizedError
from FlaredUI.Modules.DB import db, get_or_create_oauth_user, OAuthProvider
from flask_login import login_user


class OpenID:
    def __init__(self, oauth, client_id=None, client_secret=None):
        self.oauth = oauth
        self.client_id = client_id
        self.client_secret = client_secret

    def register(self):
        """Registers the OAuth callback route for OpenID Connect."""
        raise NotImplementedError("Subclass must implement the register method")

    def _get_provider_id(self):
        """Helper function to get the provider ID from the database."""
        return OAuthProvider.query.filter_by(platform=self.name).first().id

    def _create_or_get_user(self, userinfo):
        """Creates or gets a user based on the OpenID Connect userinfo."""
        user_data = {
            'username': userinfo['preferred_username'],
            'email': userinfo['email'],
            'provider_id': self._get_provider_id(),
            'oauth_id': userinfo['sub'],
        }
        return get_or_create_oauth_user(user_data)


class Keycloak(OpenID):
    name = 'keycloak'

    def register(self):
        """Registers the OAuth callback route for Keycloak."""
        # Get provider-specific data from the database
        provider_data = OAuthProvider.query.filter_by(platform=self.name).first().provider_data

        if not provider_data or 'server_metadata_url' not in provider_data:
            raise ValueError(f"Missing server_metadata_url for Keycloak provider in the database.")

        self.oauth.register(
            name=self.name,
            client_id=self.client_id,
            client_secret=self.client_secret,
            server_metadata_url=provider_data['server_metadata_url'],  # Get from provider_data
            client_kwargs={'scope': 'openid email profile'}  # Adjust scopes as needed
        )

        @self.oauth.callback(self.name)
        def keycloak_callback():
            """Handles the callback from Keycloak after user authorization."""
            try:
                token = self.oauth.keycloak.authorize_access_token()
                userinfo = self.oauth.keycloak.parse_id_token(token)

                user = self._create_or_get_user(userinfo)
                login_user(user)
                return redirect(url_for("index"))
            except UnauthorizedError as e:
                # Handle unauthorized access (e.g., invalid tokens)
                return jsonify({"error": str(e)}), 401
            except Exception as e:  # Catch any other unexpected exceptions

                app.logger.error(f"Error during Keycloak authorization: {e}")
                return jsonify({"error": "An error occurred during Keycloak authorization."}), 500


class Auth0(OpenID):
    name = 'auth0'  # Provider name

    def register(self):
        """Registers the OAuth callback route for Auth0."""
        provider_data = OAuthProvider.query.filter_by(platform=self.name).first().provider_data
        domain = provider_data.get('domain')
        self.oauth.register(
            name=self.name,
            client_id=self.client_id,
            client_secret=self.client_secret,
            access_token_url=f'https://{domain}/oauth/token',
            authorize_url=f'https://{domain}/authorize',
            api_base_url=f'https://{domain}',
            client_kwargs={'scope': 'openid email profile'},
        )

        @self.oauth.callback(self.name)
        def auth0_callback():
            """Handles the callback from Auth0 after user authorization."""
            try:
                token = self.oauth.auth0.authorize_access_token()
                userinfo = self.oauth.auth0.parse_id_token(token)
                user = self._create_or_get_user(userinfo)
                login_user(user)
                return redirect(url_for("index"))  # Redirect to your main page
            except UnauthorizedError as e:
                # Handle unauthorized access (e.g., invalid tokens)
                return jsonify({"error": str(e)}), 401
            except Exception as e:  # Catch any other unexpected exceptions

                app.logger.error(f"Error during Auth0 authorization: {e}")
                return jsonify({"error": "An error occurred during Auth0 authorization."}), 500


class Okta(OpenID):
    name = 'okta'

    def register(self):
        """Registers the OAuth callback route for Okta."""
        # Get provider-specific data from the database
        provider_data = OAuthProvider.query.filter_by(platform=self.name).first().provider_data

        if not provider_data or 'server_metadata_url' not in provider_data:
            raise ValueError(f"Missing server_metadata_url for Okta provider in the database.")

        self.oauth.register(
            name=self.name,
            client_id=self.client_id,
            client_secret=self.client_secret,
            server_metadata_url=provider_data['server_metadata_url'],  # Get from provider_data
            client_kwargs={'scope': 'openid email profile'}  # Adjust scopes as needed
        )

        @self.oauth.callback(self.name)
        def okta_callback():
            """Handles the callback from Okta after user authorization."""
            try:
                token = self.oauth.okta.authorize_access_token()
                userinfo = self.oauth.okta.parse_id_token(token)

                user = self._create_or_get_user(userinfo)
                login_user(user)
                return redirect(url_for("index"))
            except UnauthorizedError as e:
                # Handle unauthorized access (e.g., invalid tokens)
                return jsonify({"error": str(e)}), 401
            except Exception as e:  # Catch any other unexpected exceptions

                app.logger.error(f"Error during Okta authorization: {e}")
                return jsonify({"error": "An error occurred during Okta authorization."}), 500
