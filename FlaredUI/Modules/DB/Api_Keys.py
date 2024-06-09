from FlaredUI.Modules.DB import db
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from marshmallow import ValidationError
from FlaredUI.Modules.DB import User, OAuthProvider
from FlaredUI.Modules.DB.Schemas import ApiKeySchema, OAuthProviderSchema
from FlaredUI.Modules.DB.Models import ApiKeys
from FlaredUI.Logging import get_logger
from flask_login import current_user
from cachetools import cached, TTLCache
import secrets
from cryptography.fernet import Fernet
from FlaredUI.Config import encryption_key
from FlaredUI.Modules.Errors import UnauthorizedError
from datetime import datetime, timezone


logger = get_logger(__name__)


def create_api_key(data):
    """Creates a new API key for the specified user (or current user if not specified)."""
    try:
        ApiKeySchema().load(data)

        # Get the user from the input data or current user
        if 'user_id' in data:
            user = User.query.get(data['user_id'])
            if not user:
                raise ValueError(f"User with ID {data['user_id']} not found.")
        elif current_user.is_authenticated:
            user = current_user
        else:
            raise ValueError("User ID must be provided or you must be logged in.")

        api_key_value = secrets.token_urlsafe(32)
        api_key = ApiKeys(
            name=data['name'],
            description=data.get('description'),
            value=api_key_value,
            user=user
        )
        db.session.add(api_key)
        db.session.commit()

        get_all_api_keys.cache_clear()

        logger.info(f"Created API key '{api_key.name}' for user {user.username}")
        return api_key
    except ValidationError as err:

        logger.error(f"Validation error creating API key: {err.messages}")
        raise ValueError(err.messages)
    except IntegrityError:
        db.session.rollback()
        raise ValueError("API key name already exists for this user.")
    except SQLAlchemyError as e:
        db.session.rollback()

        logger.error(f"Database error creating API key: {e}")
        raise Exception("Database error.")


@cached(cache=TTLCache(maxsize=1024, ttl=300))
def get_all_api_keys():
    """Retrieves all API keys but excludes the actual key values."""
    try:
        api_keys = ApiKeys.query.all()
        return [key.to_dict() for key in api_keys]
    except SQLAlchemyError as e:

        logger.error(f"Database error: {e}")
        raise Exception("Database error")


@cached(cache=TTLCache(maxsize=1024, ttl=300))
def get_api_key_by_id(api_key_id):
    """Retrieves an API key by its ID, but excludes the actual key value."""
    try:
        api_key = ApiKeys.query.get(api_key_id)
        if not api_key:
            raise ValueError("API key not found")
        return api_key.to_dict()
    except SQLAlchemyError as e:

        logger.error(f"Database error: {e}")
        raise Exception("Database error")


@cached(cache=TTLCache(maxsize=1024, ttl=300))
def get_api_keys_by_user(user_id):
    """Retrieves all API keys associated with a specific user, excluding values."""
    try:
        api_keys = ApiKeys.query.filter_by(user_id=user_id).all()
        return [key.to_dict() for key in api_keys]
    except SQLAlchemyError as e:

        logger.error(f"Database error: {e}")
        raise Exception("Database error")


@cached(cache=TTLCache(maxsize=1024, ttl=300))
def get_api_key_by_value(value):
    """Retrieves an API key by its value."""
    try:
        return ApiKeys.query.filter_by(value=value).first()
    except SQLAlchemyError as e:

        logger.error(f"Database error: {e}")
        raise Exception("Database error")


def update_api_key(api_key_id, data):
    """Updates an API key's information (name and description)."""
    try:
        ApiKeySchema(exclude=['value', 'user_id']).load(data)
        api_key = get_api_key_by_id(api_key_id)
        if not api_key:
            raise ValueError("API key not found")

        # Update name and description if provided in data
        if 'name' in data:
            api_key.name = data['name']
        if 'description' in data:
            api_key.description = data['description']

        db.session.commit()

        get_all_api_keys.cache_clear()
        get_api_key_by_id.cache_clear()

        logger.info(f"Updated API key '{api_key.name}' (ID: {api_key_id})")
        return api_key
    except ValidationError as err:

        logger.error(f"Validation error updating API key: {err.messages}")
        raise ValueError(err.messages)
    except SQLAlchemyError as e:
        db.session.rollback()

        logger.error(f"Database error updating API key: {e}")
        raise Exception("Database error.")


