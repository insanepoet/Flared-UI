from sqlalchemy.exc import SQLAlchemyError
from FlaredUI.Modules.DB.Models import Application
from cachetools import cached, TTLCache
from FlaredUI.Logging import get_logger


logger = get_logger(__name__)


@cached(cache=TTLCache(maxsize=1024, ttl=300))
def get_application_by_id(application_id):
    """Retrieves an application by its ID."""
    try:
        application = Application.query.get(application_id)
        if not application:
            raise ValueError("Application not found")
        return application
    except SQLAlchemyError as e:

        logger.error(f"Database error: {e}")
        raise Exception("Database error")
