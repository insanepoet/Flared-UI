from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from marshmallow import ValidationError
from flask_login import current_user  # Import current_user
from cachetools import cached, TTLCache
from FlaredUI.Modules.DB import db, AppSettingsSchema, AppSettings
from datetime import datetime, timezone
from FlaredUI.Modules.Errors import UnauthorizedError
from FlaredUI.Logging import get_logger


logger = get_logger(__name__)


def create_app_setting(data):
    """Creates a new app setting"""

    try:
        AppSettingsSchema().load(data)

        # Check if the user is authenticated
        if not current_user.is_authenticated:
            raise UnauthorizedError("You must be logged in to create an app setting.")

        app_setting = AppSettings(
            name=data['name'],
            value=data['value'],
            last_modified=datetime.now(timezone.utc),
            modified_by=current_user.id
        )
        db.session.add(app_setting)
        db.session.commit()

        get_all_app_settings.cache_clear()

        logger.info(f"Created app setting '{app_setting.name}' by user {current_user.username}")
        return app_setting
    except ValidationError as err:
        logger.error(f"Validation error creating app setting: {err.messages}")
        raise ValueError(err.messages)
    except IntegrityError:
        db.session.rollback()
        raise ValueError("App setting name already exists.")
    except SQLAlchemyError as e:
        db.session.rollback()
        logger.error(f"Database error creating app setting: {e}")
        raise Exception("Database error.")


@cached(cache=TTLCache(maxsize=1024, ttl=300))
def get_all_app_settings():
    """Retrieves all application settings."""

    try:
        return AppSettings.query.all()
    except SQLAlchemyError as e:
        logger.error(f"Database error: {e}")
        raise Exception("Database error")


@cached(cache=TTLCache(maxsize=1024, ttl=300))
def get_app_setting_by_id(setting_id):
    """Retrieves an application setting by its ID."""

    try:
        app_setting = AppSettings.query.get(setting_id)
        if not app_setting:
            raise ValueError("App setting not found")
        return app_setting
    except SQLAlchemyError as e:
        logger.error(f"Database error: {e}")
        raise Exception("Database error")


@cached(cache=TTLCache(maxsize=1024, ttl=300))
def get_app_setting_by_name(name):
    """Retrieves an application setting by its name."""

    try:
        return AppSettings.query.filter_by(name=name).first()
    except SQLAlchemyError as e:
        logger.error(f"Database error: {e}")
        raise Exception("Database error")


def update_app_setting(setting_id, data):
    try:
        AppSettingsSchema(exclude=['name', 'last_modified']).load(data)

        if not current_user.is_authenticated:
            raise UnauthorizedError("You must be logged in to update an app setting.")

        app_setting = get_app_setting_by_id(setting_id)
        if not app_setting:
            raise ValueError("App setting not found")

        app_setting.value = data['value']
        app_setting.last_modified = datetime.now(timezone.utc)
        app_setting.modified_by = current_user.id

        get_app_setting_by_id.cache_clear()
        get_app_setting_by_name.cache_clear()
        get_all_app_settings.cache_clear()

        db.session.commit()

        logger.info(f"Updated app setting '{app_setting.name}' by user {current_user.username}")
        return app_setting

    except ValidationError as err:
        logger.error(f"Validation error updating app setting: {err.messages}")
        raise ValueError(err.messages)
    except SQLAlchemyError as e:
        db.session.rollback()
        logger.error(f"Database error updating app setting: {e}")
        raise Exception("Database error")


def delete_app_setting(setting_id):
    """Deletes an application setting."""

    try:
        # Check if the user is authenticated
        if not current_user.is_authenticated:
            raise UnauthorizedError("You must be logged in to delete an app setting.")

        app_setting = get_app_setting_by_id(setting_id)
        if app_setting:
            db.session.delete(app_setting)
            db.session.commit()

            get_all_app_settings.cache_clear()
            logger.info(f"Deleted app setting '{app_setting.name}' by user {current_user.username}")
            return app_setting
    except SQLAlchemyError as e:
        logger.error(f"Database error: {e}")
        raise Exception("Database error")