def delete_api_key(api_key_id):
    """Deletes an API key."""
    try:
        api_key = get_api_key_by_id(api_key_id)
        if api_key:
            db.session.delete(api_key)
            db.session.commit()

            logger.info(f"Deleted API key '{api_key.name}' (ID: {api_key_id})")
        return api_key  # Return the deleted API key (or None if not found)
    except SQLAlchemyError as e:

        logger.error(f"Database error: {e}")
        raise Exception("Database error")


# --- OAuth Provider-related functions ---
def create_oauth_provider(data):
    """Creates a new OAuth provider entry."""
    try:
        OAuthProviderSchema().load(data)

        # Encrypt the client secret before storing
        f = Fernet(encryption_key)
        encrypted_secret = f.encrypt(data['client_secret'].encode())

        provider = OAuthProvider(
            platform=data['platform'],
            client_id=data['client_id'],
            client_secret=encrypted_secret,
            enabled=data.get('enabled', False)
        )
        db.session.add(provider)
        db.session.commit()

        logger.info(f"Created OAuth provider '{provider.platform}'")
        return provider
    except ValidationError as err:

        logger.error(f"Validation error creating OAuth provider: {err.messages}")
        raise ValueError(err.messages)
    except IntegrityError as e:
        db.session.rollback()
        raise ValueError(f"OAuth provider with platform '{data['platform']}' already exists.") from e
    except SQLAlchemyError as e:
        db.session.rollback()

        logger.error(f"Database error creating OAuth provider: {e}")
        raise Exception("Database error.")


@cached(cache=TTLCache(maxsize=1024, ttl=300))
def get_all_oauth_providers():
    """Retrieves all OAuth providers."""
    try:
        return OAuthProvider.query.all()
    except SQLAlchemyError as e:

        logger.error(f"Database error getting OAuth providers: {e}")
        raise Exception("Database error.")


@cached(cache=TTLCache(maxsize=1024, ttl=300))
def get_oauth_provider_by_id(provider_id):
    """Retrieves an OAuth provider by ID."""
    try:
        provider = OAuthProvider.query.get(provider_id)
        if not provider:
            raise ValueError("OAuth provider not found.")
        return provider
    except SQLAlchemyError as e:

        logger.error(f"Database error getting OAuth provider by ID: {e}")
        raise Exception("Database error.")


def update_oauth_provider(provider_id, data):
    """Updates an OAuth provider."""
    try:
        OAuthProviderSchema(partial=True).load(data)  # Validate input data
        provider = get_oauth_provider_by_id(provider_id)
        if not provider:
            raise ValueError("OAuth provider not found.")

        for key, value in data.items():
            if key == 'client_secret' and value:  # Encrypt if client secret is updated
                f = Fernet(encryption_key)
                value = f.encrypt(value.encode())
            setattr(provider, key, value)

        db.session.commit()

        get_all_oauth_providers.cache_clear()

        logger.info(f"Updated OAuth provider '{provider.platform}'")
        return provider
    except ValidationError as err:

        logger.error(f"Validation error updating OAuth provider: {err.messages}")
        raise ValueError(err.messages)
    except SQLAlchemyError as e:
        db.session.rollback()

        logger.error(f"Database error updating OAuth provider: {e}")
        raise Exception("Database error.")


def delete_oauth_provider(provider_id):
    """Deletes an OAuth provider."""
    try:
        provider = get_oauth_provider_by_id(provider_id)
        if not provider:
            raise ValueError("OAuth provider not found.")
        db.session.delete(provider)
        db.session.commit()

        get_all_oauth_providers.cache_clear()
        get_oauth_provider_by_id.cache_clear()

        logger.info(f"Deleted OAuth provider '{provider.platform}'")
        return provider
    except SQLAlchemyError as e:

        logger.error(f"Database error deleting OAuth provider: {e}")
        raise Exception("Database error.")
