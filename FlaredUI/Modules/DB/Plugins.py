from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from marshmallow import ValidationError
from cachetools import cached, TTLCache
from flask_login import current_user
from FlaredUI.Modules.DB import (
    db, PluginRepositorySchema, PluginSchema,
    PluginRepository, Plugin,
)
from FlaredUI.Modules.Errors import UnauthorizedError
from FlaredUI.Logging import get_logger


logger = get_logger(__name__)


def create_plugin_repo(data):
    """Creates a new plugin repository entry."""

    try:
        PluginRepositorySchema().load(data)
        repo = PluginRepository(**data)
        db.session.add(repo)
        db.session.commit()
        logger.info(f"Created plugin repository: {repo.name}")
        return repo
    except ValidationError as err:
        logger.error(f"Validation error creating plugin repository: {err.messages}")
        raise ValueError(err.messages)
    except IntegrityError as e:
        db.session.rollback()
        raise ValueError(f"Plugin repository with name '{data['name']}' already exists.") from e
    except SQLAlchemyError as e:
        db.session.rollback()
        logger.error(f"Database error creating plugin repository: {e}")
        raise Exception("Database error.")


@cached(cache=TTLCache(maxsize=1024, ttl=300))
def get_plugin_repos():
    """Retrieves all plugin repositories."""

    try:
        return PluginRepository.query.all()
    except SQLAlchemyError as e:
        logger.error(f"Database error getting plugin repositories: {e}")
        raise Exception("Database error.")


@cached(cache=TTLCache(maxsize=1024, ttl=300))
def get_plugin_repo_by_id(repo_id):
    """Retrieves a plugin repository by its ID."""

    try:
        repo = PluginRepository.query.get(repo_id)
        if not repo:
            raise ValueError("Plugin repository not found.")
        return repo
    except SQLAlchemyError as e:
        logger.error(f"Database error getting plugin repository by ID: {e}")
        raise Exception("Database error.")


def update_plugin_repo(repo_id, data):
    """Updates an existing plugin repository."""

    try:
        PluginRepositorySchema(partial=True).load(data)  # Validate input data
        repo = get_plugin_repo_by_id(repo_id)
        if not repo:
            raise ValueError("Plugin repository not found.")

        for key, value in data.items():
            setattr(repo, key, value)

        db.session.commit()

        get_plugin_repos.cache_clear()
        get_plugin_repo_by_id.cache_clear()
        logger.info(f"Updated plugin repository: {repo.name}")
        return repo
    except ValidationError as err:
        logger.error(f"Validation error updating plugin repository: {err.messages}")
        raise ValueError(err.messages)
    except SQLAlchemyError as e:
        db.session.rollback()
        logger.error(f"Database error updating plugin repository: {e}")
        raise Exception("Database error.")


def delete_plugin_repo(repo_id):
    """Deletes a plugin repository by its ID."""

    try:
        repo = get_plugin_repo_by_id(repo_id)
        if not repo:
            raise ValueError("Plugin repository not found.")

        db.session.delete(repo)
        db.session.commit()

        logger.info(f"Deleted plugin repository: {repo.name}")
        return repo
    except SQLAlchemyError as e:
        logger.error(f"Database error deleting plugin repository: {e}")
        raise Exception("Database error.")


# --- Plugin Functions ---
def create_plugin(data):
    """Creates a new plugin entry."""

    try:
        # Validate input data
        PluginSchema().load(data)

        if not current_user.is_authenticated:
            raise UnauthorizedError("You must be logged in to create a plugin.")

        plugin = Plugin(**data)  # Create the Plugin object
        db.session.add(plugin)  # Add it to the database session
        db.session.commit()  # Commit the changes to the database

        logger.info(f"Created plugin '{plugin.name}' in repository {plugin.repository_id}")
        return plugin
    except ValidationError as err:
        logger.error(f"Validation error creating plugin: {err.messages}")
        raise ValueError(err.messages)
    except IntegrityError as e:
        db.session.rollback()
        raise ValueError(
            f"Plugin with name '{data['name']}' from repository ID {data['repository_id']} already exists.") from e
    except SQLAlchemyError as e:
        db.session.rollback()
        logger.error(f"Database error creating plugin: {e}")
        raise Exception("Database error.")


@cached(cache=TTLCache(maxsize=1024, ttl=300))
def get_plugins():
    """Retrieves all plugins."""

    try:
        return Plugin.query.all()
    except SQLAlchemyError as e:
        logger.error(f"Database error getting plugins: {e}")
        raise Exception("Database error.")


@cached(cache=TTLCache(maxsize=1024, ttl=300))
def get_plugin_by_id(plugin_id):
    """Retrieves a plugin by its ID."""

    try:
        plugin = Plugin.query.get(plugin_id)
        if not plugin:
            raise ValueError("Plugin not found.")
        return plugin
    except SQLAlchemyError as e:
        logger.error(f"Database error getting plugin by ID: {e}")
        raise Exception("Database error.")


def update_plugin(plugin_id, data):
    """Updates an existing plugin entry."""

    try:
        # Validate input data
        PluginSchema(partial=True).load(data)  # Allow partial updates

        # Ensure the user is authenticated
        if not current_user.is_authenticated:
            raise UnauthorizedError("You must be logged in to update a plugin.")

        # Retrieve the plugin
        plugin = get_plugin_by_id(plugin_id)
        if not plugin:
            raise ValueError("Plugin not found.")

        # Update only the provided fields (partial update)
        for key, value in data.items():
            if key != 'id' and key != 'repository_id':  # Exclude unmodifiable fields
                setattr(plugin, key, value)

        db.session.commit()

        get_plugins.cache_clear()
        get_plugin_by_id.cache_clear()

        logger.info(f"Updated plugin '{plugin.name}' (ID: {plugin_id})")
        return plugin
    except ValidationError as err:
        logger.error(f"Validation error updating plugin: {err.messages}")
        raise ValueError(err.messages)
    except SQLAlchemyError as e:
        db.session.rollback()
        logger.error(f"Database error updating plugin: {e}")
        raise Exception("Database error.")
